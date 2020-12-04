import typing
import sqlite3
import datetime
import enum
import pathlib
from ..util.exception_info import ExceptionInfo


class _Tables(enum.Enum):
	SCRAP_STAT = "scrap_stat"
	SCRAP_FAILS = "scrap_fails"
	SCRAP_ITEMS = "scrap_items"


class _ScrapState(enum.Enum):
	IN_PROGRESS = "in_progress"
	COMPLETE = "complete"
	FAILED = "failed"


class _SqliteApi(object):
	def __init__(self, sqlite_datafile:pathlib.Path):
		self.sqlite_datafile = sqlite_datafile

	def write(self, table_name, value_mapping:dict):
		with sqlite3.Connection(self.sqlite_datafile) as conn:
			cols = list(value_mapping.keys())
			sql_stmt = f"insert into {table_name}({', '.join(cols)}) values (:{', :'.join(cols)})"
			conn.execute(sql_stmt, value_mapping)

	def update(self, table_name, value_mapping:dict, where_condition_mapping:dict):
		# rename all value_mapping keys to "new_{key}" and where_condition_mapping keys to "where_{key}"
		with sqlite3.Connection(self.sqlite_datafile) as conn:
			# statement pattern:
			# update table_name set col_a=:new_col_a, col_b=:new_col_b where col_c=:where_col_c and col_d=:where_col_d
			stmt_set = ", ".join(map(lambda k: f"{k}=:new_{k}", value_mapping.keys()))
			stmt_whr = " and ".join(map(lambda k: f"{k}=:where_{k}", where_condition_mapping.keys()))
			sql_stmt = f"update {table_name} set {stmt_set} where {stmt_whr}"
			conn.execute(sql_stmt, {
				**{ f"new_{k}": v for (k, v) in value_mapping.items() },
				**{ f"where_{k}": v for (k, v) in where_condition_mapping.items() }
			})

	def read_last_seq(self, table_name):
		with sqlite3.Connection(self.sqlite_datafile) as conn:
			try:
				c = conn.cursor()
				c.execute("select seq from sqlite_sequence where name=?", (table_name, ))
				return c.fetchone()[0]
			finally:
				c.close()


class _Helpers(object):
	@staticmethod
	def get_formatted_date_time_tuple(datetime_value=None):
		ts = datetime_value if datetime_value is not None else datetime.datetime.now()
		return f"{ts:%Y-%m-%d}", f"{ts:%H:%M.%S,%f}"

	@staticmethod
	def get_formatted_date_time_week_tuple(datetime_value=None):
		ts = datetime_value if datetime_value is not None else datetime.datetime.now()
		return *_Helpers.get_formatted_date_time_tuple(), f"{ts:%Y-%V}"


class SqlitePersistence(object):
	def __init__(self, sqlite_datafile):
		self._db = _SqliteApi(sqlite_datafile)

	def scrap_start(self, source):
		now_date, now_time = _Helpers.get_formatted_date_time_tuple()
		self._db.write(_Tables.SCRAP_STAT.value, {
			"source": source.value,
			"ts_start_date": now_date,
			"ts_start_time": now_time,
			"status": _ScrapState.IN_PROGRESS.value,
		})
		return ScrapPersistence(
			self._db,
			self._db.read_last_seq(_Tables.SCRAP_STAT.value)
			)


class ScrapPersistence(object):
	def __init__(self, db_api:_SqliteApi, scrap_stat_id):
		self._db = db_api
		self._scrap_stat_id = scrap_stat_id
		self._item_succ_count = 0
		self._item_fail_count = 0

	def on_scrap_item_success(self, local_path:pathlib.Path, item_name:str):
		self._item_succ_count += 1
		now_date, now_time, now_week = _Helpers.get_formatted_date_time_week_tuple()
		self._db.write(_Tables.SCRAP_ITEMS.value, {
			"scrap_stat_id": self._scrap_stat_id,
			"ts_date": now_date,
			"ts_week": now_week,
			"ts_time": now_time,
			"local_path": str(local_path).replace("\\", "/"),
			"name": item_name,
			"impressions": 0,
		})

	def on_scrap_item_failure(self, item_name:str, description:str, exception_info:ExceptionInfo):
		self._item_fail_count += 1
		now_date, now_time = _Helpers.get_formatted_date_time_tuple()
		self._db.write(_Tables.SCRAP_FAILS.value, {
			"scrap_stat_id": self._scrap_stat_id,
			"ts_date": now_date,
			"ts_time": now_time,
			"item_name": item_name,
			"description": description,
			"exc_type": str(exception_info.exception_type),
			"exc_value": str(exception_info.value),
			"exc_traceback": str(exception_info.formatted_exception),
		})

	def finish(self):
		now_date, now_time = _Helpers.get_formatted_date_time_tuple()
		self._db.update(_Tables.SCRAP_STAT.value, {
			"ts_end_date": now_date,
			"ts_end_time": now_time,
			"status": _ScrapState.COMPLETE.value,
			"succ_count": self._item_succ_count,
			"fail_count": self._item_fail_count,
		}, {
			"scrap_stat_id": self._scrap_stat_id,
		})

	def finish_exceptionaly(self, exception_info:ExceptionInfo):
		now_date, now_time = _Helpers.get_formatted_date_time_tuple()
		self._db.update(_Tables.SCRAP_STAT.value, {
			"ts_end_date": now_date,
			"ts_end_time": now_time,
			"status": _ScrapState.FAILED.value,
			"succ_count": self._item_succ_count,
			"fail_count": self._item_fail_count,
			"exc_type": str(exception_info.exception_type),
			"exc_value": str(exception_info.value),
			"exc_traceback": str(exception_info.formatted_exception),
		}, {
			"scrap_stat_id": self._scrap_stat_id,
		})
