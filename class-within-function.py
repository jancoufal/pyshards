#!/bin/env python3


def main():
	class C(object):
		def foo(self):
			print('main::C::foo()')

	c = C()
	c.foo()


if __name__ == '__main__':
	main()
