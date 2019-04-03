def cantor(a, b):
	return int((a + b) * (a + b + 1) / 2 + b)


def main():
	cp = [['%3d' % cantor(a, b) for b in range(20)] for a in range(20)]

	for b in cp:
		print(' '.join(b))


if __name__ == '__main__':
	main()
