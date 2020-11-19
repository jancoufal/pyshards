import sqlite3

def install(sql_connection: sqlite3.Connection):

	c = sql_connection.cursor()
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
