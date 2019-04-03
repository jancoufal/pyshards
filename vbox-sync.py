#!/bin/env python3.6
#
# dependency: pyftpdlib

import argparse
import configparser
# emitter
import ftplib
import ipaddress
import logging
import os
import pathlib
import shutil
import sys
import tempfile
import time
from collections import OrderedDict
from collections import deque
from enum import Enum, auto

import math
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.filesystems import AbstractedFS
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.log import config_logging as ftpd_config_logging
# receiver
from pyftpdlib.servers import FTPServer


class RunMode(Enum):
	EMITTER = auto(),
	RECEIVER = auto()


def get_default_config(mode, emitter_paths=None, ip_port=9731, home_dir='./temp/', local_path='./sync/'):
	if not isinstance(emitter_paths, OrderedDict):
		raise TypeError('Path must be instance of OrderedDict class')

	config = OrderedDict(
		(configparser.DEFAULTSECT, OrderedDict(
			('mode', RunMode[mode.upper()].name.lower()),
			('user', 'bob'),
			('password', 'bob'),
		)),
		('logging', OrderedDict(
			('level', 'debug'),
			('format', '%(asctime)s - %(levelname)s : %(message)s'),
			('datefmt', '%Y-%m-%d %H:%M:%S'),
		)),
		('emitter', OrderedDict(
			('receiver_ip', '127.0.0.1'),
			('receiver_port', ip_port),
			('sync_section', 'emitter_paths'),
		)),
		('emitter_paths', OrderedDict(
			('path1', 'd:/dl/*JQ.jpg'),
			# ('path2', 'd:/dl/*.zip'),
		)),
		('receiver', OrderedDict(
			('ftp_logging_level', 'warning'),
			('listening_ip', '0.0.0.0'),
			('listening_port', ip_port),
			('home_path', home_dir),
			('local_path', local_path),
		)),
	)

	return config


def deep_walk_files(root):
	"""
	Walks all files in the {root} recursively

	:param root: root path
	:return: generator with file paths relative to root
	"""
	dir_queue = deque([root])

	try:
		base = dir_queue.popleft()
		for r, d, f in os.walk(base, followlinks=False):
			# yield all files (full path)
			yield from map(lambda x: os.path.join(r, x), f)
			# enqueue all child directories
			dir_queue.extend(os.path.join(r, x) for x in d)

	except IndexError:
		'''end of iteration'''


def time_diff_format(seconds):
	"""
	Seconds formatter to human readable format.
	Like "2w 5d 12h 34m 56s 987ms" or "12m 34s 567ms".

	Higher specifiers are not used if not necessary - when duration takes 0 weeks,
	then "0w" is not used in the result and so on.
	So, when duration takes exactly one day, then output string is "1d 0h 0m 0s 0ms".

	When {seconds} is not float or is lower than zero, than output is unpredictable.

	:param seconds: float number
	:return: formatted string
	"""
	# milliseconds & seconds
	millis, secs = math.modf(seconds)

	# rounded >=0.9995 seconds is not 999ms, but 1 extra second
	extra, millis = divmod(round(millis * 1000), 1000)
	secs += extra

	# factors for (week, day, hour, minute, second)
	time_factors = (604800, 86400, 3600, 60, 1)
	time_parts = []

	for tf in time_factors:
		g = int(secs) // tf
		time_parts.append(g)
		secs -= g * tf
	time_parts.append(millis)

	time_fmts = ('%dw ', '%dd ', '%dh ', '%dm ', '%ds ', '%dms')

	time_formatted = ''
	for z in zip(time_parts, time_fmts):
		if z[0] > 0 or len(time_formatted) > 0:
			time_formatted += z[1] % z[0]

	# zero milliseconds
	if len(time_formatted) == 0:
		time_formatted = time_fmts[-1] % 0

	return time_formatted


