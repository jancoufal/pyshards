import typing
import sqlite3
from pathlib import Path
import scrappers


def main():

	sql_conn = sqlite3.Connection("image_box.sqlite3")
	# sqlite_install(sql_conn)

	# TODO: invoke all scrappers (except NOOP)...

	scrapper_settings = scrappers.Settings(
		local_base_path=Path.cwd(),
		local_relative_path=Path("static/images"),
		sql_connection=sql_conn
		)

	scrapper = scrappers.create(
		source=scrappers.Source.ROUMEN_MASO,
		settings=scrapper_settings
		)

	scrap_result = scrapper.scrap()

	sql_conn.close()

	print(scrap_result)


def sqlite_install(conn: sqlite3.Connection):
	c = conn.cursor()
	# c.execute("drop table image_box")
	c.execute("""create table if not exists
	image_box(
		source text,
		ts_date text,
		ts_week text,
		ts_time text,
		local_path text,
		name text,
		impressions integer
	);""")
	c.close()


if __name__ == "__main__":
	main()
