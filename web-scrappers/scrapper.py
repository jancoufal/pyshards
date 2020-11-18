import typing
import sqlite3
from pathlib import Path
import scrappers


def main():

	scrapper_settings = scrappers.Settings(
		Path.cwd(),
		Path("static/images"),
		sqlite3.Connection("image_box.sqlite3")
	)
	scrapper = scrappers.create(scrappers.Source.ROUMEN, scrapper_settings)
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