def binary_size_format(byte_size):
	base_factor = 1024
	size = byte_size
	size_fmt = ('%d %s', '%.1f %s')
	size_hum = ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB')

	i = 0
	fmt = size_fmt[0]
	for i in range(len(size_hum)):
		if size < base_factor:
			break
		size /= base_factor
		fmt = size_fmt[1]

	return fmt % (size, size_hum[i])


def percent(part, total):
	return '%.2f%%' % (0 if total == 0 else 100.0 * part / total)


class Timer(object):
	def __init__(self, start_immediate=False):
		self._start = None
		if start_immediate:
			self.start()

	def start(self, restart=True):
		if restart or self._start is None:
			self._start = time.time()

	def __str__(self):
		return 'unknown' if self._start is None else time_diff_format(time.time() - self._start)


class EventType(Enum):
	OVERALL_START = auto(),
	OVERALL_STOP = auto(),
	EMITTER_LIST_FILE = auto(),
	EMITTER_MATCH_FILE = auto(),
	RECEIVER_ACCEPT_FILE = auto(),
	RECEIVER_CREATE_DIR = auto(),
	RECEIVER_CREATE_FILE = auto(),
	SYNCER_SYNC_FILE = auto(),
	SYNCER_CLEANUP_DIR = auto(),
	SYNCER_CLEANUP_FILE = auto(),


class EventRecord(object):
	def __init__(self, event_type, event_data=None):
		self._type = event_type
		self._data = event_data

	@property
	def type(self):
		return self._type

	@property
	def data(self):
		return self._data

	def __str__(self):
		return '%s: %s' % (str(self._type), str(self._data))


class EventLogger(object):
	def __init__(self):
		self._e = []
		self._t = Timer()

	def __iter__(self):
		return iter(self._e)

	def add(self, event_type, event_data=None):
		self._t.start(False)
		self._e.append(EventRecord(event_type, event_data))

	def add_events(self, event_logger):
		self._t.start(False)
		self._e.extend(event_logger)

	def as_timer(self):
		return self._t

	def __str__(self):
		return 'Event count: %d, Time taken: %s' % (len(self._e), str(self._t))


class Emitter(object):
	"""
	Emitter (client / caster) class.
	"""

	def __init__(self, logger):
		self._l = logger
		self._events = None
		self._send_paths = []
		self._receiver_ip = None
		self._receiver_port = None
		self._login_user = None
		self._login_password = None

	def init(self, config, events):

		self._events = events

		ini_emitter = config['emitter']

		# read dirs & masks to synchronize
		sync_section = ini_emitter['sync_section']
		self._send_paths = [pathlib.Path(config[sync_section][p]) for p in config[sync_section] if p.startswith('path')]

		self._l.info('Paths to be sent:')
		for d in self._send_paths:
			self._l.info('  ' + str(d))

		# emitter target
		self._receiver_ip = ipaddress.ip_address(ini_emitter['receiver_ip'])
		self._receiver_port = ini_emitter.getint('receiver_port')
		self._l.info('Emitter endpoint: ' + str(self._receiver_ip) + ', port: ' + str(self._receiver_port) + '.')

		# user name & password
		self._login_user = ini_emitter['user']
		self._login_password = ini_emitter['password']

		self._l.info('Initialization completed.')

	def _send_files(self, ftp, events):

		for p in self._send_paths:
			self._l.info('Scanning path %s' % p)

			# walk the files
			for f in deep_walk_files(p.parent):
				events.add(EventType.EMITTER_LIST_FILE)

				file_path = pathlib.Path(f)

				if file_path.match(p.name):
					self._l.info(' -> ' + str(file_path))

					with open(file_path, 'rb') as fh:
						self._l.debug('STOR ' + str(file_path.relative_to(p.parent)))
						ftp.storbinary('STOR ' + str(file_path.relative_to(p.parent)), fh)

					events.add(EventType.EMITTER_MATCH_FILE, {
						'path': file_path,
						'size': file_path.stat().st_size,
					})

	def log_statistics(self):
		f_walked = f_sent = f_size = 0
		for e in self._events:
			if e.type == EventType.EMITTER_LIST_FILE:
				f_walked += 1
			elif e.type == EventType.EMITTER_MATCH_FILE:
				f_sent += 1
				f_size += e.data['size']

		self._l.info('Emitter statistics:')
		self._l.info('  Files walked: %d, files sent: %d (%s, size: %s) in %s' % (
			f_walked, f_sent, percent(f_sent, f_walked), binary_size_format(f_size), str(self._events.as_timer())
		))

	def run(self):

		ftp_connect = {
			'host': str(self._receiver_ip),
			'port': self._receiver_port,
		}

		ftp_login = {
			'user': self._login_user,
			'passwd': self._login_password,
		}

		self._l.info('Logging to {host}:{port} as {user}.'.format(**{**ftp_connect, **ftp_login}))
		ftp = ftplib.FTP()

		events = EventLogger()

		try:
			ftp.connect(**ftp_connect)
			self._l.info('Connected to {host}:{port}.'.format(**ftp_connect))

			ftp.login(**ftp_login)
			self._l.info('Logged as {user}.'.format(**ftp_login))

			self._send_files(ftp, events)

			ftp.quit()

		except ConnectionRefusedError as e:
			self._l.error(str(e))

		finally:
			self._l.info('Closing connection.')
			ftp.close()
			self._events.add_events(events)


