import itertools


def main():
	# knobs
	for k1, k2, k3, k4 in itertools.product(range(0, 141, 20), repeat=4):
		if (k1 + k3 + k4) == 220 and (k3 + k4) == 140 and (k1 + k2) == 200 and (k2 + k4) == 160:
			print(f"{k1}, {k2}, {k3}, {k4}")
			break
	else:
		print("nothing found :(")


if __name__ == "__main__":
	main()
