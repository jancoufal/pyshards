#!/bin/env python3


class C1(object):
	def __init__(self, i, j, k):
		print('C1::__init__()')
		self.i = i
		print('i = %s, j = %s, k = %s' % (str(i), str(j), str(k)))


class C2(C1):
	def __init__(self, *args, **kwargs):
		print('C2::__init__()')
		super().__init__(*args, **kwargs)

	def foo(self):
		print('C2::foo(%d)' % self.i)


def main():
	c2 = C2(1, 2, 3)
	c2.foo()


if __name__ == '__main__':
	main()
