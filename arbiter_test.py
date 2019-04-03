#!/bin/env python3

import os
import subprocess
import threading
import pathlib
import queue		# a synchronized queue class
import time
import concurrent.futures
from enum import Enum, IntFlag, auto
from collections import deque
import wx
import wx.dataview


class WorkQueueMessage(object):
	"""
	Dispatcher message and its data
	"""
	def __init__(self, message_type, data=None):
		self._type = message_type
		self._data = data

	def __str__(self):
		return '%s: %s' % (str(self._type), str(self._data))

	@property
	def type(self):
		return self._type

	@property
	def data(self):
		return self._data


class DispatcherEventReturnCode(Enum):
	ITEM_OK = auto(),
	DISCARD_ITEM = auto(),


class DispatcherEvents(object):
	def on_producer_new_work(self, dispatcher, message_data):
		print('DispatcherEvents::on_new_producer_work(dispatcher => %x, message_data => %s)' % (id(dispatcher), str(message_data)))
		return DispatcherEventReturnCode.ITEM_OK

	def on_extractor_work_done(self, dispatcher, message_data):
		print('DispatcherEvents::on_extractor_work_done(dispatcher => %x, message_data => %s)' % (id(dispatcher), str(message_data)))
		return DispatcherEventReturnCode.ITEM_OK

	def on_stop(self, dispatcher, message_data):
		print('DispatcherEvents::on_stop(dispatcher => %x, message_data => %s)' % (id(dispatcher), str(message_data)))
		return DispatcherEventReturnCode.ITEM_OK


class JarOpenerEvents(object):
	def on_new_jar_arrived(self, jar_opener, message_data):
		pass

	def on_jar_opened(self, jar_opener, message_data):
		pass

	def on_stop(self, jar_opener, message_data):
		pass


class Dispatcher(object):
	"""
	Dispatcher itself
	"""

	class MessageType(Enum):
		"""
		Dispatcher message types
		"""
		PRODUCER_NEW_WORK = auto(),
		EXTRACTOR_WORK_DONE = auto(),
		STOP_DISPATCHER = auto(),

	class JarOpenerEventsProxy(JarOpenerEvents):
		def __init__(self, owner):
			self._owner = owner

		def on_new_jar_arrived(self, jar_opener, message_data):
			print('JarOpenerEventsProxy::on_new_jar_arrived: ' + str(message_data))

		def on_jar_opened(self, jar_opener, message_data):
			print('JarOpenerEventsProxy::on_jar_opened: ' + str(message_data))
			self._owner.add_message(Dispatcher.MessageType.EXTRACTOR_WORK_DONE, message_data=message_data)

		def on_stop(self, jar_opener, message_data):
			print('JarOpenerEventsProxy::on_stop: ' + str(message_data))

	def __init__(self, event_handler):
		self._jar_opener = JarOpener(Dispatcher.JarOpenerEventsProxy(self))
		self._wqueue = queue.Queue()
		self._wqueue_event = threading.Event()
		self._event_handler = event_handler
		self._wthread = threading.Thread(target=Dispatcher._run, args=(self, self._wqueue, self._wqueue_event))
		self._wthread.start()

	def add_producer_new_message(self, message_data):
		self.add_message(Dispatcher.MessageType.PRODUCER_NEW_WORK, message_data)

	def add_message(self, message_type, message_data=None):
		self._wqueue.put(WorkQueueMessage(message_type, message_data))
		self._wqueue_event.set()

	def request_stop(self):
		self._jar_opener.request_stop()
		self._wqueue.put(WorkQueueMessage(Dispatcher.MessageType.STOP_DISPATCHER))
		self._wqueue_event.set()

	def wait_till_stopped(self, timeout=None):
		self._jar_opener.wait_till_stopped(timeout=timeout)
		self._wthread.join(timeout=timeout)

	def _handle_message_event(self, message):
		if self._event_handler is not None:
			triggers = {
				Dispatcher.MessageType.PRODUCER_NEW_WORK: self._event_handler.on_producer_new_work,
				Dispatcher.MessageType.EXTRACTOR_WORK_DONE: self._event_handler.on_extractor_work_done,
				Dispatcher.MessageType.STOP_DISPATCHER: self._event_handler.on_stop,
			}

			trigger = triggers[message.type]

			return trigger(self, message.data)

	@staticmethod
	def _run(owner, message_queue, message_event):
		while True:
			message_event.wait()
			m = message_queue.get()

			# todo: event may be able to return some error (or behavioral) code
			owner._handle_message_event(m)

			if m.type == Dispatcher.MessageType.PRODUCER_NEW_WORK:
				owner._jar_opener.add_jar_to_extract(m.data)

			if m.type == Dispatcher.MessageType.STOP_DISPATCHER:
				break


