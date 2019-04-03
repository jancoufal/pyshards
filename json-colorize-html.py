#!/bin/python3
import json

file = r"d:\configuration.v3_test.json"


class JsonWalker(object):
	def __init__(self, json_data):
		JsonWalker.__walkers = {
			dict: JsonWalker.walk_dict,
			list: JsonWalker.walk_list,
			str: JsonWalker.walk_str,
			int: JsonWalker.walk_number,
			float: JsonWalker.walk_number,
		}
		self.j = json_data
		self.depth = 0

	def indent(self, change_level=0):
		if change_level > 0:
			self.depth += change_level
			ret = ' ' * self.depth
		elif change_level < 0:
			ret = ' ' * self.depth
			self.depth -= change_level
		else:
			ret = ' ' * self.depth

		return ret

	@staticmethod
	def get_walker(type_key):
		if type_key in JsonWalker.__walkers:
			return JsonWalker.__walkers[type_key]
		else:
			raise TypeError('No walker defined for type: ' + str(type_key))

	def walk(self):
		self.walk_impl(self.j)

	def walk_impl(self, j):
		JsonWalker.get_walker(type(j))(self, j)

	def walk_dict(self, j):
		print('%s{' % self.indent(+1))
		for i, key in enumerate(j):
			if i != 0:
				print(',')
			print('%s"%s": ' % (self.indent(), key), end='')
			self.walk_impl(j[key])
		self.indent(-1)
		print('\n%s}' % self.indent())

	def walk_list(self, j):
		print('[')
		for idx in range(len(j)):
			if idx != 0:
				print(', ', end='')
			self.walk_impl(j[idx])
		print(']')

	def walk_str(self, j):
		# print('walk_str', end = '')
		print('"%s"' % j, end='')

	def walk_number(self, j):
		# print('walk_number', end = '')
		print('%d' % j, end='')


def main():
	with open(file, 'rt') as json_file:
		j = json.loads(json_file.read())
		jsonWalker = JsonWalker(j)
		jsonWalker.walk()
	print('ok')


if __name__ == '__main__':
	main()
