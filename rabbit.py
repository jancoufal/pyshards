#!/bin/env python3

# https://www.google.com/doodles/celebrating-50-years-of-kids-coding


from enum import Enum


class Direction(Enum):
	UP = 'A'
	RIGHT = '>'
	DOWN = 'V'
	LEFT = '<'

	def __init__(self, symbol):
		self._symbol = symbol

	@property
	def symbol(self):
		return self._symbol

	@staticmethod
	def rotate(direction, to_right):
		# -> rotate right
		# <- rotate left
		rot_map = (
			(Direction.UP, Direction.RIGHT),
			(Direction.RIGHT, Direction.DOWN),
			(Direction.DOWN, Direction.LEFT),
			(Direction.LEFT, Direction.UP)
		)

		src_index = 0 if to_right else 1
		res_index = 1 if to_right else 0

		new_direction = next(filter(lambda item: item[src_index] == direction, rot_map))

		return new_direction[res_index]


class ActorAction(Enum):
	FORWARD = 'f'
	ROTATE_RIGHT = 'r'
	ROTATE_LEFT = 'l'

	def __init__(self, symbol):
		self._symbol = symbol

	@property
	def symbol(self):
		return self._symbol

	@staticmethod
	def symbol_to_type(symbol):
		for v in ActorAction.__members__.values():
			if v.symbol == symbol:
				return v

		raise IndexError('Unknown enum for symbol ' + symbol)


class FiledType(Enum):
	PLAIN = ('.', True)
	CARROT = ('c', True)
	WALL = ('x', False)

	def __init__(self, symbol, is_walkable):
		self._symbol = symbol
		self._is_walkable = is_walkable

	@property
	def symbol(self):
		return self._symbol

	@property
	def is_walkable(self):
		return self._is_walkable

	@staticmethod
	def symbol_to_type(symbol):
		for v in FiledType.__members__.values():
			if v.symbol == symbol:
				return v

		raise IndexError('Unknown enum for symbol ' + symbol)


class GameBoardField(object):
	def __init__(self, field_type):
		self._steps = 0
		self._type = field_type

	@property
	def type(self):
		return self._type

	@property
	def steps(self):
		return self._steps

	def do_step(self):
		self._steps += 1


class GameBoardState(object):
	def __init__(self):
		self._board = list()
		self._create_board()

	def _create_board(self):
		def row_adder(symbol_string):
			self._board.append(list(GameBoardField(FiledType.symbol_to_type(ch)) for ch in symbol_string))

		row_adder('xcccx')
		row_adder('c...c')
		row_adder('c...c')
		row_adder('c...c')
		row_adder('xcccx')

	def __str__(self):
		s = ''
		for row in self._board:
			s += ''.join(cell.type.symbol for cell in row)
			s += 8 * ' '
			s += ' '.join('%2d' % cell.steps for cell in row)
			s += '\n'
		return s

	def step_on_board(self, x, y):
		self._board[x][y].do_step()

	def can_step_on(self, x, y):
		try:
			if x < 0 or y < 0:
				return False

			return self._board[x][y].type.is_walkable
		except IndexError:
			return False


class GameActorState(object):
	def __init__(self, position_x, position_y, direction):
		self._x = position_x
		self._y = position_y
		self._direction = direction

	def __str__(self):
		return 'position(%d; %d), heading: %s' % (self._x, self._y, str(self._direction))

	@property
	def position_x(self):
		return self._x

	@property
	def position_y(self):
		return self._y

	@property
	def direction(self):
		return self._direction

	def set_position(self, position_x, position_y):
		self._x = position_x
		self._y = position_y

	def set_direction(self, direction):
		self._direction = direction

	def try_step(self):
		"""
		get a new step position based on current location and direction (no boundaries)
		:return: tuple (new position)
		"""
		step_size = 1
		new_x = self.position_x
		new_y = self.position_y

		if self._direction == Direction.UP:
			new_x -= step_size

		if self._direction == Direction.DOWN:
			new_x += step_size

		if self._direction == Direction.RIGHT:
			new_y += step_size

		if self._direction == Direction.LEFT:
			new_y -= step_size

		return new_x, new_y


class GameState(object):
	def __init__(self):
		self._board = GameBoardState()
		self._rabbit = GameActorState(2, 2, Direction.UP)
		self.update()

	def update(self):
		self._board.step_on_board(
			self._rabbit.position_x,
			self._rabbit.position_y
		)

	def step_forward(self):
		new_pos = self._rabbit.try_step()
		if self._board.can_step_on(*new_pos):
			self._rabbit.set_position(*new_pos)
			self._board.step_on_board(*new_pos)

	def rotate_rabbit_right(self):
		new_direction = Direction.rotate(self._rabbit.direction, True)
		self._rabbit.set_direction(new_direction)

	def rotate_rabbit_left(self):
		new_direction = Direction.rotate(self._rabbit.direction, False)
		self._rabbit.set_direction(new_direction)

	def __str__(self):
		s = str(self._board)
		s += str(self._rabbit)
		s += '\n'
		return s


class GameActions(object):
	def __init__(self, game_state):
		self._gs = game_state

	def do_action(self, actor_action):
		aa_map = {
			ActorAction.FORWARD: self._gs.step_forward,
			ActorAction.ROTATE_RIGHT: self._gs.rotate_rabbit_right,
			ActorAction.ROTATE_LEFT: self._gs.rotate_rabbit_left,
		}

		aa_map[actor_action]()

	def do_actions(self, symbol_string):
		for symb in symbol_string:
			aa = ActorAction.symbol_to_type(symb)
			self.do_action(aa)


def main():
	gs = GameState()
	ga = GameActions(gs)

	for _ in range(4):
		for __ in range(4):
			ga.do_actions('flf')
		ga.do_actions('l')

	print(gs)


if __name__ == '__main__':
	main()
