#!/bin/env python3


from enum import Enum


class Element(Enum):
	HYDROGEN = 'H',
	HELIUM = 'He',
	LITHIUM = 'Li',

	def __init__(self, symbol):
		self._symbol = symbol

	@property
	def symbol(self):
		return self._symbol


def main():
	for elem in Element.__members__.values():
		print(str(elem) + ': ' + str(elem.symbol))

	print(10 * '-')
	print(Element.HELIUM)
	print(Element.HELIUM.symbol)


if __name__ == '__main__':
	main()
