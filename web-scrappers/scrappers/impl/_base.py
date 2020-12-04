import typing
import datetime
import pathlib
import sqlite3
from ..settings import Settings
from ..sources import Source
from ..database import SqlitePersistence, ScrapPersistence


class Base(object):
	def __init__(self, source: Source, settings: Settings):
		self._settings = settings
		self._source = source
		self._db = SqlitePersistence(settings.sqlite_datafile)

	def read_last_images_from_db(self):
		with sqlite3.Connection(self._settings.sqlite_datafile) as conn:
			try:
				cur = conn.cursor()
				stmt = "select distinct name"
				stmt += " from scrap_items"
				stmt += " inner join scrap_stat on scrap_stat.scrap_stat_id = scrap_items.scrap_stat_id"
				stmt += " where scrap_stat.source=? and scrap_items.ts_date > date('now', '-1 month')"
				cur.execute(stmt, (self._source.value, ))
				return set(row[0] for row in cur.fetchall())
			finally:
				cur.close()