class ReceiverHandler(FTPHandler):
	"""
	Receiver (server / acceptor) event handler.
	"""

	def __init__(self, conn, server, ioloop=None):
		super().__init__(conn, server, ioloop)
		self._owner = server.owner_instance  # owner is instance of Receiver
		self._l = self._owner._l
		self._events = EventLogger()
		self._l.debug('Event handler created: ' + str(self))
		self._l.debug('  Owner: ' + str(self._owner))

	# Own methods

	def add_events(self, events):
		self._events.add_events(events)

	# FTPHandler overridden methods

	def on_connect(self):
		self._l.debug('Someone connected...')

	def on_disconnect(self):
		self._l.debug('Someone disconnected...')

	def on_login(self, username):
		self._l.info('Hi %s.' % username)

	def on_login_failed(self, username, password):
		self._l.warning('Login failed for %s.' % username)

	def on_logout(self, username):
		self._l.info('Good bye %s.' % username)
		self._owner.add_events(self._events)

	def on_file_sent(self, file):
		self._l.debug(' -> %s' % file)

	def on_file_received(self, file):
		self._l.debug(' <- %s' % file)

	def on_incomplete_file_sent(self, file):
		# os.remove(file)
		self._l.debug(' ! %s' % file)

	def on_incomplete_file_received(self, file):
		# os.remove(file)
		self._l.debug(' !! %s' % file)


class ReceiverAbstractedFS(AbstractedFS):
	"""
	Receiver (server / acceptor) abstracted file system handler.
	It is only used for creating directories (even recursively),
	when emitter is storing files into non-existent paths.
	"""

	def __init__(self, root, cmd_channel):
		self._owner = cmd_channel
		self._l = self._owner._l  # owner is instance of ReceiverHandler
		super().__init__(root, cmd_channel)
		self._l.debug('Abstracted FS created: ' + str(self))
		self._l.debug('  Owner: ' + str(self._owner))

	def open(self, filename, mode):

		events = EventLogger()

		self._l.debug('Incoming filename: ' + str(filename))
		destination_path = pathlib.Path(filename).parent

		# we have to log every created directory, so we can't use os.makedirs :(
		d_create = []
		d_path = destination_path
		while not d_path.exists():
			d_create.append(d_path)
			d_path = d_path.parent

		for d in reversed(d_create):
			self._l.debug('Creating non-existent directory: %s' % str(destination_path))
			os.mkdir(d)
			events.add(EventType.RECEIVER_CREATE_DIR, {'name': d})

		events.add(EventType.RECEIVER_CREATE_FILE, {'name': pathlib.Path(filename)})
		ret = super().open(filename, mode)
		self._owner.add_events(events)  # notify owner with all events
		return ret


