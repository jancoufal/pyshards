def main():
	with open("input04a.dat") as f:
		raw_records = [GuardRawRecord.from_line(l.strip()) for l in f.readlines()]

	shifts = get_guard_shifts(raw_records)

	part1(shifts)
	part2(shifts)


def part1(shifts):

	# find most sleeping guard
	sleeps = dict()
	for shift in shifts:
		if shift.guard_id not in sleeps.keys():
			sleeps[shift.guard_id] = 0
		sleeps[shift.guard_id] += shift.duration()
	max_sleeps = max(sleeps.values())
	most_sleeping_guard_id = None
	for key in sleeps.keys():
		if sleeps[key] == max_sleeps:
			most_sleeping_guard_id = key
			break
	print(f"most sleeping guard: {most_sleeping_guard_id}")

	# get minute hits
	minute_hits = {k: 0 for k in range(60)}
	for shift in shifts:
		if shift.guard_id == most_sleeping_guard_id:
			for m in shift.gen_minutes():
				minute_hits[m] += 1
	max_hits = max(minute_hits.values())
	print(f"max minute hits: {max_hits}")

	# result
	print("most sleeping minutes:")
	for k in minute_hits.keys():
		if minute_hits[k] == max_hits:
			print(f"  {k} -> result {k * most_sleeping_guard_id}")


def part2(shifts):
	guard_ids = set([gs.guard_id for gs in shifts])
	guard_max_hits = dict()
	max_guard = dict()

	for guard_id in guard_ids:
		minute_hits = {k: 0 for k in range(60)}
		for shift in shifts:
			if shift.guard_id == guard_id:
				for m in shift.gen_minutes():
					minute_hits[m] += 1

		max_hits = max(minute_hits.values())

		for k in minute_hits.keys():
			if minute_hits[k] == max_hits:
				guard_max_hits[guard_id] = (k, max_hits)
				max_guard[max_hits] = (guard_id, k)

	max_occurrence = max(max_guard.keys())

	print(f"result: {max_guard[max_occurrence][0] * max_guard[max_occurrence][1]}")


def get_guard_shifts(raw_records):
	shifts = list()
	rr_beg = None
	key = None
	for rr in sorted(raw_records):
		if isinstance(rr.action, int):
			key = rr.action
		if rr.action == "down":
			rr_beg = rr
		if rr.action == "up":
			shifts.append(GuardShift(key, rr_beg.date, rr_beg.time, rr.time))
	return shifts


class GuardRawRecord(object):

	@classmethod
	def from_line(cls, line):
		# [1518-04-05 00:00] Guard #131 begins shift
		# [1518-09-12 00:54] falls asleep
		# [1518-06-06 00:25] wakes up
		msg = line[19:]
		if msg.startswith("Guard"):
			idx1 = msg.index('#') + 1
			idx2 = msg.index(' ', idx1)
			action = int(msg[idx1:idx2])
		elif msg == "falls asleep":
			action = "down"
		elif msg == "wakes up":
			action = "up"
		else:
			raise RuntimeError(line, msg)

		return cls(
			(int(line[1:5]), int(line[6:8]), int(line[9:11])),
			(int(line[12:14]), int(line[15:17])),
			action
		)

	def __init__(self, date, time, action):
		self.date = date
		self.time = time
		self.action = action

	def __str__(self):
		date_str = f"{self.date[0]}-{self.date[1]:02d}-{self.date[2]:02d}"
		time_str = f"{self.time[0]:02d}:{self.time[1]:02d}"
		return f"[{date_str} {time_str}] {self.action}"

	def __lt__(self, other):
		date_rhs = self.date[0] * 600 + self.date[1] * 50 + self.date[2]
		date_lhs = other.date[0] * 600 + other.date[1] * 50 + other.date[2]
		if date_rhs < date_lhs:
			return True
		if date_rhs > date_lhs:
			return False

		time_rhs = self.time[0] * 24 + self.time[1]
		time_lhs = other.time[0] * 24 + other.time[1]
		if time_rhs < time_lhs:
			return True

		return False


class GuardShift(object):
	def __init__(self, guard_id, date, start, end):
		self.guard_id = guard_id
		self.date = date
		self.start = start
		self.end = end

	def __str__(self):
		date_str = f"{self.date[0]}-{self.date[1]:02d}-{self.date[2]:02d}"
		time_s_str = f"{self.start[0]:02d}:{self.start[1]:02d}"
		time_e_str = f"{self.end[0]:02d}:{self.end[1]:02d}"
		return f"#{self.guard_id:05d}: {date_str}, {time_s_str}-{time_e_str}, duration: {self.duration()}"

	def duration(self):
		return self.end[1] - self.start[1]

	def gen_minutes(self):
		for m in range(self.start[1], self.end[1]):
			yield m


if __name__ == '__main__':
	main()
