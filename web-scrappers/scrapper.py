import datetime
import os
import typing
import requests
import urllib
import bs4
import sqlite3
from pathlib import Path
from scrapper_enum import ScrapSource
from scrapper_factory import create_scrapper
from scrapper_holders import ScrapperSettings


def main():
	scrapper_settings = ScrapperSettings(
		Path.cwd(),
		Path("static/images"),
		sqlite3.Connection("image_box.sqlite3")
	)
	scrapper = create_scrapper(ScrapSource.ROUMEN, scrapper_settings)
	scrap_result = scrapper.scrap()
	print(scrap_result)


def sqlite_install(conn: sqlite3.Connection):
	c = conn.cursor()
	c.execute("drop table image_box")
	c.execute("""create table
	image_box(
		source text,
		ts_date text,
		ts_time text,
		local_path text,
		name text,
		impressions integer
	);""")
	c.close()


if __name__ == "__main__":
	main()
