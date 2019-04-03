#!/bin/env python3

import concurrent.futures
import os
import pathlib
import queue
import subprocess
import threading
import time
from enum import Enum, auto

import wx
import wx.dataview


class WorkQueueMessage(object):
	"""
	Typical working queue item message
	"""

	def __init__(self, work_id, message_type, data=None):
		self._work_id = work_id
		self._message_type = message_type
		self._data = data

	def __str__(self):
		return '%s (id: %d): %s' % (str(self._message_type), self._work_id, str(self._data))

	@property
	def work_id(self):
		return self._work_id

	@property
	def type(self):
		return self._message_type

	@property
	def data(self):
		return self._data


class WorkCounter(object):
	def __init__(self):
		self._counter = 0
		self._counter_reentrant_lock = threading.RLock()

	def get_and_increment(self):
		with self._counter_reentrant_lock:
			c = self._counter
			self._counter += 1
			return c


class AsyncFileWalker(object):
	"""
	Async file walker
	"""

	class Events(object):
		def on_work_enqueue(self, work_message):
			pass

		def on_work_finished(self, work_message):
			pass

		def on_all_work_done(self):
			pass

		def on_stopped(self):
			pass

	class _MessageTypes(Enum):
		NEW_DIR_ENQUEUED = auto(),
		STOP_REQUEST = auto(),

	def __init__(self, event_handler):
		self._events = event_handler
		self._work_counter = WorkCounter()
		self._active_works = set()
		self._wqueue = queue.Queue()
		self._wqueue_event = threading.Event()
		self._wthread = threading.Thread(target=self._thread_loop)
		self._wthread.start()

	def add_directory(self, directory):
		self._enqueue_work(AsyncFileWalker._MessageTypes.NEW_DIR_ENQUEUED, directory)

	def stop_request(self):
		# todo: stop request should be prioritized
		# todo: stop request should also kill all executors
		self._enqueue_work(AsyncFileWalker._MessageTypes.STOP_REQUEST, None)

	def _enqueue_work(self, message_type, data=None):
		work_message = WorkQueueMessage(self._work_counter.get_and_increment(), message_type, data)
		self._events.on_work_enqueue(work_message)
		self._active_works.add(work_message.work_id)
		self._wqueue.put(work_message)
		self._wqueue_event.set()

	def wait_till_stopped(self, timeout=None):
		self._wthread.join(timeout=timeout)

	def _thread_loop(self):
		while True:
			self._wqueue_event.wait()
			m = self._wqueue.get()

			if m.type == AsyncFileWalker._MessageTypes.NEW_DIR_ENQUEUED:
				for r, d, f in os.walk(str(m.data), followlinks=False):
					for file_name in map(lambda x: os.path.join(r, x), f):
						self._events.on_file(file_name)

			if m.type == AsyncFileWalker._MessageTypes.STOP_REQUEST:
				self._events.on_stopped()
				break
			else:
				self._events.on_work_finished(m)
				self._active_works.remove(m.work_id)

			if len(self._active_works) == 0:
				self._events.on_all_work_done()


class JavaClassDescriptor(object):
	"""
	Single Java class descriptor
	"""

	def __init__(self, class_file):
		self._file = class_file
		self._name = pathlib.Path(class_file).name

	@property
	def file(self):
		return self._file

	@property
	def name(self):
		return self._name


class JavaJarDescriptor(object):
	"""
	Single Java JAR container descriptor
	"""

	def __init__(self, jar_file, classes=None):
		self._file = jar_file
		self._classes = classes if classes is not None else list()

	def __str__(self):
		return '%s: %d classes' % (self._file, len(self._classes))

	@classmethod
	def load_from_file(cls, jar_file):
		instance = cls(jar_file)

		jar_opener = JarOpener(jar_file)
		jar_opener.extract()

		if jar_opener.errors is not None:
			raise RuntimeError('Failed when parsing file \'%s\'.' % jar_file, jar_file, jar_opener.errors)

		for c in jar_opener.class_files:
			instance.add_class(JavaClassDescriptor(c))

		return instance

	def add_class(self, class_descriptor):
		self._classes.append(class_descriptor)

	@property
	def file(self):
		return self._file

	@property
	def classes(self):
		return self._classes


