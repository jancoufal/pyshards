import sys, typing, traceback
import datetime, os, pathlib
import requests, urllib, bs4
import sqlite3
from scrapper_enum import ScrapSource
from scrapper_holders import ScrapperSettings, ScrapResult


class Null(object):
	def __init__(self, settings: ScrapperSettings):
		pass

	def scrap(self):
		return None


class _Scrapper(object):
	def __init__(self, source: str, settings: ScrapperSettings):
		self._settings = settings
		self._source = source

	def write_image_info(self, local_path: pathlib.Path, image_name: str):
		ts_now = datetime.datetime.now()
		mapping = {
			"source": self._source,
			"ts_date": f"{ts_now:%Y-%m-%d}",
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
		cur.execute("select distinct name from image_box where source=? and ts_date > date('now', '-5 days')", (self._source, ))
		return set(row[0] for row in cur.fetchall())


class Roumen(_Scrapper):

	REQUEST_HEADERS = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0",
	}

	def __init__(self, settings: ScrapperSettings):
		super().__init__(ScrapSource.ROUMEN.value, settings)
		self._base_url = "https://www.rouming.cz"
		self._base_par = {}
		self._img_base = "https://www.rouming.cz/upload"

	def scrap(self):
		ts = datetime.datetime.now()
		result = ScrapResult(ts)

		try:
			for image_to_download in self._get_images_to_download():
				destination_path = self._settings.base_path / f"{ts:%Y}" / f"{ts:%m}"

				try:
					destination_path.mkdir(parents=True, exist_ok=True)
					destination_file = destination_path / image_to_download

					remote_file_url = f"{self._img_base}/{image_to_download}"
					# r = requests.get(remote_file_url, headers=Roumen.REQUEST_HEADERS)
					urllib.request.urlretrieve(remote_file_url, filename=str(destination_file))

					# write to DB
					self.write_image_info(destination_file, image_to_download)

					result.on_item_success(destination_file, remote_file_url)

				except:
					result.on_item_failure(image_to_download, "\n".join(traceback.format_exception(*sys.exc_info())))

			result.on_scrapping_finished()

		except:
			result.on_scrapping_exception("\n".join(traceback.format_exception(*sys.exc_info())))

		return result

	def _get_images_to_download(self):
		remote_image_names = self._scrap_image_names()
		stored_image_names = self.read_last_images_from_db()
		images_to_download = [name for name in remote_image_names if name not in stored_image_names]

		# remove possible duplicates (and preserve order)
		seen = set()
		seen_add = seen.add
		return reversed([_ for _ in images_to_download if not (_ in seen or seen_add(_))])

	def _scrap_image_names(self):
		r = requests.get(self._base_url, params=self._base_par)
		soup = bs4.BeautifulSoup(r.content.decode(r.apparent_encoding), features="html.parser")

		# extract all "a" tags having "roumingShow.php" present in the "href"
		all_urls = map(lambda a: urllib.parse.urlparse(a.get("href")), soup.find_all("a"))
		all_show = [url for url in all_urls if "roumingShow.php" in url.path]

		# extract all "file" values from the query string
		all_qstr = [urllib.parse.parse_qs(url.query) for url in all_show]
		all_imgs = [qs.get("file").pop() for qs in all_qstr if "file" in qs]

		return all_imgs


class RoumenMaso(_Scrapper):
	def __init__(self, settings: ScrapperSettings):
		super().__init__(ScrapSource.ROUMEN_MASO.value, settings)

	def scrap(self):
		pass
