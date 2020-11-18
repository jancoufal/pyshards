import datetime
import os
import typing
import requests
import urllib
import bs4
import sqlite3


SETTINGS = {
	"kecy": {
		"base_url": "https://www.rouming.cz",
		"base_params": {},
		"img_base": "https://www.rouming.cz/upload/",
	}
}


def main():
	# image_names = get_image_names(**SETTINGS["kecy"])
	# print(image_names)
	# sqlite3.connect

	conn = sqlite3.Connection("image_box.sqlite3")
	sqlite_install(conn)
	sqlite_test_write(conn)
	print(get_last_images(conn))

	# urllib.request.urlretrieve("http://www.digimouth.com/news/media/2011/09/google-logo.jpg", "local-filename.jpg")

	r = requests.Request("GET", "https://www.rouming.cz/upload/les_a_hara.jpg", params={"a": "a b", "b": "c  d"}).prepare()
	
	os.makedirs("static/image/2020/11/", exist_ok=True)
	urllib.request.urlretrieve(r.url, filename="static/image/2020/11/les_a_hara.jpg")


def make_url(base_url, path_parts=None, query_params=None):
	url = base_url
	if path_parts is not None:
		url += "/" + "/".join(path_parts)
	if query_params is not None:
		url += "?" + urllib.parse.urlencode(query_params)
	return url


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

def sqlite_test_write(conn: sqlite3.Connection):
	c = conn.cursor()
	for r in range(15):
		ts = datetime.datetime.now()
		img_name = f"image_name{r}.png"
		img_data = {
			"source": "roumen",
			"ts_date": f"{ts:%Y-%m-%d}",
			"ts_time": f"{ts:%H:%M.%S,%f}",
			"local_path": os.path.join("images", f"{ts:%Y}", f"{ts:%m}", img_name),
			"name": img_name,
			"impressions": 0,
		}
		c.execute("insert into image_box(source, ts_date, ts_time, local_path, name, impressions) values (:source, :ts_date, :ts_time, :local_path, :name, :impressions)", img_data)
		conn.commit()
	c.close()

def get_last_images(conn: sqlite3.Connection):
	c = conn.cursor()
	cur = c.execute("select distinct name from image_box where source=? and ts_date > date('now', '-5 days')", ("roumen", ))
	return set(row[0] for row in cur.fetchall())

def get_image_names(base_url, base_params=None, *args, **kwargs):
	r = requests.get(base_url, params=base_params)
	soup = bs4.BeautifulSoup(r.content.decode(r.apparent_encoding), features="html.parser")

	# extract all "a" tags with have "roumingShow.php" present in the "href"
	all_urls = map(lambda a: urllib.parse.urlparse(a.get("href")), soup.find_all("a"))
	all_show = [url for url in all_urls if "roumingShow.php" in url.path]

	# extract all "file" values from the query string
	all_qstr = [urllib.parse.parse_qs(url.query) for url in all_show]
	all_imgs = [qs.get("file").pop() for qs in all_qstr if "file" in qs]

	return all_imgs

if __name__ == "__main__":
	main()
