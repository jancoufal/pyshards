#!/bin/env python3


class TestEvents(object):
	def on_foo(self):
		pass

	def on_bar(self, bar_size):
		pass

	def on_baz(self, baz_size=None):
		pass


class TestEventInvoker(object):
	def __init__(self, event_handler):
		self._events = event_handler

	def invoke_events(self):
		self._events.on_foo()
		self._events.on_bar(42)
		self._events.on_baz(baz_size=1337)


class EventPropagator(object):

	def test(self):
		ei = TestEventInvoker(self._create_test_event_proxy())
		ei.invoke_events()

	def _create_test_event_proxy(self):
		class E(TestEvents):
			def __init__(self, owner):
				self._owner = owner

			def __getattribute__(self, item):
				print('__getattribute__', item)
				cb_map = {
					TestEvents.on_foo.__name__: self._owner._on_test_event,
					TestEvents.on_bar.__name__: self._owner._on_test_event,
					TestEvents.on_baz.__name__: self._owner._on_test_event,
				}
				return cb_map[item]

		return E(self)

	def _on_test_event(self, *args, **kwargs):
		print('_on_test_event', *args, **kwargs)

	def _private_method(self):
		print('private_method')


def main():
	ep = EventPropagator()
	ep.test()


if __name__ == '__main__':
	main()
