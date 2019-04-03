def main():
	with open("input05a.dat") as f:
		raw_records = [l.strip() for l in f.readlines()]

	polymer = raw_records[0]
	# polymer = "dabAcCaCBAcCcaDA"

	print("--- part 1")
	part1(polymer)

	print("--- part 2")
	part2(polymer)


def part1(polymer):
	deletions = -1
	while deletions != 0:
		deletions = 0
		new_polymer = ""
		it = bi_iter(polymer)
		for pair in it:
			if should_annihilate(*pair):
				deletions += 1
				try:
					next(it)
				except StopIteration:
					pass
			else:
				new_polymer += pair[0]
		else:
			new_polymer += pair[1]

		polymer = new_polymer

	print("result polymer:", new_polymer)
	print("result polymer len:", len(new_polymer))

	return len(new_polymer)


def part2(polymer):
	all_units = set([u.lower() for u in polymer])
	print(all_units)

	best_unit = None
	best_len = None

	for unit in all_units:
		print(f"remove unit: {unit}")
		new_polymer = "".join([u for u in polymer if u.lower() != unit])
		print(f"optimized polymer: {new_polymer}")

		new_polymer_len = part1(new_polymer)
		if best_len is None or new_polymer_len < best_len:
			best_len = new_polymer_len
			best_unit = unit

	print()
	print(f"best len: {best_len}, for '{best_unit}' unit")


def should_annihilate(lhs, rhs):
	if lhs.lower() != rhs.lower():
		return False

	if (lhs.islower() and rhs.isupper()) or (lhs.isupper() and rhs.islower()):
		return True

	return False


def bi_iter(iterable):
	it = iter(iterable)
	try:
		i1, i2 = next(it), next(it)
		while True:
			yield i1, i2
			i1, i2 = i2, next(it)
	except StopIteration:
		pass


if __name__ == '__main__':
	main()