class Receiver(object):
	"""
	Receiver (server / acceptor) class.
	"""

	def __init__(self, logger):
		self._l = logger
		self._events = None
		self._ftp_log_level = None
		self._listening_ip = None
		self._listening_port = None
		self._home_path = None
		self._home_path_auto_delete = False
		self._local_path = None
		self._accepted_login = None
		self._accepted_password = None

		self._l.debug('Receiver: ' + str(self))

	def init(self, config, events):

		self._events = events

		ini_receiver = config['receiver']

		# emitter target
		self._listening_ip = ipaddress.ip_address(ini_receiver['listening_ip'])
		self._listening_port = ini_receiver.getint('listening_port')
		self._l.info('Listening on ' + str(self._listening_ip) + ', port ' + str(self._listening_port) + '.')

		# receiver home path
		local_path = ini_receiver.get('home_path')
		if local_path is None:
			self._home_path_auto_delete = True
			self._home_path = pathlib.Path(tempfile.mkdtemp(prefix='vboxsync_'))
			self._l.warning('Receiver home path not set, using temporary dir (%s).' % self._home_path)
			self._events.add(EventType.RECEIVER_CREATE_DIR, {'name': self._home_path})
		else:
			self._home_path_auto_delete = False
			self._home_path = pathlib.Path(local_path).absolute()
			if not self._home_path.exists():
				raise RuntimeError('Receiver home path do not exists (%s).' % self._home_path)
		self._l.info('Home path is "%s".' % self._home_path)

		# receiver local path (where to sync to)
		self._local_path = pathlib.Path(ini_receiver['local_path']).absolute()
		if not self._local_path.exists():
			raise RuntimeError('Receiver local path (where to sync to) do not exists ("%s")!' % self._local_path)
		self._l.info('Local (sync) path is "%s".' % self._local_path)

		# accepted user & password
		self._accepted_login = ini_receiver['user']
		self._accepted_password = ini_receiver['password']

		# ftp daemon log level
		self._ftp_log_level = logging.getLevelName(ini_receiver.get('ftp_logging_level', 'WARNING').upper())

		self._l.info('Initialization completed.')

	def add_events(self, events):

		# receiver handler is not able to get file size, so we will do it
		for e in events:
			if e.type == EventType.RECEIVER_CREATE_FILE:
				e.data['size'] = e.data['name'].stat().st_size

		self.sync_files(events)
		self.clean_up_files(events)
		self._log_new_statistics(events, 'Receiver statistics')
		self._events.add_events(events)

	def _log_new_statistics(self, events, title):
		f_count = f_size = d_count = 0
		for e in events:
			if e.type == EventType.RECEIVER_CREATE_FILE:
				f_count += 1
				f_size += e.data['size']
			elif e.type == EventType.RECEIVER_CREATE_DIR:
				d_count += 1

		self._l.info(title + ':')
		self._l.info('  Received %d files (size: %s) in %d directories in %s' % (
			f_count, binary_size_format(f_size), d_count, str(events.as_timer())
		))

	def log_statistics(self):
		self._log_new_statistics(self._events, 'Overall statistics')

	def sync_files(self, events):

		self._l.info('Starting sync into %s:' % str(self._local_path))

		for e in events:
			if e.type == EventType.RECEIVER_CREATE_FILE:
				f = e.data['name']

				relative_path = pathlib.Path(f).relative_to(self._home_path)
				self._l.info(' -> ' + str(relative_path))

				destination_file = self._local_path.joinpath(relative_path)
				self._l.debug(' d -> ' + str(destination_file))

				destination_path = destination_file.parent
				if not destination_path.exists():
					self._l.debug('Creating non-existent directory: %s' % str(destination_path))
					os.makedirs(destination_path)

				shutil.move(f, destination_file)

	def clean_up_files(self, events):

		def for_events(event_type, on_exists):
			for e in events:
				if e.type == event_type and e.data['name'].exists():
					on_exists(e.data['name'])

		def del_file(f):
			self._l.debug('REMOVE: ' + str(f))
			os.remove(f)

		def del_dir(d):
			self._l.debug('RMTREE: ' + str(d))
			try:
				shutil.rmtree(str(d))
			except OSError as e:
				self._l.warning(str(e))

		# files first, then dirs
		for_events(EventType.RECEIVER_CREATE_FILE, del_file)
		for_events(EventType.RECEIVER_CREATE_DIR, del_dir)

	def run(self):

		ftpd_config_logging(level=self._ftp_log_level)

		self._l.info('Creating dummy authorizer for user "%s" identified by "%s".'
					 % (self._accepted_login, self._accepted_password))
		self._l.info('Home path is "%s"' % self._home_path)
		self._l.info('Local path is "%s"' % self._local_path)

		authorizer = DummyAuthorizer()
		authorizer.add_user(self._accepted_login, self._accepted_password, str(self._home_path), 'elradfmwM')

		ReceiverHandler.authorizer = authorizer
		ReceiverHandler.abstracted_fs = ReceiverAbstractedFS

		self._l.info('Starting server (Ctrl+C to break)...')
		server = FTPServer((str(self._listening_ip), self._listening_port), ReceiverHandler)
		server.owner_instance = self
		server.serve_forever()

		if self._home_path_auto_delete and self._home_path.parent == pathlib.Path(tempfile.gettempdir()):
			self._l.info('Removing home directory "%s", because it was created automatically.', self._home_path)
			shutil.rmtree(self._home_path, ignore_errors=True)


