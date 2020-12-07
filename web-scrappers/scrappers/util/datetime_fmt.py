import datetime


def get_formatted_date_time(datetime_value=None):
	return " ".join(get_formatted_date_time_tuple(datetime_value))


def get_formatted_date_time_tuple(datetime_value=None, include_ms=True):
	ts = datetime_value if datetime_value is not None else datetime.datetime.now()
	return (f"{ts:%Y-%m-%d}", f"{ts:%H:%M.%S,%f}") if include_ms else (f"{ts:%Y-%m-%d}", f"{ts:%H:%M.%S}")


def get_formatted_date_time_week_tuple(datetime_value=None, include_ms=True):
	ts = datetime_value if datetime_value is not None else datetime.datetime.now()
	return *get_formatted_date_time_tuple(ts, include_ms), f"{ts:%Y-%V}"


def get_datetime_from_date_time(date_yyyy_mm_dd:str, time_hh_mm_ss_fff:str, include_ms=True):
	fmt = "%Y-%m-%d %H:%M.%S"
	if include_ms:
		fmt += ",%f"
	return datetime.datetime.strptime(f"{date_yyyy_mm_dd} {time_hh_mm_ss_fff}", fmt)


def get_datetime_for_print_from_date_time(dt:datetime.datetime):
	return f"{dt:%Y-%m-%d %H:%M.%S}"


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
