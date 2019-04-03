#!/bin/env python3


import os
import pathlib
import subprocess


class JavaClassDescriptor(object):
	"""
	Single Java class descriptor
	"""

	def __init__(self, class_file):
		self._file = class_file
		self._name = pathlib.Path(class_file).name

	def __str__(self):
		return '%s: %s' % (self._file, self._name)

	@property
	def file(self):
		return self._file

	@property
	def name(self):
		return self._name


class JavaJarDescriptor(object):
	"""
	Single Java JAR container descriptor
	"""

	def __init__(self, jar_file, classes=None):
		self._file = jar_file
		self._classes = classes if classes is not None else list()

	def __str__(self):
		return '%s: %d classes' % (self._file, len(self._classes))

	@classmethod
	def load_from_file(cls, jar_file):
		instance = cls(jar_file)

		jar_opener = JarOpener(jar_file)
		jar_opener.extract()

		if jar_opener.errors is not None:
			raise RuntimeError('Failed when parsing file \'%s\'.' % jar_file, jar_file, jar_opener.errors)

		for c in jar_opener.class_files:
			instance.add_class(JavaClassDescriptor(c))

		return instance

	def add_class(self, class_descriptor):
		self._classes.append(class_descriptor)

	@property
	def file(self):
		return self._file

	@property
	def classes(self):
		return self._classes


class JarOpener(object):
	_JAR_COMMAND = ['c:/Program Files/Java/jdk1.8.0_144/bin/jar.exe', 'tf']
	_COMMAND_OUTPUT_ENCODING = 'utf-8'

	def __init__(self, jar_file):
		self._jar_file = jar_file
		self._errors = None
		self._class_files = list()

	def extract(self):
		cp = subprocess.run(
			JarOpener._JAR_COMMAND + [str(self._jar_file)],
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE
		)

		self._extract_class_files(cp.stdout)
		self._extract_errors(cp.stderr)

	def _extract_class_files(self, cmd_stdout):
		if cmd_stdout is not None and len(cmd_stdout) > 0:
			raw_lines = cmd_stdout.decode(JarOpener._COMMAND_OUTPUT_ENCODING).split(os.linesep)
			self._class_files = list(filter(lambda x: x.endswith('.class'), [l.strip() for l in raw_lines]))

	def _extract_errors(self, cmd_stderr):
		if cmd_stderr is not None and len(cmd_stderr) > 0:
			print(cmd_stderr)
			self._errors = cmd_stderr.decode(JarOpener._COMMAND_OUTPUT_ENCODING)

	@property
	def class_files(self):
		return self._class_files

	@property
	def errors(self):
		return self._errors


def main():
	jar = JavaJarDescriptor.load_from_file('c:/webdev/NetLedger/_dist/cassandra/ns-cassandra-auth-plugin.jar')
	print('str():', jar)

	print('File:', jar.file)
	for c in jar.classes:
		print('Class:', str(c))


if __name__ == '__main__':
	main()