class JarOpener(object):
	_JAR_COMMAND = ['c:/Program Files/Java/jdk1.8.0_144/bin/jar.exe', 'tf']
	_COMMAND_OUTPUT_ENCODING = 'utf-8'

	def __init__(self, jar_file):
		self._jar_file = jar_file
		self._errors = None
		self._class_files = list()

	def extract(self):
		cp = subprocess.run(
			JarOpener._JAR_COMMAND + [str(self._jar_file)],
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE
		)

		self._extract_class_files(cp.stdout)
		self._extract_errors(cp.stderr)

	def _extract_class_files(self, cmd_stdout):
		if cmd_stdout is not None and len(cmd_stdout) > 0:
			raw_lines = cmd_stdout.decode(JarOpener._COMMAND_OUTPUT_ENCODING).split(os.linesep)
			self._class_files = list(filter(lambda x: x.endswith('.class'), [l.strip() for l in raw_lines]))

	def _extract_errors(self, cmd_stderr):
		if cmd_stderr is not None and len(cmd_stderr) > 0:
			print(cmd_stderr)
			self._errors = cmd_stderr.decode(JarOpener._COMMAND_OUTPUT_ENCODING)

	@property
	def class_files(self):
		return self._class_files

	@property
	def errors(self):
		return self._errors


class AsyncJarOpener(object):
	"""
	Asynchronous Java JAR container opener.
	Adding new JAR to open is nonblocking.
	"""

	class Events(object):
		def on_new_jar(self, jar_file):
			pass

		def on_jar_extracted(self, jar_descriptor):
			pass

		def on_jar_extraction_failure(self, jar_file, exception):
			pass

		def on_empty_queue(self):
			pass

		def on_stop(self):
			pass

	_MAX_CONCURRENT_EXECUTORS = 5

	class _MessageTypes(Enum):
		NEW_JAR_ENQUEUED = auto(),
		STOP_REQUEST = auto(),

	def __init__(self, event_handler):
		self._events = event_handler
		self._wqueue = queue.Queue()
		self._wqueue_event = threading.Event()
		self._executors_pool = concurrent.futures.ThreadPoolExecutor(
			max_workers=AsyncJarOpener._MAX_CONCURRENT_EXECUTORS,
			# thread_name_prefix=AsyncJarOpener.__class__.__name__
		)
		self._wthread = threading.Thread(target=self._thread_loop)
		self._wthread.start()

	def enqueue_jar_file(self, jar_file):
		self._wqueue.put(WorkQueueMessage(AsyncJarOpener._MessageTypes.NEW_JAR_ENQUEUED, jar_file))
		self._wqueue_event.set()

	def stop_request(self):
		# todo: stop request should be prioritized
		# todo: stop request should also kill all executors
		self._wqueue.put(WorkQueueMessage(AsyncJarOpener._MessageTypes.STOP_REQUEST, None))
		self._wqueue_event.set()

	def wait_till_stopped(self, timeout=None):
		self._wthread.join(timeout=timeout)

	def _acquire_jar_opener_executor(self, jar_file):
		def _generate_executor_callback():
			def _cb():
				try:
					self._events.on_jar_extracted(JavaJarDescriptor.load_from_file(jar_file))
				except Exception as e:
					self._events.on_jar_extraction_failure(jar_file, e)

			return _cb

		return self._executors_pool.submit(_generate_executor_callback())

	def _thread_loop(self):
		while True:
			self._wqueue_event.wait()
			m = self._wqueue.get()

			if m.type == AsyncJarOpener._MessageTypes.NEW_JAR_ENQUEUED:
				self._acquire_jar_opener_executor(m.data)

			if self._wqueue.empty():
				self._events.on_empty_queue()

			if m.type == AsyncJarOpener._MessageTypes.STOP_REQUEST:
				self._events.on_stop()
				break


