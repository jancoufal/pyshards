#!/bin/env python3


GAME_INPUT = '2	8	8	5	4	2	3	1	5	5	1	2	15	13	5	14'


def part1(game_input):
	backtrace = set()
	iterations = 0
	game_input_len = len(game_input)
	while True:
		if tuple(game_input) in backtrace:
			break
		iterations += 1
		backtrace.add(tuple(game_input))

		idx = game_input.index(max(game_input))
		val = game_input[idx]
		game_input[idx] = 0

		for distr in range(val):
			game_input[(distr + idx + 1) % game_input_len] += 1

	print('iterations =', iterations)


def part2(game_input):
	backtrace = list()
	iterations = 0
	game_input_len = len(game_input)
	while True:
		if tuple(game_input) in backtrace:
			cycles = iterations - backtrace.index(tuple(game_input))
			break
		iterations += 1
		backtrace.append(tuple(game_input))

		idx = game_input.index(max(game_input))
		val = game_input[idx]
		game_input[idx] = 0

		for distr in range(val):
			game_input[(distr + idx + 1) % game_input_len] += 1

	print('repeat cycles =', cycles)


def main():
	sanitized_input = [int(row) for row in GAME_INPUT.strip().split()]

	print('part 1')
	part1(list(sanitized_input))

	print('part 2')
	part2(list(sanitized_input))


if __name__ == '__main__':
	main()
