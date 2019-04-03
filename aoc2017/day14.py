#!/bin/env python3


import itertools
import functools
import operator


GAME_INPUT = 'jxqlasbh'


def main():
	knot_names = tuple('%s-%d' % (GAME_INPUT, i) for i in range(128))
	sanitized_input = tuple(tuple(map(lambda tok: ord(tok), knot_name)) for knot_name in knot_names)

	print('part 1')
	part1(sanitized_input)

	print('part 2')
	part2(sanitized_input)


def circular_reverse(buff, buff_size, index_from, index_to):
	i1 = index_from
	i2 = index_to - 1

	while i1 < i2:
		buff[i1 % buff_size], buff[i2 % buff_size] = buff[i2 % buff_size], buff[i1 % buff_size]
		i1 += 1
		i2 -= 1


def get_knot_hash_xor(input_data):
	buff_size = 256
	buff = list(range(buff_size))

	additional_sequence = tuple((17, 31, 73, 47, 23))
	input_data += additional_sequence

	position = 0
	skip_size = 0
	cycle_repeats = 64

	for step in itertools.chain.from_iterable(itertools.repeat(input_data, cycle_repeats)):
		circular_reverse(buff, buff_size, position, position + step)
		position += step + skip_size
		skip_size += 1

	xor_blocks = list()
	for block in range(0, buff_size, 16):
		xor_blocks.append(functools.reduce(operator.xor, buff[block:block+16]))

	return xor_blocks


def get_knot_hash_str(xor_blocks):
	return ''.join('%02x' % v for v in xor_blocks)


def part1(game_input):
	def print_mapper(bool_value):
		return {'0': '.', '1': '#'}[bool_value]

	used = 0
	for inp in game_input:
		knot_hash = get_knot_hash_xor(inp)
		bin_string = ''.join('{0:08b}'.format(val) for val in knot_hash)
		# print(''.join(map(print_mapper, bin_string)))
		for ch in bin_string:
			if ch == '1':
				used += 1

	print('used =', used)


def part2(game_input):

	MATRIX_SIZE = 128

	def bool_mapper(bool_value):
		return {'0': False, '1': True}[bool_value]

	def flood_fill(matrix, _r, _c):
		if 0 <= _r < MATRIX_SIZE and 0 <= _c < MATRIX_SIZE and matrix[_r][_c]:
			matrix[_r][_c] = False
			flood_fill(matrix, _r, _c - 1)
			flood_fill(matrix, _r, _c + 1)
			flood_fill(matrix, _r - 1, _c)
			flood_fill(matrix, _r + 1, _c)

	disk_map = list()
	for inp in game_input:
		knot_hash = get_knot_hash_xor(inp)
		bin_string = ''.join('{0:08b}'.format(val) for val in knot_hash)
		disk_map.append(list(map(bool_mapper, bin_string)))

	# flood fill the regions
	regions = 0
	for r in range(MATRIX_SIZE):
		for c in range(MATRIX_SIZE):
			if disk_map[r][c]:
				regions += 1
				flood_fill(disk_map, r, c)

	print('regions =', regions)


if __name__ == '__main__':
	main()
