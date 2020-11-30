import sys, traceback
import typing
import pathlib
import datetime
from .sources import Source


class ExceptionResultItem(object):
	@classmethod
	def createFromLastException(cls):
		return cls(*sys.exc_info())

	def __init__(self, exception_type, value, traceback):
		self._exception_type = exception_type
		self._value = value
		self._traceback = traceback

	@property
	def exception_type(self):
		return self._exception_type

	@property
	def value(self):
		return self._value

	@property
	def traceback(self):
		return self._traceback

	@property
	def formatted_exception(self):
		return traceback.format_exception(etype=self.exception_type, value=self.value, tb=self.traceback)
		

class Result(object):
	@classmethod
	def create_empty(cls):
		pass

	def __init__(self, source: Source, ts_start: datetime.datetime=None):
		self._source = source
		self._ts_start = ts_start if ts_start is not None else datetime.datetime.now()
		self._time_taken = "unknown"
		self._items_suceeded = 0
		self._items_failed = 0
		self._errors = list()
		self._general_error = list()

	def __str__(self):
		return f"Result of [{self._source.value}] scrapper: {self.items_suceeded} of {self.items_total} ({self.suceeded_percentage_str}) scrapped in {self.time_taken}"

	def on_item_success(self, local_file: pathlib.Path, url: str):
		self._items_suceeded += 1

	def on_item_failure(self, item_name: str, error: ExceptionResultItem):
		self._items_failed += 1
		self._errors.append((item_name, error))

	def on_scrapping_finished(self):
		self._time_taken = str(datetime.datetime.now() - self._ts_start)

	def on_scrapping_exception(self, error: ExceptionResultItem):
		self._general_error = error
		self.on_scrapping_finished()

	@property
	def time_taken(self):
		return self._time_taken

	@property
	def items_total(self):
		return self._items_suceeded + self._items_failed

	@property
	def items_suceeded(self):
		return self._items_suceeded

	@property
	def items_failed(self):
		return self._items_failed

	@property
	def suceeded_percentage_str(self):
		return "n/a" if self.items_total == 0 else f"{(100.0 * self.items_suceeded) / self.items_total:3.2f}%"

	@property
	def errors_list(self):
		return self._errors

	@property
	def general_error_list(self):
		return self._general_error
