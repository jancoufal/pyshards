import re


def main():
	with open("input03a.dat") as fh:
		claims = [Claim.from_line(l.strip()) for l in fh.readlines()]

	part1(claims)
	part2(claims)


def part1(claims):
	fabric = dict()
	for c in claims:
		for f in c.gen_indexes():
			if f not in fabric.keys():
				fabric[f] = 0
			fabric[f] += 1

	overlays = 0
	for f in fabric.keys():
		if fabric[f] > 1:
			overlays += 1

	print(f"overlays: {overlays}")


def part2(claims):
	collisions = set()

	for i1, c1 in enumerate(claims[0:-1]):
		for c2 in claims[(i1+1):]:
			if c1.in_collision_with(c2):
				collisions.add(c1)
				collisions.add(c2)

	non_collisions = claims[:]
	for c in collisions:
		non_collisions.remove(c)

	print("non-collision items:")
	for nc in non_collisions:
		print(nc)


class Claim(object):

	# "#1 @ 16,576: 17x14"
	line_re = re.compile(r"^#(?P<id>\d+) \@ (?P<x>\d+)\,(?P<y>\d+)\: (?P<w>\d+)x(?P<h>\d+)$")

	@classmethod
	def from_line(cls, line):
		re_search = Claim.line_re.search(line)

		return Claim(
			int(re_search.group('id')),
			int(re_search.group('x')),
			int(re_search.group('y')),
			int(re_search.group('w')),
			int(re_search.group('h'))
		)

	def __init__(self, claim_id, x, y, w, h):
		self.claim_id = claim_id
		self.x = x
		self.y = y
		self.w = w
		self.h = h

	def __str__(self):
		return f"#{self.claim_id} @ {self.x},{self.y}: {self.w}x{self.h}"

	def gen_indexes(self):
		for x in range(self.x, self.x + self.w):
			for y in range(self.y, self.y + self.h):
				yield f"{x}x{y}"

	def in_collision_with(self, other):
		return \
			self.x < other.x + other.w and \
			self.x + self.w > other.x and \
			self.y < other.y + other.h and \
			self.h + self.y > other.y


if __name__ == "__main__":
	main()
