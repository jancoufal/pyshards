import random
from sys import argv


def rnd_buff(byte_length):
	b = bytes([random.randint(0, 0xFF) for rnd in range(byte_length)])
	s = ['0x%02x' % x for x in b]
	print('{', ', '.join(s), '},')


def get_int_param(param_index, default_value):
	if len(argv) > param_index and argv[param_index].isnumeric() and int(argv[param_index]) > 0:
		return int(argv[param_index])
	return default_value


def main():
	byte_length = get_int_param(1, 16)
	repeats = get_int_param(2, 1)

	'''
	for r in range(repeats):
		#rnd_buff(byte_length)
		print(random.randint(0, 0xFFFF))
	'''

	rnd_buff(68)


if __name__ == '__main__':
	main()