class JarContent(object):

	class ClassRecord(object):
		def __init__(self, class_file):
			self._file = class_file
			self._name = pathlib.Path(class_file).name

		@property
		def file(self):
			return self._file

		@property
		def name(self):
			return self._name

	def __init__(self, filename, classes, errors):
		self._file = pathlib.Path(filename)
		self._classes = [JarContent.ClassRecord(c) for c in classes]
		self._errors = errors

	def __str__(self):
		return '%s: %d classes (errors: %s)' % (self._file.name, len(self._classes), str(self._errors))

	@property
	def file(self):
		return self._file

	@property
	def classes(self):
		return self._classes

	@property
	def errors(self):
		return self._errors


class JarOpener(object):
	"""
	Threaded JAR file extractor.
	"""
	jar_command = ['c:/Program Files/Java/jdk1.8.0_144/bin/jar.exe', 'tf']
	out_encoding = 'utf-8'
	max_concurrent_executors = 5

	class MessageTypes(Enum):
		"""
		JAR opener message types
		"""
		NEW_JAR_ARRIVED = auto(),
		JAR_OPENED = auto(),
		STOP_JAR_OPENER = auto(),

	def __init__(self, event_handler):
		self._wqueue = queue.Queue()
		self._wqueue_event = threading.Event()
		self._event_handler = event_handler
		self._executors_pool = concurrent.futures.ThreadPoolExecutor(max_workers=JarOpener.max_concurrent_executors, thread_name_prefix='jar_opener')
		self._wthread = threading.Thread(target=JarOpener._run, args=(self, self._wqueue, self._wqueue_event))
		self._wthread.start()

	def add_jar_to_extract(self, jar_file):
		self._wqueue.put(WorkQueueMessage(JarOpener.MessageTypes.NEW_JAR_ARRIVED, jar_file))
		self._wqueue_event.set()

	def _jar_opened_event(self, jar_data):
		self._wqueue.put(WorkQueueMessage(JarOpener.MessageTypes.JAR_OPENED, jar_data))
		self._wqueue_event.set()

	def request_stop(self):
		self._wqueue.put(WorkQueueMessage(JarOpener.MessageTypes.STOP_JAR_OPENER))
		self._wqueue_event.set()

	def wait_till_stopped(self, timeout=None):
		self._wthread.join(timeout=timeout)

	def _handle_message_event(self, message):
		if self._event_handler is not None:
			triggers = {
				JarOpener.MessageTypes.NEW_JAR_ARRIVED: self._event_handler.on_new_jar_arrived,
				JarOpener.MessageTypes.JAR_OPENED: self._event_handler.on_jar_opened,
				JarOpener.MessageTypes.STOP_JAR_OPENER: self._event_handler.on_stop,
			}

			trigger = triggers[message.type]

			return trigger(self, message.data)

	def _acquire_executor(self, callback_fn, *callback_args, **callback_kwargs):
		return self._executors_pool.submit(callback_fn, *callback_args, **callback_kwargs)

	@staticmethod
	def _run(owner, message_queue, message_event):

		def _gen_executor_callback(jar_opener, jar_file):
			def _cb():
				try:
					jar_data = jar_opener.extract_single_jar(jar_file)
					jar_opener._jar_opened_event(jar_data)
				except Exception as e:
					jar_opener._jar_opened_event(JarContent(jar_file, [], str(e)))
			return _cb

		while True:
			message_event.wait()
			m = message_queue.get()

			# todo: event may be able to return some error (or behavioral) code
			owner._handle_message_event(m)

			if m.type == JarOpener.MessageTypes.NEW_JAR_ARRIVED:
				print('JarOpener.MessageTypes.NEW_JAR_ARRIVED,', owner)
				owner._acquire_executor(_gen_executor_callback(owner, m.data))

			if m.type == JarOpener.MessageTypes.STOP_JAR_OPENER:
				break

	def extract_single_jar(self, jar_file):
		cp = subprocess.run(
			JarOpener.jar_command + [str(jar_file)],
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT
		)

		return JarContent(jar_file, self._extract_classes(cp.stdout), self._extract_errors(cp.stderr))

	def _extract_classes(self, jar_stdout):
		if jar_stdout is None:
			return None
		raw_lines = jar_stdout.decode(JarOpener.out_encoding).split(os.linesep)
		return list(filter(lambda x: x.endswith('.class'), [l.strip() for l in raw_lines]))

	def _extract_errors(self, jar_stderr):
		if jar_stderr is None:
			return None
		return jar_stderr.decode(JarOpener.out_encoding)


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


class DE(DispatcherEvents):
	def __init__(self, data_form):
		self._data_form = data_form

	def on_producer_new_work(self, dispatcher, message_data):
		super().on_producer_new_work(dispatcher=dispatcher, message_data=message_data)
		return DispatcherEventReturnCode.ITEM_OK if message_data.match('*.jar') else DispatcherEventReturnCode.DISCARD_ITEM

	def on_extractor_work_done(self, dispatcher, message_data):
		super().on_extractor_work_done(dispatcher=dispatcher, message_data=message_data)
		print('DE::on_extractor_work_done(dispatcher => %x, message_data => %s)' % (id(dispatcher), str(message_data)))
		self._data_form.add_jar(message_data)
		return DispatcherEventReturnCode.ITEM_OK


