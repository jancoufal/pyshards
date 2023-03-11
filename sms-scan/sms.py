import xml.etree.ElementTree as et
from datetime import datetime
from collections import defaultdict


def main():
	counts = defaultdict(int)
	for sms in et.parse("sms.xml").findall("sms"):
		ts = datetime.fromtimestamp(int(sms.get("date")) / 1000.0)
		ts_key = datetime.strftime(ts, "%Y-%m")
		counts[ts_key] += 1

	metrics = {
		"min": (1e9, ""),	# count, month
		"max": (0, ""),
		"avg": None,
		"total": 0,
	}
	for k in sorted(counts.keys()):
		n = counts[k]
		print(f"{k} => {n:3d}")

		metrics["total"] += n

		if n < metrics["min"][0]:
			metrics["min"] = (n, k)

		if n > metrics["max"][0]:
			metrics["max"] = (n, k)

	metrics["avg"] = metrics["total"] / len(counts)
		
	print(metrics)


if __name__ == "__main__":
	main()
