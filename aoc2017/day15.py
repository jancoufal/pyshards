#!/bin/env python3


# Generator A starts with 722
# Generator B starts with 354
GAME_INPUT = [722, 354]
# GAME_INPUT = [65, 8921]


def create_generator_part1(initial_value, factor):
	val = initial_value
	while True:
		new_val = (val * factor) % 0x7FFFFFFF
		val = new_val
		yield new_val


def create_generator_part2(initial_value, factor, divisibility):
	gen = create_generator_part1(initial_value, factor)
	while True:
		val = next(gen)
		if val % divisibility == 0:
			yield val


def part1(game_input):

	g1 = create_generator_part1(game_input[0], 16807)
	g2 = create_generator_part1(game_input[1], 48271)
	mask = 0xFFFF
	million = 1000 * 1000
	million_count = 0
	judge = 0

	for i in range(40 * million):
		v1 = next(g1)
		v2 = next(g2)
		# print(v1, v2)

		if i % million == 0:
			print('million:', million_count)
			million_count += 1

		if v1 & mask == v2 & mask:
			judge += 1

	print('judge =', judge)


def part2(game_input):
	g1 = create_generator_part2(game_input[0], 16807, 4)
	g2 = create_generator_part2(game_input[1], 48271, 8)
	mask = 0xFFFF
	million = 1000 * 1000
	million_count = 0
	judge = 0

	for i in range(5 * million):
		v1 = next(g1)
		v2 = next(g2)

		if i % million == 0:
			print('million:', million_count)
			million_count += 1

		if v1 & mask == v2 & mask:
			judge += 1

	print('judge =', judge)


def main():

	print('part 1')
	# part1(list(GAME_INPUT))

	print('part 2')
	part2(list(GAME_INPUT))


if __name__ == '__main__':
	main()
