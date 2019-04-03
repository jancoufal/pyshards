#!/bin/env python3


GAME_INPUT = 312051


def part1(game_input):

	def centered_octagonal_number(n):
		"""aka A016754 sequence"""
		return (2 * n + 1) ** 2

	def find_square_size_level():
		for n in range(1000):
			con = centered_octagonal_number(n)
			if game_input < con:
				return n
		raise Exception('Could not find proper square. Too big number.')

	def get_corners(_square_size_level):
		"""
		<code>
		17  16  15  14  13
		18   5   4   3  12
		19   6   1   2  11
		20   7   8   9  10
		21  22  23---> ...
		1 -> (1,1,1,1)
		2 -> (3,5,7,9)
		3 -> (13,17,21,25)
		"""
		if _square_size_level == 0:
			return 1, 1, 1, 1
		else:
			edge_size = (2 * _square_size_level + 1) - 1
			con = centered_octagonal_number(_square_size_level)
			return tuple(con - l * edge_size for l in range(3, -1, -1))

	def find_edge(_corners):
		_edge = -1
		if game_input <= _corners[0]:
			_edge = 0

		for e in range(3):
			if _corners[e] < game_input <= _corners[e+1]:
				_edge = e + 1

		return _edge

	def get_edge_midpoint(_square_size_level, _corners, _edge):
		return _corners[_edge] - _square_size_level

	# find the square, that contains GAME_INPUT number
	square_size_level = find_square_size_level()
	print('square_size_level = %d' % square_size_level)

	corners = get_corners(square_size_level)
	print('corners = %s' % str(corners))

	edge = find_edge(corners)
	print('edge = %d' % edge)

	edge_midpoint = get_edge_midpoint(square_size_level, corners, edge)
	print('edge_midpoint = %d' % edge_midpoint)

	distance_to_midpoint = abs(edge_midpoint - game_input)
	print('distance_to_midpoint = %d' % distance_to_midpoint)

	manhattan_distance = distance_to_midpoint + square_size_level
	print('manhattan_distance = %d' % manhattan_distance)


def part2(game_input):
	"""
	see
	https://oeis.org/A141481
	https://oeis.org/A141481/b141481.txt -> row: 61 312453
	"""
	print('312453')


def main():
	game_input = GAME_INPUT

	print('part 1')
	part1(game_input)

	print('part 2')
	part2(game_input)


if __name__ == '__main__':
	main()