class JarDispatcher(object):
	"""
	Async JAR extractor from directories.
	"""

	class Events(object):
		def on_new_scan(self, directory):
			pass

		def on_jar_file(self, java_jar_descriptor):
			pass

		def on_jar_file_error(self, jar_file, exception):
			pass

		def on_class_file(self, java_class_descriptor):
			pass

		def on_empty_queue(self):
			pass

		def on_work_done(self):
			pass

		def on_stop(self):
			pass

	class _AsyncFileWalkerEventsProxy(AsyncFileWalker.Events):

		def __init__(self, owner_dispatcher):
			self._owner = owner_dispatcher

		def on_file(self, file_name):
			# print('JarDispatcher._AsyncFileWalkerEventsProxy.on_file(file_name => %s)' % str(file_name))
			f = pathlib.Path(file_name)
			if f.match('*.jar'):
				self._owner._enqueue_message(JarDispatcher._MessageTypes.NEW_JAR_FILE, file_name)
			elif f.match('*.class'):
				self._owner._enqueue_message(JarDispatcher._MessageTypes.NEW_CLASS_FILE, file_name)

		def on_empty_queue(self):
			# print('JarDispatcher._AsyncFileWalkerEventsProxy.on_empty_queue()')
			pass

		def on_stop(self):
			# print('JarDispatcher._AsyncFileWalkerEventsProxy.on_stop()')
			pass

	class _AsyncJarOpenerEventsProxy(AsyncJarOpener.Events):
		def __init__(self, owner_dispatcher):
			self._owner = owner_dispatcher

		def on_new_jar(self, jar_file):
			# print('JarDispatcher._AsyncJarOpenerEventsProxy.on_new_jar(jar_file => %s)' % str(jar_file))
			pass

		def on_jar_extracted(self, jar_descriptor):
			print('JarDispatcher._AsyncJarOpenerEventsProxy.on_jar_extracted(jar_descriptor => %s)' % (
				str(jar_descriptor)))
			self._owner._enqueue_message(JarDispatcher._MessageTypes.JAR_EXTRACTED, jar_descriptor)

		def on_jar_extraction_failure(self, jar_file, exception):
			# print('JarDispatcher._AsyncJarOpenerEventsProxy.on_jar_extraction_failure(jar_file => %s, exception => %s)' % (str(jar_file), str(exception)))
			self._owner._enqueue_message(JarDispatcher._MessageTypes.JAR_EXTRACT_ERROR, (jar_file, exception))

		def on_empty_queue(self):
			# print('JarDispatcher._AsyncJarOpenerEventsProxy.on_empty_queue()')
			pass

		def on_stop(self):
			# print('JarDispatcher._AsyncJarOpenerEventsProxy.on_stop()')
			pass

	class _MessageTypes(Enum):
		NEW_DIR_ENQUEUED = auto(),
		NEW_JAR_FILE = auto(),
		NEW_CLASS_FILE = auto(),
		JAR_EXTRACTED = auto(),
		JAR_EXTRACT_ERROR = auto(),
		STOP_REQUEST = auto(),

	def __init__(self, event_handler):
		self._fwalker = AsyncFileWalker(JarDispatcher._AsyncFileWalkerEventsProxy(self))
		self._jopener = AsyncJarOpener(JarDispatcher._AsyncJarOpenerEventsProxy(self))
		self._events = event_handler
		self._wqueue = queue.Queue()
		self._wqueue_event = threading.Event()
		self._wthread = threading.Thread(target=self._thread_loop)
		self._wthread.start()

	def scan_directory(self, directory):
		self._wqueue.put(WorkQueueMessage(JarDispatcher._MessageTypes.NEW_DIR_ENQUEUED, directory))
		self._wqueue_event.set()

	def stop_request(self):
		# todo: stop request should be prioritized
		# todo: stop request should also kill all executors
		self._wqueue.put(WorkQueueMessage(JarDispatcher._MessageTypes.STOP_REQUEST, None))
		self._wqueue_event.set()

	def wait_till_stopped(self, timeout=None):
		self._jopener.wait_till_stopped(timeout=timeout)
		self._fwalker.wait_till_stopped(timeout=timeout)
		self._wthread.join(timeout=timeout)

	def _enqueue_message(self, message_type, message_data):
		self._wqueue.put(WorkQueueMessage(message_type, message_data))
		self._wqueue_event.set()

	def _thread_loop(self):
		while True:
			self._wqueue_event.wait()
			m = self._wqueue.get()

			if m.type == JarDispatcher._MessageTypes.NEW_DIR_ENQUEUED:
				self._fwalker.add_directory(m.data)

			elif m.type == JarDispatcher._MessageTypes.NEW_JAR_FILE:
				self._jopener.enqueue_jar_file(m.data)

			elif m.type == JarDispatcher._MessageTypes.NEW_CLASS_FILE:
				self._events.on_class_file(JavaClassDescriptor(m.data))

			elif m.type == JarDispatcher._MessageTypes.JAR_EXTRACTED:
				self._events.on_jar_file(m.data)

			elif m.type == JarDispatcher._MessageTypes.JAR_EXTRACT_ERROR:
				self._events.on_jar_file_error(*m.data)

			if self._wqueue.empty():
				self._events.on_empty_queue()

			if m.type == JarDispatcher._MessageTypes.STOP_REQUEST:
				self._events.on_stop()
				self._jopener.stop_request()
				self._fwalker.stop_request()
				break


