#!/bin/env python3


import itertools


def main():

	game_actions = tuple(load_input('day16.dat'))
	# print(game_actions)

	print('part 1')
	game_buffer = CircularBuffer.create_game_buffer(16)
	part1(game_actions, game_buffer)

	print('part 2')
	game_buffer = CircularBuffer.create_game_buffer(16)
	part2(game_actions, game_buffer)


def load_input(game_file):
	with open(game_file, 'rt') as fh:
		lines = fh.readlines()
		for line in lines:
			yield from create_actions(line.split(','))


def create_actions(tokens):
	for token in tokens:
		yield create_action(token)


def create_action(token):
	factory_map = {
		's': ActionSpin,
		'x': ActionExchange,
		'p': ActionPartner,
	}
	return factory_map[token[0]](*token[1:].split('/'))


class ActionSpin(object):
	def __init__(self, amount):
		self.amount = int(amount)

	def __str__(self):
		return 'spin ' + str(self.amount)

	def get_tuples(self):
		return self.amount,


class ActionExchange(object):
	def __init__(self, pos1, pos2):
		self.pos1 = int(pos1)
		self.pos2 = int(pos2)

	def __str__(self):
		return 'exchange ' + str(self.pos1) + ' with ' + str(self.pos2)

	def get_tuples(self):
		return self.pos1, self.pos2


class ActionPartner(object):
	def __init__(self, name1, name2):
		self.name1 = name1
		self.name2 = name2

	def __str__(self):
		return 'partner swap ' + self.name1 + ' with ' + self.name2

	def get_tuples(self):
		return self.name1, self.name2


class CircularBuffer(object):
	def __init__(self, items):
		self._items = list(items)
		self._size = len(self._items)
		self._index = 0

	@classmethod
	def create_game_buffer(cls, size):
		return cls([chr(ord('a') + i) for i in range(size)])

	def __str__(self):
		return ''.join(['(' + itm + ')' if idx == self._index else itm for idx, itm in enumerate(self._items)])

	def get_result_string(self):
		return ''.join(self._items[self._index:] + self._items[0: self._index])

	def do_action(self, action):
		action_map = {
			ActionSpin: CircularBuffer._action_spin,
			ActionExchange: CircularBuffer._action_exchange,
			ActionPartner: CircularBuffer._action_partner,
		}
		action_map[type(action)](self, *action.get_tuples())

	def _action_spin(self, amount):
		# print('_action_spin(amount => %d)' % amount)
		self._index -= amount
		self._index %= self._size

	def _action_exchange(self, pos1, pos2):
		# print('_action_exchange(%d <-> %d)' % (pos1, pos2))
		self._swap_items(
			(self._index + pos1) % self._size,
			(self._index + pos2) % self._size
		)

	def _action_partner(self, name1, name2):
		# print('_action_partner(%s <-> %s)' % (name1, name2))
		self._swap_items(
			self._items.index(name1),
			self._items.index(name2)
		)

	def _swap_items(self, idx1, idx2):
		self._items[idx1], self._items[idx2] = self._items[idx2], self._items[idx1]


def part1(game_actions, game_buffer):
	for game_action in game_actions:
		game_buffer.do_action(game_action)

	print(game_buffer.get_result_string())


def part2(game_actions, game_buffer):
	round_limit = 1000 * 1000 * 1000
	loops = 0
	for game_action in itertools.cycle(game_actions):
		game_buffer.do_action(game_action)

		if (loops % (10 * 1000 * 1000)) == 0:
			print(loops / (10 * 1000 * 1000), 'x 10m')

		if loops > round_limit - 5:
			print(loops, ':', game_buffer.get_result_string())

		if loops > round_limit + 5:
			break

		loops += 1

	print(game_buffer.get_result_string())


if __name__ == '__main__':
	main()
