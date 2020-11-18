import typing
import pathlib
import sqlite3
import datetime

class ScrapperSettings(object):
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


class ScrapResult(object):
	@classmethod
	def create_empty(cls):
		pass

	def __init__(self, ts_start: datetime.datetime=None):
		self._ts_start = ts_start if ts_start is not None else datetime.datetime.now()
		self._time_taken = "unknown"
		self._items_scrapped = 0
		self._items_failed = 0
		self._errors = list()
		self._general_error = None

	def on_item_success(self, local_file: pathlib.Path, url: str):
		self._items_scrapped += 1

	def on_item_failure(self, item_name: str, error_message: str):
		self._items_failed += 1
		self._errors.append((item_name, error_message))

	def on_scrapping_finished(self):
		self._time_taken = str(datetime.datetime.now() - self._ts_start)

	def on_scrapping_exception(self, error_message: str):
		self._exception_str = error_message

	@property
	def time_taken(self):
		return self._time_taken

	@property
	def items_scrapped(self):
		return self._items_scrapped

	@property
	def items_failed(self):
		return self._items_failed

	@property
	def general_error(self):
		return self._general_error

	@property
	def errors(self):
		return self._errors