class JarExplorerDataModel(wx.dataview.PyDataViewModel):
	class JarFileNodeData(object):
		def __init__(self, jar_descriptor):
			self._jar = jar_descriptor

		@property
		def jar(self):
			return self._jar

	class JarClassFileNodeData(JarFileNodeData):
		def __init__(self, jar_descriptor, class_index):
			super().__init__(jar_descriptor)
			self._class_index = class_index

		@property
		def java_class(self):
			return self._jar.classes[self._class_index]

	class JarFileErrorNodeData(object):
		def __init__(self, jar_file, exception):
			self._jar_file = jar_file
			self._exception = exception

		@property
		def jar_file(self):
			return self.jar_file

		@property
		def exception(self):
			return self._exception

	class StandAloneClassesRootNodeData(object):
		def __init__(self, node_name):
			self._name = node_name

		@property
		def name(self):
			return self._name

	class StandAloneClassNodeData(object):
		def __init__(self, class_descriptor):
			self._class = class_descriptor

		@property
		def java_class(self):
			return self._class

	def __init__(self):
		super().__init__()
		self._jd = None
		self._data = dict()
		self._classes_data = None
		self._classes_node = None
		self._data_lock = threading.Lock()

	def initialize(self, jar_dispatcher):
		self._jd = jar_dispatcher

	def jde_on_jar_file(self, java_jar_descriptor):
		with self._data_lock:
			jar_node = self.ObjectToItem(JarExplorerDataModel.JarFileNodeData(java_jar_descriptor))
			self._data.update({jar_node: list()})
			self.ItemAdded(wx.dataview.NullDataViewItem, jar_node)

			for index, cls in enumerate(java_jar_descriptor.classes):
				c_node = self.ObjectToItem(JarExplorerDataModel.JarClassFileNodeData(java_jar_descriptor, index))
				self._data[jar_node].append(c_node)
				self.ItemAdded(jar_node, c_node)

	def jde_on_jar_file_error(self, jar_file, exception):
		with self._data_lock:
			jar_node = self.ObjectToItem(JarExplorerDataModel.JarFileNodeData(jar_file))
			self._data.update({jar_node: list()})
			self.ItemAdded(wx.dataview.NullDataViewItem, jar_node)

			err_node = self.ObjectToItem(JarExplorerDataModel.JarFileErrorNodeData(jar_file, exception))
			self._data[jar_node].append(err_node)
			self.ItemAdded(jar_node, err_node)

	def jde_on_class_file(self, java_class_descriptor):
		with self._data_lock:
			if self._classes_node is None:
				self._classes_node = self.ObjectToItem(
					JarExplorerDataModel.StandAloneClassesRootNodeData('Stand alone classes'))
				self._data.update({self._classes_node: list()})
				self.ItemAdded(wx.dataview.NullDataViewItem, self._classes_node)

			cls_node = self.ObjectToItem(JarExplorerDataModel.StandAloneClassNodeData(java_class_descriptor))
			self._data[self._classes_node].append(cls_node)
			self.ItemAdded(self._classes_node, cls_node)

	def IsContainer(self, item):
		# The hidden root is a container
		if not item:
			return True

		return item in self._data.keys()

	def GetParent(self, item):
		# DataViewItem
		if not item:
			return wx.dataview.NullDataViewItem

		for node in self._data.keys():
			if item in self._data[node]:
				return node

		return wx.dataview.NullDataViewItem

	def GetChildren(self, item, children):
		# unsigned int
		try:
			nodes = self._data.keys() if not item else self._data[item]

			for node in nodes:
				children.append(node)
			return len(nodes)

		except KeyError as e:
			print('Exception: %s' % str(e))
			return 0

	def GetColumnCount(self):
		# unsigned int
		return 2

	def GetColumnType(self, col):
		# string
		# all columns are string
		return 'string'

	def GetValue(self, item, col):
		# variant
		data = self.ItemToObject(item)

		mapper = {0: str(data), 1: ''}

		if type(data) == JarExplorerDataModel.JarFileNodeData:
			mapper.update({
				0: '%s (count: %d)' % (data.jar.file, len(self._data[item])),
				1: '',
			})
		elif type(data) == JarExplorerDataModel.JarClassFileNodeData:
			mapper.update({
				0: data.java_class.file,
				1: data.java_class.name,
			})
		elif type(data) == JarExplorerDataModel.JarFileErrorNodeData:
			mapper.update({
				0: str(data.exception),
				1: 'Error!'
			})
		elif type(data) == JarExplorerDataModel.StandAloneClassesRootNodeData:
			mapper.update({
				0: '%s (count: %d)' % (data.name, len(self._data[item])),
				1: '',
			})
		elif type(data) == JarExplorerDataModel.StandAloneClassNodeData:
			mapper.update({
				0: data.java_class.file,
				1: data.java_class.name,
			})
		else:
			raise TypeError('Unknown node type! item => %s, col => %d' % (str(item), col))

		return mapper[col]

	def GetAttr(self, item, col, attr):
		if item in self._data.keys():
			attr.SetColour('blue')
			attr.SetBold(True)
			return True
		return False


