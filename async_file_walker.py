#!/bin/env python3

from async_work_queue import AsyncWorkQueue
from enum import Enum, auto
import os


class AsyncFileWalker(AsyncWorkQueue):
	class Events(AsyncWorkQueue.Events):
		def on_file(self, file_name):
			pass

	class MessageTypes(Enum):
		NEW_DIR_ENQUEUED = auto(),

	def add_directory(self, directory):
		self._enqueue_work(AsyncFileWalker.MessageTypes.NEW_DIR_ENQUEUED, directory)

	def _file_walker_generator(self, root_directory):
		for r, d, f in os.walk(str(root_directory), followlinks=False):
			yield from map(lambda x: os.path.join(r, x), f)

	def _on_work_message(self, work_message):
		if work_message.type == AsyncFileWalker.MessageTypes.NEW_DIR_ENQUEUED:
			for file_name in self._file_walker_generator(work_message.data):
				self._events.on_file(file_name)


def main():
	class AFWE(AsyncFileWalker.Events):
		def on_work_enqueue(self, work_message):
			print('AsyncFileWalker.Events.on_work_enqueue(work_message => %s)' % str(work_message))

		def on_work_finished(self, work_message):
			print('AsyncFileWalker.Events.on_work_finished(work_message => %s)' % str(work_message))

		def on_all_work_done(self):
			print('AsyncFileWalker.Events.on_all_work_done()')

		def on_stopped(self):
			print('AsyncFileWalker.Events.on_stopped()')

		def on_file(self, file_name):
			# print('AsyncFileWalker.Events.on_file(file_name => %s)' % str(file_name))
			pass

	afw = AsyncFileWalker(AFWE())
	afw.add_directory('c:/webdev/NetLedger/.gradle')
	afw.add_directory('c:/webdev/NetLedger')
	afw.add_directory('c:/webdev/NetLedger/.gradle')

	print('Waiting till all work is done...')
	afw.wait_till_all_work_done()

	afw.add_directory('c:/webdev/NetLedger/.gradle')
	afw.add_directory('c:/webdev/NetLedger')
	afw.add_directory('c:/webdev/NetLedger/.gradle')

	print('Waiting till all work is done again...')
	afw.wait_till_all_work_done()

	print('Requesting stop...')
	afw.stop_request()
	afw.wait_till_stopped()


if __name__ == '__main__':
	main()