def run(logger, config, mode_override=None):
	try:
		if mode_override is not None:
			mode = mode_override
		else:
			mode = RunMode[config.get(configparser.DEFAULTSECT, 'mode').upper()]

		logger.info('Run mode: %s. (Overridden? %s.)' % (str(mode), 'no' if mode_override is None else 'yes'))

		mode_to_executor = {
			RunMode.EMITTER: Emitter,
			RunMode.RECEIVER: Receiver,
		}

		events = EventLogger()
		events.add(EventType.OVERALL_START, {'mode': mode})

		executor = mode_to_executor[mode](logger)
		executor.init(config, events)
		executor.run()
		executor.log_statistics()

		events.add(EventType.OVERALL_STOP, {'mode': mode})

	except KeyError or RuntimeError as e:
		logger.fatal(str(e))


def main(module_name, argv):
	def arg_parser_run_mode(arg):
		try:
			return None if arg is None else RunMode[arg.upper()]
		except KeyError:
			raise argparse.ArgumentTypeError('Specified run mode (\'%s\') not recognized.' % arg)

	default_ini_file = pathlib.Path(module_name).with_suffix('.ini')

	# args
	parser = argparse.ArgumentParser(prefix_chars='-')
	parser.add_argument('-config', type=pathlib.Path, default=default_ini_file, help='Config file path.')
	parser.add_argument('-mode', type=arg_parser_run_mode,
						help='Script run mode (overrides config): EMITTER or RECEIVER.')
	args = parser.parse_args(argv)

	# ini file
	config = configparser.ConfigParser()
	config.read(args.config)

	# logger
	logging.basicConfig(**{
		'level': logging.getLevelName(config['logging'].get('level', 'INFO').upper()),
		'format': config['logging'].get('format', '%(asctime)s - %(levelname)s : %(message)s', raw=True),
		'datefmt': config['logging'].get('datefmt', '%Y-%m-%d %H:%M:%S', raw=True),
	})

	# run
	logger = logging.getLogger(module_name)
	run(logger, config, args.mode)


if __name__ == '__main__':
	main(sys.argv[0], sys.argv[1:])