class JarExplorerGui(wx.Frame):
	def __init__(self):
		super(JarExplorerGui, self).__init__(None, wx.ID_ANY, title='Java Class Explorer', size=(800, 600))

		self._jd = None
		self._dc = None
		self._wx_scan_path = None
		self._create_gui()

	def initialize(self, jar_dispatcher, data_model):
		self._jd = jar_dispatcher
		self._dc.AssociateModel(data_model)
		data_model.DecRef()

	def _create_gui(self):
		self._panel = wx.Panel(self, wx.ID_ANY)

		tool_sizer = self._create_toolbar_sizer(self._panel)
		self._dc = self._create_data_ctrl(self._panel)

		frame_sizer = wx.BoxSizer(wx.VERTICAL)
		frame_sizer.Add(tool_sizer, 0, wx.LEFT | wx.TOP | wx.RIGHT)
		frame_sizer.Add(self._dc, 1, wx.ALL | wx.EXPAND)

		self._panel.SetSizer(frame_sizer)

		self._create_status_bar()

	def _create_toolbar_sizer(self, panel):
		inputLabel = wx.StaticText(panel, wx.ID_ANY, ' Scan path: ')
		inputPath = wx.TextCtrl(panel, wx.ID_ANY, 'd:/tmp/jar-test/')
		buttonListDir = wx.Button(panel, wx.ID_ANY, '...')
		self.Bind(wx.EVT_BUTTON, self.on_list_dir, buttonListDir)
		buttonScan = wx.Button(panel, wx.ID_ANY, 'Scan!')
		self.Bind(wx.EVT_BUTTON, self.on_new_scan, buttonScan)
		filterLabel = wx.StaticText(panel, wx.ID_ANY, ' Find: ')
		filterText = wx.TextCtrl(panel, wx.ID_ANY, '')

		tool_sizer = wx.BoxSizer(wx.HORIZONTAL)
		tool_sizer.Add(inputLabel, 0, wx.ALIGN_CENTRE_VERTICAL | wx.LEFT | wx.TOP, 5)
		tool_sizer.Add(inputPath, 0, wx.LEFT | wx.TOP | wx.EXPAND, 5)
		tool_sizer.Add(buttonListDir, 0, wx.LEFT | wx.TOP, 5)
		tool_sizer.Add(wx.StaticLine(panel), 0, wx.ALL | wx.EXPAND, 5)
		tool_sizer.Add(buttonScan, 0, wx.LEFT | wx.TOP, 5)
		tool_sizer.Add(wx.StaticLine(panel), 0, wx.ALL | wx.EXPAND, 5)
		tool_sizer.Add(filterLabel, 0, wx.ALIGN_CENTRE_VERTICAL | wx.LEFT | wx.TOP, 5)
		tool_sizer.Add(filterText, 0, wx.LEFT | wx.TOP | wx.EXPAND, 5)

		self._wx_scan_path = inputPath

		return tool_sizer

	def _create_data_ctrl(self, panel):
		dvc = wx.dataview.DataViewCtrl(
			panel,
			style=wx.BORDER_THEME | wx.dataview.DV_ROW_LINES | wx.dataview.DV_VERT_RULES | wx.dataview.DV_MULTIPLE
		)

		tr = wx.dataview.DataViewTextRenderer()

		dvc.AppendColumn(wx.dataview.DataViewColumn('Jar / Class file', tr, 0, width=500))
		# dvc.AppendTextColumn('Class file', 1, width=300, mode=wx.dataview.DATAVIEW_CELL_ACTIVATABLE)
		dvc.AppendTextColumn('Class name', 1, width=200, mode=wx.dataview.DATAVIEW_CELL_ACTIVATABLE)

		for c in dvc.Columns:
			c.Sortable = True
			c.Reordeable = True

		return dvc

	def _create_status_bar(self):
		self.CreateStatusBar()
		self.SetStatusText('Welcome to Java Class Explorer!')

	def _update_status_text(self):
		# self.SetStatusText('List item count: %d' % (self._dc.GetItemCount()))
		pass

	def jde_on_new_scan(self, directory):
		pass

	def jde_on_empty_queue(self):
		# print('JarDispatcher.Events.on_empty_queue()')
		self._update_status_text()

	def jde_on_work_done(self):
		# print('JarDispatcher.Events.on_work_done()')
		self._update_status_text()

	def jde_on_stop(self):
		# print('JarDispatcher.Events.on_stop()')
		pass

	def on_list_dir(self, event):
		print('JavaClassExplorerFrame::on_list_dir()')
		self._dc.Refresh()
		pass

	def on_new_scan(self, event):
		# self._dc.DeleteAllItems()
		print('JavaClassExplorerFrame::on_new_scan(dir => %s)' % self._wx_scan_path.GetLineText(0))
		self._jd.scan_directory(self._wx_scan_path.GetLineText(0))


