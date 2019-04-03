#!/bin/env python3


GAME_INPUT = '''
0: 3
1: 2
2: 4
4: 4
6: 5
8: 8
10: 6
12: 6
14: 8
16: 6
18: 6
20: 8
22: 12
24: 8
26: 8
28: 12
30: 8
32: 12
34: 9
36: 14
38: 12
40: 12
42: 12
44: 14
46: 14
48: 10
50: 14
52: 12
54: 14
56: 12
58: 17
60: 10
64: 14
66: 14
68: 12
70: 12
72: 18
74: 14
78: 14
82: 14
84: 24
86: 14
94: 14
'''


def part1(game_input):
	period_hit = {k: (v - 1) * 2 for k, v in game_input.items()}

	severity = 0
	for step in range(max(period_hit.keys()) + 1):
		if step in period_hit and step % period_hit[step] == 0:
			severity += step * game_input[step]

	print('severity =', severity)


def part2(game_input):
	period_hit = {k: (v - 1) * 2 for k, v in game_input.items()}

	delay = -1
	while True:
		caught = False
		scanner_pos = delay
		for layer in range(max(period_hit.keys()) + 1):
			if layer in period_hit and scanner_pos % period_hit[layer] == 0:
				caught = True
				break
			scanner_pos += 1

		if caught:
			delay += 1
		else:
			break

	print('delay =', delay)


def main():

	def gen_key(line):
		splat = line.strip().split(':')
		return int(splat[0].strip())

	def gen_val(line):
		splat = line.strip().split(':')
		return int(splat[1].strip())

	sanitized_input = {gen_key(line): gen_val(line) for line in GAME_INPUT.strip().split('\n')}

	print('part 1')
	part1(dict(sanitized_input))

	print('part 2')
	part2(dict(sanitized_input))


if __name__ == '__main__':
	main()
