from flask import Flask, url_for, render_template, request
import sys, typing, traceback
import random
import sqlite3
from pathlib import Path
import scrappers


SETTINGS = {
	"flask": {
		"host": "localhost",
		"port": 5000,
		"debug": True,
	},
	"sqlite3": {
		"datafile": "image_box.sqlite3",
	},
	"scrap": {
		"auth-key": "wewewe",
		"auth-error-messages": [
			"You don't know the auth key. Do not mess with me!",
			"Stop it! That's not the valid auth key.",
			"You are wrong. I'm going to tell my dad, sucker.",
			"Auth key valid... meh, just kiddin'. You don't know it, do you?",
			"Why are you even trying, when you know that you don't konw the auth key?",
			"Oh gosh, you failed so bad. I won't do anything for you.",
			"Murder, death, kill. Murder, death, kill! Attention, attention. Calling 911.",
			"I know what are you trying to do and it doesn't work. You screw it.",
			"Feeling like a hacker? Try another auth key, but be gentle.",
			"I feel sorry for you. You've tried some auth key and it does nothing.",
		],
	},

}

app = Flask(__name__)
app.debug = SETTINGS["flask"]["debug"]


def get_page_data(page_values: dict=None):
	HTML_ENTITY_SYMBOL_HOME = "&#x2302;"
	HTML_ENTITY_SYMBOL_RELOAD = "&#x21bb;"

	page_data = {
		"title": "compressor",
		"head": {
			"less": url_for("static", filename="site.less"),
		},
		"current": {
			"endpoint": None if request.endpoint is None else url_for(request.endpoint, **page_values if page_values is not None else {}),
			"image_dir": url_for("static", filename="images") + "/",
			"debug": SETTINGS["flask"]["debug"],
		},
		"links": {
			"griffin": url_for("page_griffin"),
		},
		"navigation": [
			{ "name": HTML_ENTITY_SYMBOL_HOME, "href": url_for("page_index"), },
			{ "name": HTML_ENTITY_SYMBOL_RELOAD, "href": url_for("page_scrap"), },
		]
	}

	for s in scrappers.Source:
		if s is not scrappers.Source.NOOP:
			page_data["navigation"].append({"name":s.value, "href":url_for("page_view", source=s.value)})

	return page_data


@app.route("/")
def page_index():
	return render_template("home.html", page_data=get_page_data())


@app.route("/griffin/")
def page_griffin():
	return render_template("griffin.html", page_data=get_page_data())


@app.route("/scrap/", methods=["GET"])
def page_scrap():
	page_data = get_page_data()
	page_data["request"] = {
		"method": request.method,
		"args": request.args,
		"form": request.form,
	}

	if request.method == "GET" and "auth-key" in request.args.keys():
		if SETTINGS["scrap"]["auth-key"] == request.args.get("auth-key"):
			page_data["scrapper_results"] = {s: scrap(s) for s in scrappers.Source if s is not scrappers.Source.NOOP}
		else:
			page_data["auth_error"] = {
				"title": "Authentication error",
				"message": random.choice(SETTINGS["scrap"]["auth-error-messages"]),
			}

	return render_template("scrap.html", page_data=page_data)


@app.route("/view/<source>/")
def page_view(source):
	page_data = get_page_data({"source": source})
	try:
		page_data["images"] = load_images_data(source, {}, 100)
		return render_template("view.html", page_data=page_data)
	except:
		# TODO: redirect to error page
		e = sys.exc_info()
		page_data["exception"] = {
			"endpoint": page_data["current"]["endpoint"],
			"type": e[0],
			"value": e[1],
			"traceback": traceback.format_tb(e[2]),
		}
		return render_template("exception.html", page_data=page_data)


@app.errorhandler(404)
def page_not_found(e):
	page_data = get_page_data()
	page_data["error"] = {
		"code": e.code,
		"name": e.name,
		"description": e.description,
	}
	# note that we set the 404 status explicitly
	return render_template('error.html', page_data=page_data), 404


def load_images_data(source: str, sql_filter_map: dict=None, sql_limit: int=None):
	cols = [ "source", "ts_date", "ts_time", "name", "local_path", "impressions" ]

	filter_map = { "source": source }
	if sql_filter_map is not None:
		filter_map.update(sql_filter_map)

	return load_records_from_db_simple(
		"image_box",
		cols,
		filter_map,
		[("ts_date", "desc"), ("ts_time", "desc")],
		sql_limit,
		lambda row: { c:row[i] for i, c in enumerate(cols) }
	)


def load_records_from_db_simple(source_table:str, column_list:list, filter_map:dict, order_tuple_list:tuple, limit:int, row_mapper:callable=None):
	stmt = f"select {', '.join(column_list)} from {source_table}"

	if filter_map is not None and len(filter_map) > 0:
		stmt += " where " + " and ".join(f"{k}=:{k}" for k in filter_map.keys())

	if order_tuple_list is not None and len(order_tuple_list) > 0:
		stmt += " order by " + ", ".join(f"{_1} {_2}" for (_1, _2) in order_tuple_list)

	# clamp to 1..100 range or default 10
	stmt += " limit " + str(max(1, min(100, limit)) if isinstance(limit, int) else 10)

	r_mapper = row_mapper if row_mapper is not None else lambda row: row

	try:
		result = list()
		sql_conn = sqlite3.Connection(SETTINGS["sqlite3"]["datafile"])
		c = sql_conn.cursor()
		for r in c.execute(stmt, filter_map):
			result.append(r_mapper(r))
		return result
	finally:
		c.close()


def fake_scrap(scrapper_source: scrappers.Source):
	r = scrappers.result.Result(scrapper_source)

	for i in range(5):
		r.on_item(scrappers.result.ResultItem.createSucceeded(
			f"relative_path_{i}",
			f"remote_url_{i}"
			))

	for i in range(5):
		try:
			raise KeyError("test item exception")
		except:
			r.on_item(scrappers.result.ResultItem.createFailedWithLastException(f"image_name_{i}"))

	if scrapper_source == scrappers.Source.ROUMEN_MASO:
		try:
			raise KeyError("test scrapper exception")
		except:
			r.on_scrapping_exception(scrappers.result.ExceptionInfo.createFromLastException())

	r.on_scrapping_finished()

	return r


def scrap(scrapper_source: scrappers.Source):
	sql_conn = sqlite3.Connection(SETTINGS["sqlite3"]["datafile"])

	scrapper_settings = scrappers.Settings(
		local_base_path=Path.cwd(),
		local_relative_path=Path("static").joinpath("images"),
		sql_connection=sql_conn
		)

	scrapper = scrappers.create(
		source=scrapper_source,
		settings=scrapper_settings
		)

	scrap_result = scrapper.scrap()
	sql_conn.close()
	return scrap_result


if __name__ == "__main__":
	app.run(**SETTINGS["flask"])
