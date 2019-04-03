def foo1(): print('foo1'); return 'foo1'
def foo2(): print('foo2'); return 'foo2'
def foo3(): print('foo3'); return None
def foo4(): print('foo4'); return 'foo4'
def foo5(): print('foo5'); return 'foo5'


def main():
	fns = []
	fns.append(foo1)
	fns.append(foo2)
	fns.append(foo3)
	fns.append(foo4)
	fns.append(foo5)

	print([fn() for fn in fns if fn() is not None])

if __name__ == '__main__':
	main()
