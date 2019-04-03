#!/bin/env python3


import itertools
import functools
import operator


GAME_INPUT = '192,69,168,160,78,1,166,28,0,83,198,2,254,255,41,12'


def circular_reverse(buff, buff_size, index_from, index_to):
	i1 = index_from
	i2 = index_to - 1
	
	while i1 < i2:
		buff[i1 % buff_size], buff[i2 % buff_size] = buff[i2 % buff_size], buff[i1 % buff_size]
		i1 += 1
		i2 -= 1

		
def part1(game_input):
	buff_size = 256
	buff = list(range(buff_size))
	
	position = 0
	skip_size = 0
	
	for step in game_input:
		circular_reverse(buff, buff_size, position, position + step)
		position += step + skip_size
		skip_size += 1

	print('result =', buff[0] * buff[1])


def part2(game_input):

	print(game_input)

	buff_size = 256
	buff = list(range(buff_size))

	additional_sequence = [17, 31, 73, 47, 23]
	game_input += additional_sequence

	position = 0
	skip_size = 0
	cycle_repeats = 64

	for step in itertools.chain.from_iterable(itertools.repeat(game_input, cycle_repeats)):
		circular_reverse(buff, buff_size, position, position + step)
		position += step + skip_size
		skip_size += 1

	xor_blocks = list()
	for block in range(0, buff_size, 16):
		xor_blocks.append(functools.reduce(operator.xor, buff[block:block+16]))

	result = ''.join('%02x' % v for v in xor_blocks)
	print(result)


def main():
	print('part 1')
	part1(list(map(lambda tok: int(tok), GAME_INPUT.strip().split(','))))

	print('part 2')
	part2(list(map(lambda tok: ord(tok), GAME_INPUT.strip())))


if __name__ == '__main__':
	main()
