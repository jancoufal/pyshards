class Point(object):
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __str__(self):
		return '[%.2f;%.2f]' % (self.x, self.y)

	def __neg__(self):
		return Point(-self.x, -self.y)

	def __add__(self, point):
		return Point(self.x + point.x, self.y + point.y)

	def __sub__(self, point):
		return Point(self.x - point.x, self.y - point.y)

	def __mul__(self, factor):
		return Point(self.x * factor, self.y * factor)

	def __rmul__(self, factor):
		return Point(self.x * factor, self.y * factor)

	def __call__(self, *args, **kwargs):
		print('oh, wow. calling a point...', *args, **kwargs)


def main():
	p1 = Point(1, 1)
	p2 = Point(2, 2)

	p3 = p1 + p2  # add
	print(p1, '+', p2, '=', p3)

	p3 = p1 - p2  # sub
	print(p1, '-', p2, '=', p3)

	p3 = p2 - p1  # sub
	print(p2, '-', p1, '=', p3)

	p3 += p1  # add
	print('(iadd) +', p1, '=', p3)

	p3 -= p1  # add
	print('(iadd) -', p1, '=', p3)

	p3 = -p1  # neg
	print('(unary)-', p1, '=', p3)

	p3 = p2 * 3  # mul
	print(p2, '* 3 =', p3)

	p3 = 3 * p2  # rmul
	print('3 *', p2, '=', p3)


if __name__ == '__main__':
	main()