'''
class JavaClassExplorerDataModel(wx.dataview.PyDataViewModel):
	def __init__(self):
		super(JavaClassExplorerDataModel, self).__init__()
		self._data = list()

	def add_data(self, jar_content):
		print('JavaClassExplorerDataModel::add_data(jar_content => %s)' % str(jar_content))
		self._data.append(jar_content)

	def GetColumnCount(self):
		return 4

	def GetColumnType(self, col):
		mapper = {
			0: 'string',
			1: 'string',
			2: 'string',
			3: 'string',
		}
		return mapper[col]

	def IsContainer(self, item):
		return False!

	def GetChildren(self, parent, children):
		return 1

	def GetValue(self, item, col):
		node = self.ItemToObject(item)

		if isinstance(node, JarContent):
			mapper = {
				0: node.file,
				1: node.classes,
				2: node.errors,
				3: 'XXXXX',
			}
			return mapper[col]

	def GetAttr(self, item, col, attr):
		if col == 0:
			attr.SetColour('blue')
			return True
		return False
'''

class JavaClassExplorerFrame(wx.Frame):
	def __init__(self):
		super(JavaClassExplorerFrame, self).__init__(None, wx.ID_ANY, title='Java Class Explorer', size=(800, 600))

		self._dc = None
		self._create_gui()

	def _create_gui(self):
		self._panel = wx.Panel(self, wx.ID_ANY)

		tool_sizer = self._create_toolbar_sizer(self._panel)
		self._dc = self._create_data_ctrl(self._panel)

		frame_sizer = wx.BoxSizer(wx.VERTICAL)
		frame_sizer.Add(tool_sizer, 0, wx.LEFT | wx.TOP | wx.RIGHT)
		# frame_sizer.Add(self._dc, 0, wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.EXPAND)
		frame_sizer.Add(self._dc, 0, wx.ALL | wx.EXPAND)

		self._panel.SetSizer(frame_sizer)

		self._create_status_bar()

	def _create_toolbar_sizer(self, panel):
		inputLabel = wx.StaticText(panel, wx.ID_ANY, ' Scan path: ')
		inputPath = wx.TextCtrl(panel, wx.ID_ANY, 'c:/webdev/NetLedger/_dist/wlclient')
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

		return tool_sizer

	'''
	def _create_data_ctrl(self, panel):

		dvc = wx.dataview.DataViewCtrl(
			panel,
			style=wx.BORDER_THEME | wx.dataview.DV_ROW_LINES | wx.dataview.DV_VERT_RULES | wx.dataview.DV_MULTIPLE
		)

		tr = wx.dataview.DataViewTextRenderer()

		c0 = wx.dataview.DataViewColumn('Jar file', tr, 0, width=100)
		dvc.AppendColumn(c0)

		dvc.AppendTextColumn('Jar file', 1, width=170, mode=wx.dataview.DATAVIEW_CELL_ACTIVATABLE)
		dvc.AppendTextColumn('Class file', 2, width=170, mode=wx.dataview.DATAVIEW_CELL_ACTIVATABLE)
		dvc.AppendTextColumn('Class name', 3, width=170, mode=wx.dataview.DATAVIEW_CELL_ACTIVATABLE)

		dvc.AssociateModel(self._data_model)

		for c in dvc.Columns:
			c.Sortable = True
			c.Reordeable = True

		return dvc
	'''

	def _create_data_ctrl(self, panel):
		lc = wx.ListCtrl(panel, wx.ID_ANY, style=wx.LC_REPORT | wx.BORDER_SUNKEN, size=(0, 10000))
		lc.AppendColumn('Jar file', wx.LIST_FORMAT_LEFT, 300)
		lc.AppendColumn('Class file', wx.LIST_FORMAT_LEFT, 300)
		lc.AppendColumn('Class name', wx.LIST_FORMAT_LEFT, 100)
		lc.AppendColumn('Errors', wx.LIST_FORMAT_LEFT, 300)
		return lc

	def _create_status_bar(self):
		self.CreateStatusBar()
		self.SetStatusText("Welcome to Java Class Explorer!")

	def add_jar(self, jar_content):
		for c in jar_content.classes:
			self._dc.Append((jar_content.file, c.file, c.name, jar_content.errors))

	def on_list_dir(self, event):
		print('JavaClassExplorerFrame::on_list_dir()')
		pass

	def on_new_scan(self, event):
		self._dc.DeleteAllItems()
		print('JavaClassExplorerFrame::on_new_scan()')
		pass

def main():

	app = wx.App()
	# dm = JavaClassExplorerDataModel()
	frm = JavaClassExplorerFrame()
	frm.Show()

	de = DE(frm)
	dispatcher = Dispatcher(de)

	counter = 0
	for f in deep_walk_files('c:/webdev/NetLedger/_dist/wlclient'):
		dispatcher.add_producer_new_message(pathlib.Path(f))
		counter += 1
		if counter > 1:
			break

	app.MainLoop()

	dispatcher.request_stop()
	dispatcher.wait_till_stopped()


if __name__ == '__main__':
	main()
