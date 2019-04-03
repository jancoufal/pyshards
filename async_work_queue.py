#!/bin/env python3

import queue
import threading
from enum import Enum


class WorkIdGenerator(object):
	"""
	Work ID generator for AsyncWorkQueue.
	"""

	def __init__(self):
		self._counter = 0
		self._counter_reentrant_lock = threading.RLock()

	def get_and_increment(self):
		with self._counter_reentrant_lock:
			c = self._counter
			self._counter += 1
			return c


class WorkQueueMessage(object):
	"""
	Work item (task) for AsyncWorkQueue.
	"""

	def __init__(self, work_id, message_type, message_data=None):
		self._work_id = work_id
		self._message_type = message_type
		self._message_data = message_data

	def __str__(self):
		return '%s (id: %d): %s' % (str(self._message_type), self._work_id, str(self._message_data))

	@property
	def work_id(self):
		return self._work_id

	@property
	def type(self):
		return self._message_type

	@property
	def data(self):
		return self._message_data


class AsyncWorkQueue(object):
	"""
	Async work queue base.
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

	class MessageTypes(Enum):
		pass

	def __init__(self, event_handler):
		self._events = event_handler
		self._work_id_generator = WorkIdGenerator()
		self._active_works = set()
		self._no_active_works_event = threading.Event()
		self._work_queue = queue.Queue()
		self._stop_event = threading.Event()
		self._work_thread = threading.Thread(target=self._thread_loop_wrap)
		self._work_thread.start()

	def stop_request(self):
		self._stop_event.set()

	def _enqueue_work(self, message_type, data=None):
		work_message = WorkQueueMessage(self._work_id_generator.get_and_increment(), message_type, data)
		self._no_active_works_event.clear()
		self._events.on_work_enqueue(work_message)
		self._active_works.add(work_message.work_id)
		self._work_queue.put(work_message)

	def wait_till_all_work_done(self, timeout=None):
		self._no_active_works_event.wait(timeout=timeout)

	def wait_till_stopped(self, timeout=None):
		self._work_thread.join(timeout=timeout)

	def _thread_loop_wrap(self):
		while not self._stop_event.wait(0):

			try:
				work_message = self._work_queue.get(timeout=0.1)

				self._on_work_message(work_message)
				self._events.on_work_finished(work_message)
				self._active_works.remove(work_message.work_id)

				if len(self._active_works) == 0:
					self._events.on_all_work_done()
					self._no_active_works_event.set()

			except queue.Empty:
				pass

		self._events.on_stopped()

	def _on_work_message(self, work_message):
		"""
		This is the main thread loop event, that should be overridden.

		:param work_message:
		:return:
		"""
		pass
