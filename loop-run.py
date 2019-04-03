#!/bin/env python3.6

from enum import Enum, auto
import argparse
import time
import subprocess
import sys
import os


class RunMode(Enum):
	AUTO = auto(),
	USER = auto(),


def rewrite(string, pos, text):
	return string[:pos] + text + string[pos + len(text):]


def print_title(title=None, **kwargs):
	marquee = '=' * 80
	if title is not None:
		marquee = rewrite(marquee, 2, '[ ' + title + ' ]')
	print(marquee, **kwargs)


def print_output(utf8_data, title):
	if len(utf8_data) > 0:
		print_title(title)
		print(utf8_data.decode('utf-8').strip())
		print('')


def single_run(file, file_args):
	cp = subprocess.run(
		[sys.executable, file] + file_args,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
	)

	print_output(cp.stderr, 'Error')
	print_output(cp.stdout, 'Output')


def auto_loop_run(file, file_args, delay, runs):
	for i in range(runs):
		os.system('cls')
		print_title('Run %d of %d (%.1f%%): %s' % (i + 1, runs, 100.0 * (i+1) / runs, file))
		
		single_run(file, file_args)
		
		if i + 1 < runs:
			for timeout in range(delay, 0, -1):
				print_title('Next run in %0.1f seconds...' % (timeout / 10), end='\r')
				time.sleep(0.1)


def user_loop_run(file, file_args):
	loop_count = 0
	while True:
		try:
			u = input('Press enter to run ' + file + ', type anything else to break (or Ctrl+C):\n')

			if len(u) > 0:
				break

			loop_count += 1

			print_title('Loop #%d' % loop_count)
			single_run(file, file_args)

		except KeyboardInterrupt:
			break

	print_title('User broke the loop after %d cycles.' % loop_count)


def main():

	def arg_parse_run_mode(arg):
		try:
			return None if arg is None else RunMode[arg.upper()]
		except KeyError:
			raise argparse.ArgumentTypeError('Specified run mode (\'%s\') not recognized.' % arg)

	parser = argparse.ArgumentParser(description='Run python3 file over and over again.')
	parser.add_argument('--mode', type=arg_parse_run_mode, help='Run mode:'
		+ '\'auto\' = automatic looping one right after another,'
		+ '\'user\' = semiautomatic looping - requires user confirmation to run next loop.'
	)
	parser.add_argument('--delay', default=10, type=int, help='Delay between runs in hundreds of milliseconds (used when mode=auto).')
	parser.add_argument('--runs', default=10, type=int, help='Total number of runs (used when mode=auto).')
	parser.add_argument('--file', required=True, help='File to be processed.')
	parser.add_argument('--args', help='file arguments')
	args = parser.parse_args()

	file_args = [] if args.args is None else args.args.split(' ')

	if args.mode == RunMode.AUTO:
		auto_loop_run(args.file, file_args, args.delay, args.runs)
	elif args.mode == RunMode.USER:
		user_loop_run(args.file, file_args)
	else:
		raise RuntimeError('Ups, unknown run mode.')


if __name__ == '__main__':
	main()
