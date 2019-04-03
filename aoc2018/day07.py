from collections import defaultdict
from itertools import chain


def main():
	with open("input07a.dat") as f:
		pairs = [(l.strip()[5], l.strip()[36]) for l in f.readlines()]

	graph = defaultdict(lambda: list())
	for pair in pairs:
		graph[pair[0]].append(pair[1])

	graph = dict(graph)

	scan_graph(graph, get_roots(graph))
	print()

	# while roots != set():
	# 	print(f"roots: {roots}")
	# 	next_roots = list()
	# 	for root in roots:
	# 		next_roots += graph[root]
	#
	# 	print(next_roots)
	# 	break
	# 	roots = get_roots(graph)


def scan_graph(graph, roots, indent=0):
	def prn(msg):
		# print("\t" * indent + msg)
		pass

	prn("")
	prn(f"graph: {graph}")
	prn(f"roots: {roots}")
	for root in sorted(roots):

		# print(root, end='')

		prn(f"root: {root}")
		print(root, end="")
		nr = set(graph.pop(root, set()))
		prn(f"  ..: {nr}")

		# throw away that "new roots" that are still used in the graph
		nr -= set(chain(*graph.values()))
		prn(f"  ->: {nr}")

		scan_graph(graph, nr, indent+1)


def get_roots(graph):
	return set(graph.keys()) - set(chain(*graph.values()))


if __name__ == '__main__':
	main()