def test_file_walker():
	class AFWE(AsyncFileWalker.Events):
		def on_work_enqueue(self, work_message):
			print('AsyncFileWalker.Events.on_work_enqueue(work_message => %s)' % str(work_message))

		def on_work_finished(self, work_message):
			print('AsyncFileWalker.Events.on_work_finished(work_message => %s)' % str(work_message))

		def on_all_work_done(self):
			print('AsyncFileWalker.Events.on_all_work_done()')

		def on_stopped(self):
			print('AsyncFileWalker.Events.on_stopped()')

	afw = AsyncFileWalker(AFWE())
	afw.add_directory('c:/webdev/NetLedger/.gradle')
	afw.stop_request()
	afw.wait_till_stopped()


def test_jar_opener():
	class AJOE(AsyncJarOpener.Events):
		def on_new_jar(self, jar_file):
			print('AsyncJarOpener.Events.on_new_jar(jar_file => %s)' % str(jar_file))

		def on_jar_extraction_failure(self, jar_file, exception):
			print('AsyncJarOpener.Events.on_jar_extraction_failure(jar_file => %s, exception => %s)' % (
			str(jar_file), str(exception)))

		def on_jar_extracted(self, jar_descriptor):
			print('AsyncJarOpener.Events.on_jar_extracted(jar_descriptor => %s)' % str(jar_descriptor))

		def on_empty_queue(self):
			print('AsyncJarOpener.Events.on_empty_queue()')

		def on_stop(self):
			print('AsyncJarOpener.Events.on_stop()')

	ajoe = AsyncJarOpener(AJOE())
	ajoe.enqueue_jar_file('c:/webdev/NetLedger/_dist/cassandra/ns-ldap-auth.jar')
	ajoe.stop_request()
	ajoe.wait_till_stopped()


