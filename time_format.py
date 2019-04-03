#!/bin/env python3.6

import math


def time_diff_format(seconds):
	# milliseconds & seconds
	millis, secs = math.modf(seconds)

	# rounded >=0.9995 seconds is not 999ms, but 1 extra second
	extra, millis = divmod(round(millis * 1000), 1000)
	secs += extra

	# factors for (week, day, hour, minute, second)
	time_factors = (604800, 86400, 3600, 60, 1)
	time_parts = []

	for tf in time_factors:
		g = int(secs) // tf
		time_parts.append(g)
		secs -= g * tf
	time_parts.append(millis)

	time_fmts = ('%dw ', '%dd ', '%dh ', '%dm ', '%ds ', '%dms')

	time_formatted = ''
	for z in zip(time_parts, time_fmts):
		if z[0] > 0 or len(time_formatted) > 0:
			time_formatted += z[1] % z[0]

	# zero milliseconds
	if len(time_formatted) == 0:
		time_formatted = time_fmts[-1] % 0

	return time_formatted


if __name__ == '__main__':

	tests = (
		# milliseconds
		0,
		0.123456,
		0.999999,
		# seconds
		12.34567,
		59.99999,
		# minutes
		60,
		60.0001,
		61,
		2 * 60 - 1,
		2 * 60,
		2 * 60 + 1.0001,
		# hours
		60 * 60 - 1.23456,
		60 * 60,
		60 * 60 + 1.23456,
		2 * 60 * 60 - 1.23456,
		2 * 60 * 60,
		2 * 60 * 60 + 1.23456,
		# days
		1 * 24 * 60 * 60 - 1.23456,
		1 * 24 * 60 * 60,
		1 * 24 * 60 * 60 + 1.23456,
		2 * 24 * 60 * 60 - 1.23456,
		2 * 24 * 60 * 60,
		2 * 24 * 60 * 60 + 1.23456,
		# weeks
		7 * 24 * 60 * 60 - 1.23456,
		7 * 24 * 60 * 60,
		7 * 24 * 60 * 60 + 1.23456,
		14 * 24 * 60 * 60 - 1.23456,
		14 * 24 * 60 * 60,
		14 * 24 * 60 * 60 + 1.23456,
		# extra
		14 * 24 * 60 * 60 +  # 2w
		3 * 24 * 60 * 60 +  # 3d
		12 * 60 * 60 +  # 12h
		34 * 60 +  # 34m
		56 +  # 56s
		0.7899  # 790ms

	)

	for t in tests:
		print('%f: %s' % (t, time_diff_format(t)))
