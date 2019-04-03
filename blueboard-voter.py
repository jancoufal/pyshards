#!/bin/env python3
import logging
import urllib3
from html.parser import HTMLParser
from urllib.parse import urlparse, parse_qs
import time


settings = {
	"bb_base_url": "https://miniaplikace.blueboard.cz/anketa_0.php",
	"bb_anketa_id": "1014797",
	"logging": {
		"level": logging.INFO,
		"format": "%(asctime)s - %(levelname)s : %(message)s",
		"datefmt": "%Y-%m-%d %H:%M:%S",
	},
}

log = None


def main():

	logging.basicConfig(**settings['logging'])

	global log
	log = logging.getLogger(__name__)

	while True:
		voted = bb_voter()

		sleep_minutes = 10 if voted else 1

		log.info(f"sleeping for {sleep_minutes} minute{'s' if sleep_minutes > 1 else ''}")
		time.sleep(sleep_minutes * 60)


def bb_voter():
	http = urllib3.PoolManager()
	r = http.request("GET", f"{settings['bb_base_url']}?id={settings['bb_anketa_id']}")
	log.info(f"http status: {r.status}")

	parser = BBPollParser()
	parser.feed(r.data.decode("utf-8"))

	log.info("poll info:")
	bb_poll = parser.get_bb_poll_info()
	log.info(bb_poll["q"])

	# mark weak
	min_qty = min(item["qty"] for item in bb_poll["items"])
	bb_poll["items"] = [{**i, **{"weak": i["qty"] == min_qty}} for i in bb_poll["items"]]

	# no weak option
	weak_count = len(list(filter(lambda i: i["weak"], bb_poll["items"])))
	if weak_count == len(bb_poll["items"]):
		log.info("all answers are equal, no action required")
		return False

	vote_item = None
	for item in bb_poll["items"]:
		log.debug(item)

		# can we vote?
		flagged_item = False
		lnk_has_hash = len(parse_qs(urlparse(item["lnk"]).query).get("hash", "")) > 0
		if vote_item is None and item["weak"] and lnk_has_hash:
			vote_item = item
			flagged_item = True

		log.info("{qty:5d}x {weak} {ans} => {lnk} {flag}".format(**{**item, **{
			"weak": "w" if item["weak"] else "s",
			"flag": "*" if flagged_item else ""
		}}))

	if vote_item is None:
		log.info("cannot find suitable answer, cannot vote (voting cooldown?)")
		return False

	# vote for the weakest option
	log.info(f"voting for '{vote_item['ans']}' ({vote_item['lnk']})")
	# vr = http.request("GET", vote_item['lnk'])
	# log.info(f"vote http status: {vr.status}")
	return True


class BBPollParser(HTMLParser):
	def __init__(self):
		super(BBPollParser, self).__init__()
		self.q = dict()
		self.poll_info = dict()
		self.data_consumer = None
		self.reset_data_consumer()

	def reset_data_consumer(self):
		self.data_consumer = lambda d: None

	def get_bb_poll_info(self):
		return self.poll_info

	def handle_starttag(self, tag, attrs):
		if ("id", "otazka") in attrs:
			self.data_consumer = lambda d: self.poll_info.update({"q": d})

		if tag == "a" and "q" in self.poll_info.keys():
			self.q["lnk"] = settings['bb_base_url'] + next(filter(lambda a: a[0] == "href", attrs))[1]
			self.data_consumer = lambda d: self.q.update({"ans": d})

		if tag == "span" and ("style", "float:left") in attrs:
			self.data_consumer = lambda d: self.q.update({"qty": int(d)})

	def handle_endtag(self, tag):
		if "qty" in self.q.keys():
			if "items" not in self.poll_info.keys():
				self.poll_info["items"] = list()
			self.poll_info["items"].append(self.q)
			self.q = dict()

	def handle_data(self, data):
		self.data_consumer(str(data).strip())
		self.reset_data_consumer()


if __name__ == '__main__':
	main()
