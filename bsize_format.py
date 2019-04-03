#!/bin/env python3.6

from math import pow

def binary_size_format(byte_size):

	base_factor = 1024
	size = byte_size
	size_fmt = ('%d %s', '%.1f %s')
	size_hum = ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB')

	i = 0
	fmt = size_fmt[0]
	for i in range(len(size_hum)):
		if size < base_factor:
			break
		size /= base_factor
		fmt = size_fmt[1]

	return fmt % (size, size_hum[i])


if __name__ == '__main__':

	tests = (
		0,
		1,
		1024,
		pow(1024, 2),
		pow(1024, 3),
		pow(1024, 4),
		pow(1024, 5),
		pow(1024, 6),
		pow(1024, 7),
		pow(1024, 8),
		pow(1024, 9),
	)

	for t in tests:
		print('%f: %s' % (t, binary_size_format(t)))