def test_jar_dispatcher():
	class JDE(JarDispatcher.Events):
		def on_new_scan(self, directory):
			print('JarDispatcher.Events.(directory => %s)' % str(directory))

		def on_jar_file(self, java_jar_descriptor):
			print('JarDispatcher.Events.(java_jar_descriptor => %s)' % str(java_jar_descriptor))

		def on_jar_file_error(self, jar_file, exception):
			print('JarDispatcher.Events.(jar_file => %s, exception => %s)' % (str(jar_file), str(exception)))

		def on_class_file(self, java_class_descriptor):
			print('JarDispatcher.Events.(java_class_descriptor => %s)' % str(java_class_descriptor))

		def on_empty_queue(self):
			print('JarDispatcher.Events.on_empty_queue()')

		def on_work_done(self):
			print('JarDispatcher.Events.on_work_done()')

		def on_stop(self):
			print('JarDispatcher.Events.on_stop()')

	jde = JarDispatcher(JDE())
	jde.scan_directory('d:/tmp/jar-test/')

	time.sleep(2)

	jde.stop_request()
	jde.wait_till_stopped()


def test_wx_gui():
	class JarEventsDistibutior(JarDispatcher.Events):
		def __init__(self, wx_frame, data_model):
			self._wx_frame = wx_frame
			self._data_model = data_model

		def on_new_scan(self, directory):
			self._wx_frame.jde_on_new_scan(directory)

		def on_jar_file(self, java_jar_descriptor):
			self._data_model.jde_on_jar_file(java_jar_descriptor)

		def on_jar_file_error(self, jar_file, exception):
			self._data_model.jde_on_jar_file_error(jar_file, exception)

		def on_class_file(self, java_class_descriptor):
			self._data_model.jde_on_class_file(java_class_descriptor)

		def on_empty_queue(self):
			self._wx_frame.jde_on_empty_queue()

		def on_work_done(self):
			self._wx_frame.jde_on_work_done()

		def on_stop(self):
			self._wx_frame.jde_on_stop()

	wx_app = wx.App()
	wx_dmv = JarExplorerDataModel()
	wx_frm = JarExplorerGui()
	event_proxy = JarEventsDistibutior(wx_frm, wx_dmv)
	jde = JarDispatcher(event_proxy)
	wx_frm.initialize(jde, wx_dmv)

	wx_frm.Show()

	wx_app.MainLoop()
	jde.stop_request()
	jde.wait_till_stopped()


def main():
	test_file_walker()


# test_jar_opener()
# test_jar_dispatcher()
# test_wx_gui()


if __name__ == '__main__':
	main()
