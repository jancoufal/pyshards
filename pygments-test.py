#! /c/Python/3

'''
	pygments testing script
'''

import importlib
import inspect
import os.path
import pkgutil

from pygments import highlight
from pygments.formatters.other import TestcaseFormatter
from pygments.formatters.terminal256 import TerminalTrueColorFormatter
from pygments.lexers.python import PythonLexer
from pygments.style import Style


def main():
	text = get_self_content()
	test1(text)


# test2(text)


def get_self_content():
	with open(os.path.realpath(__file__), 'r') as fh:
		content = fh.read()
	return content


def test1(text):
	PYGMENT_MODULE_NAME = 'pygments'
	PYGMENT_STYLES_MODULE_NAME = 'styles'

	# find pygments module
	pygments_module_info = next(m for m in pkgutil.iter_modules() if m.name == PYGMENT_MODULE_NAME)
	pygments_module = importlib.import_module(pygments_module_info.name, pygments_module_info.module_finder.path)

	# find all styles submodules
	pygments_styles_module = next(m for m
								  in
								  pkgutil.iter_modules(pygments_module.__path__, prefix=pygments_module.__name__ + '.')
								  if m.name == PYGMENT_MODULE_NAME + '.' + PYGMENT_STYLES_MODULE_NAME)
	pygments_styles_module = importlib.import_module(pygments_styles_module.name,
													 pygments_styles_module.module_finder.path)

	#
	for m in pkgutil.iter_modules(pygments_styles_module.__path__, prefix=pygments_styles_module.__name__ + '.'):
		l = importlib.import_module(m.name, m.module_finder.path)
		styles = inspect.getmembers(l, lambda member: inspect.isclass(member) and issubclass(member,
																							 Style) and member is not Style)

		for (style_name, style_class) in styles:
			print('==[ ' + style_name + ' ]==========================')
			print(highlight(text, PythonLexer(), TerminalTrueColorFormatter(style=style_class)))
		break


def test2(text):
	print(highlight(text, PythonLexer(), TestcaseFormatter()))


if __name__ == '__main__':
	main()
