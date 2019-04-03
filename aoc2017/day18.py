#!/bin/env python3


import itertools
from enum import Enum, auto


def main():

	game_actions = tuple(load_input('day18.dat'))
	# print(game_actions)

	print('part 1')
	machine = Machine()
	part1(game_actions, machine)

	print('part 2')
	machine = Machine()
	part2(game_actions, machine)


def load_input(game_file):
	with open(game_file, 'rt') as fh:
		lines = fh.readlines()
		for line in lines:
			yield create_action(line.split())


class Instruction(Enum):
	SND = auto()
	SET = auto()
	ADD = auto()
	MUL = auto()
	MOD = auto()
	RCV = auto()
	JGZ = auto()


def create_action(tokens):
	factory_map = {
		Instruction.SND: lambda x: lambda m: m.snd(x),
		Instruction.SET: lambda x, y: lambda m: m.set(x, y),
		Instruction.ADD: lambda x, y: lambda m: m.add(x, y),
		Instruction.MUL: lambda x, y: lambda m: m.mul(x, y),
		Instruction.MOD: lambda x, y: lambda m: m.mod(x, y),
		Instruction.RCV: lambda x: lambda m: m.rcv(x),
		Instruction.JGZ: lambda x, y: lambda m: m.jgz(x, y),
	}

	instruction = Instruction[tokens[0].upper()]
	return factory_map[instruction](*tokens[1:])


class Machine(object):
	def __init__(self):
		self._regs = dict()
		self._last_instr = None
		self._last_snd = None

	def __str__(self):
		return ', '.join(['%s(%d)' % (k, self._regs[k]) for k in self._regs.keys()])

	def _create_register_if_not_exists(self, reg):
		if reg not in self._regs:
			self._regs[reg] = 0

	@property
	def last_instruction(self):
		return self._last_instr

	def _get_register_val_or_int(self, expr):
		return self._regs[expr] if expr in self._regs else int(expr)

	def snd(self, expr):
		self._last_instr = Instruction.SND
		self._last_snd = self._get_register_val_or_int(expr)

	def set(self, reg, expr):
		self._last_instr = Instruction.SET
		self._create_register_if_not_exists(reg)
		self._regs[reg] = self._get_register_val_or_int(expr)

	def add(self, reg, expr):
		self._last_instr = Instruction.ADD
		self._create_register_if_not_exists(reg)
		self._regs[reg] += self._get_register_val_or_int(expr)

	def mul(self, reg, expr):
		self._last_instr = Instruction.MUL
		self._create_register_if_not_exists(reg)
		self._regs[reg] *= self._get_register_val_or_int(expr)

	def mod(self, reg, expr):
		self._last_instr = Instruction.MOD
		self._create_register_if_not_exists(reg)
		self._regs[reg] %= self._get_register_val_or_int(expr)

	def rcv(self, reg):
		self._last_instr = Instruction.RCV
		self._create_register_if_not_exists(reg)
		return self._last_snd if self._regs[reg] != 0 else None

	def jgz(self, reg, expr):
		self._last_instr = Instruction.JGZ
		self._create_register_if_not_exists(reg)
		return self._get_register_val_or_int(expr) if self._regs[reg] > 0 else 1


def part1(game_actions, machine):
	ip = 0

	while True:
		ret = game_actions[ip](machine)

		if machine.last_instruction == Instruction.JGZ:
			ip += int(ret)
		elif machine.last_instruction == Instruction.RCV:
			print('RCV = ' + str(ret))
			break
		else:
			ip += 1


def part2(game_actions, machine):
	pass


if __name__ == '__main__':
	main()
