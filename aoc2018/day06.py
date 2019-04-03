from copy import deepcopy

DMZ_KEY = 9999
EDGE_KEY = 8888
SAFE_ZONE = 7777
LOOP_ZONE = 6666


def main():
	with open("input06a.dat") as f:
		coords = [Coord.from_line(i+1, l) for (i, l) in enumerate(f.readlines())]

	grid = Grid.from_coords(coords)

	print("part 1")
	part1(coords, deepcopy(grid))

	print("part 2")
	part2(coords, deepcopy(grid))


def part1(coords, grid):
	# fill DMZ (borders)
	for coord in grid.gen_all_coords():
		near_count = get_nearest(coord, coords)
		if len(near_count) == 1:
			grid.put_value(near_count[0].idx, coord)
		else:
			grid.put_value(DMZ_KEY, coord)

	# find "infinite" zones
	infinite_keys = set()
	infinite_keys |= set(
		[grid.get_value(Coord(EDGE_KEY, edge, grid.c_min.y)) for edge in range(grid.c_min.x, grid.c_max.x + 1)])
	infinite_keys |= set(
		[grid.get_value(Coord(EDGE_KEY, edge, grid.c_max.y)) for edge in range(grid.c_min.x, grid.c_max.x + 1)])
	infinite_keys |= set(
		[grid.get_value(Coord(EDGE_KEY, grid.c_min.x, edge)) for edge in range(grid.c_min.x, grid.c_max.y + 1)])
	infinite_keys |= set(
		[grid.get_value(Coord(EDGE_KEY, grid.c_max.x, edge)) for edge in range(grid.c_min.x, grid.c_max.y + 1)])

	# infinite_keys -= {DMZ_KEY, BORDER_KEY}
	# print(f"infinite_keys: {infinite_keys}")
	# get zone sizes
	results = dict()
	for coord in grid.gen_all_coords():
		val = grid.get_value(coord)
		if val not in infinite_keys:
			if val not in results.keys():
				results[val] = 0
			results[val] += 1

	# print(grid)
	# print(results)
	print(f"largest zone: {max(results.values())}")


def part2(coords, grid):
	coord_count = 0
	for grid_coord in grid.gen_all_coords():
		if sum(grid_coord.manhattan_distance(coord) for coord in coords) < 10000:
			coord_count += 1
	print(f"safe zone size: {coord_count}")


class Coord(object):
	@classmethod
	def from_line(cls, idx, line):
		c = line.strip().split(',')
		return cls(idx, int(c[0]), int(c[1].strip()))

	def __init__(self, idx, x, y):
		self.idx = idx
		self.x, self.y = x, y

	def __str__(self):
		return f"Coord(#{self.idx}, x: {self.x}, y: {self.y})"

	def manhattan_distance(self, other):
		return abs(self.x - other.x) + abs(self.y - other.y)


class Grid(object):
	@classmethod
	def from_coords(cls, coords):
		x_list = [c.x for c in coords]
		y_list = [c.y for c in coords]

		return cls(
			Coord(EDGE_KEY, min(x_list) - 1, min(y_list) - 1),
			Coord(EDGE_KEY, max(x_list) + 1, max(y_list) + 1),
			coords
		)

	def __init__(self, c_min, c_max, coords):
		self.c_min = c_min
		self.c_max = c_max
		self._grid = [[0 for _ in range(self.c_max.x+1)] for _ in range(self.c_max.y+1)]

		for coord in coords:
			self.put_base_coord(coord)

	def __str__(self):
		s = f"Grid [{self.c_min} -> [{self.c_max}]:"
		for r in self._grid:
			s += "\n" + " ".join([f"{i:4d}" for i in r])
		return s

	def put_base_coord(self, coord):
		return self.put_value(-1-coord.idx, coord)

	def put_value(self, idx, coord):
		self._grid[coord.y][coord.x] = idx

	def get_value(self, coord):
		return self._grid[coord.y][coord.x]

	def gen_all_coords(self):
		for y in range(self.c_min.y, self.c_max.y + 1):
			for x in range(self.c_min.x, self.c_max.x + 1):
				yield Coord(LOOP_ZONE, x, y)


def get_distance_map(test_coord, coords):
	distances = dict()
	for coord in coords:
		distance = test_coord.manhattan_distance(coord)
		# print(f"{test_coord} to {coord} is {distance}")
		if distance not in distances.keys():
			distances[distance] = list()
		distances[distance].append(coord)
	return distances


def get_nearest(test_coord, coords):
	distances = get_distance_map(test_coord, coords)
	return distances[min(distances.keys())]


if __name__ == '__main__':
	main()
