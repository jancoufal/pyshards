#!/bin/env python3

import concurrent.futures
import threading
from enum import Enum, auto

from async_work_queue import AsyncWorkQueue
from jar_opener import JavaJarDescriptor


class AsyncJarOpener(AsyncWorkQueue):
	class Events(AsyncWorkQueue.Events):
		def on_jar_extracted(self, jar_descriptor):
			pass

		def on_jar_extraction_failure(self, jar_file, exception):
			pass

	class _AsyncWorkQueueEventsProxy(AsyncWorkQueue.Events):
		"""
		AsyncWorkQueue.Events must be handled by AsyncJarOpener itself!
		"""

		def __init__(self, event_consumer):
			self._consumer = event_consumer

		def on_work_enqueue(self, work_message):
			self._consumer._on_work_enqueue(work_message)

		def on_work_finished(self, work_message):
			self._consumer._on_work_finished(work_message)

		def on_all_work_done(self):
			self._consumer._on_all_work_done()

		def on_stopped(self):
			self._consumer._on_stopped()
	#
	# def on_jar_extracted(self, jar_descriptor):
	# 	self._events.on_jar_extracted(jar_descriptor)
	#
	# def on_jar_extraction_failure(self, jar_file, exception):
	# 	self._events.on_jar_extraction_failure(jar_file, exception)

	class MessageTypes(Enum):
		NEW_JAR_ENQUEUED = auto(),
		JAR_EXTRACTED = auto(),
		JAR_EXTRACTION_FAILURE = auto(),

	_MAX_CONCURRENT_EXECUTORS = 5

	def __init__(self, event_handler):
		self._executor_futures_lock = threading.RLock()
		self._executor_futures_empty_event = threading.Event()
		self._executor_futures = set()
		self._executor_futures_empty_event.set()
		self._executors_pool = concurrent.futures.ThreadPoolExecutor(
			max_workers=AsyncJarOpener._MAX_CONCURRENT_EXECUTORS,
			# thread_name_prefix=AsyncJarOpener.__class__.__name__
		)
		self._events_no_proxy = event_handler
		super().__init__(AsyncJarOpener._AsyncWorkQueueEventsProxy(self))

	# override of AsyncWorkQueue.Events.on_work_enqueue
	def _on_work_enqueue(self, work_message):
		self._events_no_proxy.on_work_enqueue(work_message)

	# override of AsyncWorkQueue.Events.on_work_finished
	def _on_work_finished(self, work_message):
		self._events_no_proxy.on_work_finished(work_message)

	# override of AsyncWorkQueue.Events.on_all_work_done
	def _on_all_work_done(self):
		self._events_no_proxy.on_all_work_done()

	# override of AsyncWorkQueue.Events.on_stopped
	def _on_stopped(self):
		self._events_no_proxy.on_stopped()

	def _register_future(self, future):
		with self._executor_futures_lock:
			self._executor_futures_empty_event.clear()
			self._executor_futures.add(future)
			print('_register_future(future => %s), active futures: %d' % (str(future), len(self._executor_futures)))

	def _unregister_future(self, future):
		with self._executor_futures_lock:
			self._executor_futures.remove(future)
			if len(self._executor_futures) == 0:
				self._executor_futures_empty_event.set()
			print('_unregister_future(future => %s), active futures: %d' % (str(future), len(self._executor_futures)))

	def add_jar_file(self, jar_file):
		self._enqueue_work(AsyncJarOpener.MessageTypes.NEW_JAR_ENQUEUED, jar_file)

	def wait_till_all_work_done(self, timeout=None):
		self._executor_futures_empty_event.wait(timeout=timeout)
		super().wait_till_all_work_done(timeout=timeout)

	def wait_till_stopped(self, timeout=None):
		self._executor_futures_empty_event.wait(timeout=timeout)
		super().wait_till_stopped(timeout=timeout)

	# todo: do we really want to do that?
	# with self._executor_futures_lock:
	# 	for future in self._executor_futures:
	# 		future.cancel()

	def _acquire_jar_opener_executor(self, work_message):
		def _generate_executor_callback():
			def _cb():
				try:
					jar_descriptor = JavaJarDescriptor.load_from_file(work_message.data)
					self._enqueue_work(AsyncJarOpener.MessageTypes.JAR_EXTRACTED, (work_message, jar_descriptor))
				except Exception as e:
					self._enqueue_work(AsyncJarOpener.MessageTypes.JAR_EXTRACTION_FAILURE, (work_message, e))

			return _cb

		future = self._executors_pool.submit(_generate_executor_callback())
		self._register_future(future)
		future.add_done_callback(lambda f: self._unregister_future(f))

		return future

	def _on_work_message(self, work_message):
		if work_message.type == AsyncJarOpener.MessageTypes.NEW_JAR_ENQUEUED:
			self._acquire_jar_opener_executor(work_message)

		if work_message.type == AsyncJarOpener.MessageTypes.JAR_EXTRACTED:
			self._events.on_jar_extracted(work_message.data)

		if work_message.type == AsyncJarOpener.MessageTypes.JAR_EXTRACTION_FAILURE:
			self._events.on_jar_extraction_failure(*work_message.data)


def main():
	class AJOE(AsyncJarOpener.Events):
		def on_work_enqueue(self, work_message):
			print('AsyncJarOpener.Events.on_work_enqueue(work_message => %s)' % str(work_message))

		def on_work_finished(self, work_message):
			print('AsyncJarOpener.Events.on_work_finished(work_message => %s)' % str(work_message))

		def on_all_work_done(self):
			print('AsyncJarOpener.Events.on_all_work_done()')

		def on_stopped(self):
			print('AsyncJarOpener.Events.on_stopped()')

		def on_jar_extracted(self, jar_descriptor):
			print('AsyncJarOpener.Events.on_jar_extracted(java_jar_descriptor => %s)' % str(jar_descriptor))

		def on_jar_extraction_failure(self, jar_file, exception):
			print('AsyncJarOpener.Events.on_jar_extraction_failure(jar_file => %s, exception => %s)' % (
			str(jar_file), str(exception)))

	ajo = AsyncJarOpener(AJOE())

	print('Enqueueing work...')
	# ajo.add_jar_file('c:/webdev/NetLedger/_dist/cassandra/unboundid-ldapsdk-2.3.4.jar')
	ajo.add_jar_file('c:/webdev/NetLedger/_dist/dx/ns-dx-all.jar')
	# ajo.add_jar_file('c:/webdev/NetLedger/_dist/cassandra/ns-ldap-auth.jar')

	print('Waiting till all work is done...')
	ajo.wait_till_all_work_done()
	print('Work is done...')

	# print('Enqueueing work again...')
	# ajo.add_jar_file('c:/webdev/NetLedger/_dist/cassandra/unboundid-ldapsdk-2.3.4.jar')
	# ajo.add_jar_file('c:/webdev/NetLedger/_dist/dx/ns-dx-all.jar')
	# ajo.add_jar_file('c:/webdev/NetLedger/_dist/cassandra/ns-ldap-auth.jar')
	#
	# print('Waiting till all work is done again...')
	# ajo.wait_till_all_work_done()
	# print('Work is done again...')

	print('Requesting stop...')
	ajo.stop_request()
	ajo.wait_till_stopped()
	print('Test finished.')


if __name__ == '__main__':
	main()
