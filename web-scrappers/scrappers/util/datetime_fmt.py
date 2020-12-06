import datetime


def get_formatted_date_time_tuple(datetime_value=None):
	ts = datetime_value if datetime_value is not None else datetime.datetime.now()
	return f"{ts:%Y-%m-%d}", f"{ts:%H:%M.%S,%f}"


def get_formatted_date_time_week_tuple(datetime_value=None):
	ts = datetime_value if datetime_value is not None else datetime.datetime.now()
	return *get_formatted_date_time_tuple(), f"{ts:%Y-%V}"


def get_datetime_from_date_time(date_yyyy_mm_dd:str, time_hh_mm_ss_fff:str):
	return datetime.datetime.strptime(f"{date_yyyy_mm_dd} {time_hh_mm_ss_fff}", "%Y-%m-%d %H:%M.%S,%f")


def ts_diff(ts_start:datetime.datetime, ts_end:datetime.datetime):
	return td_format((ts_start - ts_end) if ts_start > ts_end else (ts_end - ts_start))


def td_format(td:datetime.timedelta):
	s = [f"{td.microseconds // 1000}ms"]
	r = td.total_seconds()
	for (period, factor) in [("s", 60), ("m", 60), ("h", 24), ("d", 7), ("w", None)]:
		if r > 0:
			r, v = divmod(r, factor) if factor is not None else (0, r)
			s.append(f"{v:.0f}{period}")
	return " ".join(s[::-1])


if __name__ == "__main__":
	print(td_format(datetime.timedelta(microseconds=123456)))
	print(td_format(datetime.timedelta(seconds=0)))
	print(td_format(datetime.timedelta(seconds=1)))
	print(td_format(datetime.timedelta(seconds=60)))
	print(td_format(datetime.timedelta(weeks=1, days=8, seconds=60)))
	dt = get_formatted_date_time_tuple()
	print(dt)
	print(get_datetime_from_date_time(*dt))
