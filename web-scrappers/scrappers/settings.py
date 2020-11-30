import typing
import pathlib
import sqlite3


class Settings(object):
	def __init__(self, local_base_path: pathlib.Path, local_relative_path: pathlib.Path, sql_connection: sqlite3.Connection):
		self._base_path = local_base_path
		self._relative_path = local_relative_path
		self._sql_connection = sql_connection

	@property
	def base_path(self):
		return self._base_path

	@property
	def relative_path(self):
		return self._relative_path

	@property
	def scrap_path(self):
		return self._base_path / self._relative_path

	@property
	def sql_connection(self):
		return self._sql_connection
