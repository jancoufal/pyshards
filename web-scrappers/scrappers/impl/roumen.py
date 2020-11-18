import sys, typing, traceback
import datetime, os, pathlib
import requests, urllib, bs4
import sqlite3
from ._base import Base
from ..sources import Source
from ..settings import Settings
from ..result import Result


class Roumen(Base):

	REQUEST_HEADERS = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0",
	}

	def __init__(self, settings: Settings):
		super().__init__(Source.ROUMEN.value, settings)
		self._base_url = "https://www.rouming.cz"
		self._base_par = {}
		self._img_base = "https://www.rouming.cz/upload"

	def scrap(self):
		ts = datetime.datetime.now()
		result = Result(ts)

		try:
			for image_to_download in self._get_images_to_download():
				ts_path = pathlib.Path(f"{ts:%Y}").joinpath(f"{ts:%m}")
				destination_path = self._settings.scrap_path / ts_path

				try:
					destination_path.mkdir(parents=True, exist_ok=True)
					destination_file = destination_path / image_to_download

					remote_file_url = f"{self._img_base}/{image_to_download}"
					# r = requests.get(remote_file_url, headers=Roumen.REQUEST_HEADERS)
					urllib.request.urlretrieve(remote_file_url, filename=str(destination_file))

					# write to DB
					self.write_image_info(ts_path / image_to_download, image_to_download)

					result.on_item_success(ts_path / image_to_download, remote_file_url)

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
