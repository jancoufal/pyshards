#!/bin/env python3


class A(object):
	pass


class B(A):
	pass


def main():
	a = A()
	b = B()

	print('A.__class__:', A.__class__)
	print('B.__class__:', B.__class__)
	print('a.__class__:', a.__class__)
	print('b.__class__:', b.__class__)
	print('type(A):', type(A))
	print('type(B):', type(B))
	print('type(a):', type(a))
	print('type(b):', type(b))
	print('isinstance(a, A):', isinstance(a, A))
	print('isinstance(a, B):', isinstance(a, B))
	print('isinstance(b, A):', isinstance(b, A))
	print('isinstance(b, B):', isinstance(b, B))
	print('type(a) == A:', type(a) == A)
	print('type(a) == B:', type(a) == B)
	print('type(b) == A:', type(b) == A)
	print('type(b) == B:', type(b) == B)


if __name__ == '__main__':
	main()
