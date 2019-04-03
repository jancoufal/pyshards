#!/bin/env python3


import itertools
import functools
import operator


GAME_INPUT = 312


def main():
	print('part 1')
	part1(GAME_INPUT)

	print('part 2')
	part2(GAME_INPUT)


def part1(game_input):
	buff = [0]
	pos = 0

	for step in range(2017):
		pos = (pos + game_input) % len(buff)
		if (pos + 1) % len(buff) == 0:
			buff.append(step + 1)
		else:
			buff.insert((pos + 1) % len(buff), step + 1)
		pos += 1

	print('spinlock =', buff[pos + 1])


def part2(game_input):
	buff = [0]
	pos = 0

	for step in range(50 * 1000 * 1000):

		if step % (100 * 1000) == 0:
			print(step / (100 * 1000), 'ck (500)')

		pos = (pos + game_input) % len(buff)
		if (pos + 1) % len(buff) == 0:
			buff.append(step + 1)
		else:
			buff.insert((pos + 1) % len(buff), step + 1)
		pos += 1

	print('spinlock =', buff[buff.index(0) + 1])


if __name__ == '__main__':
	main()
