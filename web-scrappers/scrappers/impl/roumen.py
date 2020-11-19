import sys, typing, traceback
import datetime, os, pathlib
import requests, urllib, bs4
import sqlite3
from ._base import Base
from ..sources import Source
from ..settings import Settings
from ..result import Result


class _RoumenSettings(object):
	def __init__(self, base_url: str, base_url_params: dict, img_base: str, href_needle: str):
		self.base_url = base_url
		self.base_url_params = base_url_params
		self.img_base = img_base
		self.href_needle = hre


class BaseRoumen(Base):

	REQUEST_HEADERS = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0",
	}

	def __init__(self, source: Source, settings: Settings, roumen_settings: _RoumenSettings):
		super().__init__(source, settings)
		self._roumen_settins = roumen_settings

	def scrap(self):
		ts = datetime.datetime.now()
		result = Result(self._source, ts)

		try:
			for image_to_download in self._get_images_to_download():
				# path will be like "{scrap_path}/{source}/{yyyy}/{week}/{image.jpg}"
				relative_path = pathlib.Path(self._source.value).joinpath(f"{ts:%Y}").joinpath(f"{ts:%V}")
				destination_path = self._settings.scrap_path / relative_path

				try:
					destination_path.mkdir(parents=True, exist_ok=True)
					relative_file_path = relative_path / image_to_download

					remote_file_url = f"{self._img_base}/{image_to_download}"
					# r = requests.get(remote_file_url, headers=Roumen.REQUEST_HEADERS)
					urllib.request.urlretrieve(remote_file_url, filename=str(destination_path / image_to_download))

					# write to DB
					self.write_image_info(relative_file_path, image_to_download)

					result.on_item_success(relative_file_path, remote_file_url)

				except:
					result.on_item_failure(image_to_download, "\n".join(traceback.format_exception(*sys.exc_info())))

			result.on_scrapping_finished()

		except:
			result.on_scrapping_exception("\n".join(traceback.format_exception(*sys.exc_info())))

		return result


class Roumen(BaseRoumen):
	def __init__(self, settings: Settings):
		super().__init__(Source.ROUMEN, settings, _RoumenSettings(
			base_url="https://www.rouming.cz",
			base_url_params={},
			img_base="https://www.rouming.cz/upload",
			href_needle="roumingShow.php"
		))

class RoumenMaso(BaseRoumen):
	def __init__(self, settings: Settings):
		super().__init__(Source.ROUMEN, settings, _RoumenSettings(
			base_url="https://www.roumenovomaso.cz",
			base_url_params={ "agree": "on" },
			img_base="https://www.roumenovomaso.cz/upload,
			href_needle="masoShow.php"
		))
