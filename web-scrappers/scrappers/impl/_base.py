import typing
import datetime
import pathlib
from ..settings import Settings
from ..sources import Source


class Base(object):
	def __init__(self, source: Source, settings: Settings):
		self._settings = settings
		self._source = source

	def write_image_info(self, local_path: pathlib.Path, image_name: str):
		ts_now = datetime.datetime.now()
		mapping = {
			"source": self._source.value,
			"ts_date": f"{ts_now:%Y-%m-%d}",
			"ts_week": f"{ts_now:%Y-%V}",
			"ts_time": f"{ts_now:%H:%M.%S,%f}",
			"local_path": str(local_path),
			"name": image_name,
			"impressions": 0,
		}

		with self._settings.sql_connection as conn:
			cols = list(mapping.keys())
			sql_stmt = f"insert into image_box({', '.join(cols)}) values (:{', :'.join(cols)})"
			conn.execute(sql_stmt, mapping)

	def read_last_images_from_db(self):
		cur = self._settings.sql_connection.cursor()
		cur.execute("select distinct name from image_box where source=? and ts_date > date('now', '-5 days')", (self._source.value, ))
		return set(row[0] for row in cur.fetchall())
