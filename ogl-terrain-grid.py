import sys
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple
from itertools import takewhile
from functools import reduce
from operator import add
import pygame


GL_INDEX_RESET = -1


class DrawMode(Enum):
	TRIANGLE_STRIP_WITH_RESET_POINT = auto(),
	SEPARATE_TRIANGLES = auto()


@dataclass
class Point:
	x: float
	y: float

	def as_tuple(self): return self.x, self.y
	def __add__(self, other): return Point(self.x + other.x, self.y + other.y)
	def __sub__(self, other): return Point(self.x - other.x, self.y - other.y) if isinstance(other, Point) else Point(self.x - other, self.y - other)
	def __mul__(self, other): return Point(self.x * other.x, self.y * other.y) if isinstance(other, Point) else Point(self.x * other, self.y * other)
	def __truediv__(self, other): return Point(self.x / other.x, self.y / other.y) if isinstance(other, Point) else Point(self.x / other, self.y / other)
	def __repr__(self): return f"[{self.x},{self.y}]"
	def __str__(self): return f"[{int(self.x/10)},{int(self.y/10)}]"


@dataclass
class Triangle:
	a: Point
	b: Point
	c: Point

	def as_points_closed(self):
		return self.a, self.b, self.c, self.a

	def scale(self, factor: float):
		v = self.a, self.b, self.c
		center = reduce(add, v) / len(v)
		return Triangle(*map(lambda w: center + (w - center) * factor, v))


def generate_plane(screen, line_fractions: Point, edge_length: Point, starting_point: Point, draw_mode: DrawMode):
	print(f"{line_fractions=}")
	print(f"{edge_length=}")
	print(f"{starting_point=}")

	vertex_count = (line_fractions.x + 1) * (line_fractions.y + 1)
	print(f"{vertex_count=}")

	delta = edge_length / line_fractions
	print(f"{delta=}")

	vertices = []
	for y in range(int(line_fractions.y) + 1):
		for x in range(int(line_fractions.x) + 1):
			vertices.append(starting_point + delta * Point(x, y))
	print(f"{vertices=}")
	print(f"{len(vertices)=}")

	print(f"draw mode: {draw_mode}")
	indices = []
	draw_fn = None
	match draw_mode:
		case DrawMode.TRIANGLE_STRIP_WITH_RESET_POINT:
			index_count = (line_fractions.y + 1) * line_fractions.x * 2 + line_fractions.x
			print(f"{index_count=}")
			indices = gen_indices_triangle_strip_with_reset(line_fractions)
			draw_fn = gl_draw_with_reset
		case DrawMode.SEPARATE_TRIANGLES:
			index_count = line_fractions.y * line_fractions.x * 2 * 3
			print(f"{index_count=}")
			indices = gen_indices_separate_triangles(line_fractions)
			draw_fn = gl_draw_triangles

	print(f"{indices=}")
	print(f"{len(indices)=}")

	# draw with indices
	text_font = pygame.font.SysFont('Verdana', 10)
	for i, v in enumerate(vertices):
		v_text = text_font.render(f"{i}:{v!s}", True, (0, 200, 0))
		v_rect = v_text.get_rect()
		v_rect.center = v.as_tuple()
		screen.blit(v_text, v_rect)

	draw_fn(screen, vertices, indices)


def gen_indices_triangle_strip_with_reset(line_fractions: Point) -> List[int]:
	indices = []
	for y in range(int(line_fractions.y)):
		for x in range(int(line_fractions.x) + 1):
			indices.extend((
				(y + 0) * (line_fractions.x + 1) + x,
				(y + 1) * (line_fractions.x + 1) + x,
			))
		indices.append(GL_INDEX_RESET)
	return indices


def gen_indices_separate_triangles(line_fractions: Point) -> List[int]:
	indices = []
	for y in range(int(line_fractions.y)):
		for x in range(int(line_fractions.x)):
			indices.extend((
				# upper triangle
				(y + 0) * (line_fractions.x + 1) + x + 0,
				(y + 1) * (line_fractions.x + 1) + x + 0,
				(y + 0) * (line_fractions.x + 1) + x + 1,
				# bottom triangle
				(y + 1) * (line_fractions.x + 1) + x + 0,
				(y + 1) * (line_fractions.x + 1) + x + 1,
				(y + 0) * (line_fractions.x + 1) + x + 1,
			))
	return list(map(lambda i: int(i), indices))
	# return [1, 0, 6] + [6,7,1, 2,1,7, 7,8,2]


def gl_draw_with_reset(screen, vertices: List[Point], indices: List[int]) -> None:
	strips_indices = []
	split_begin = 0
	for _ in indices:
		try:
			split_end = indices.index(GL_INDEX_RESET, split_begin)
			strips_indices.append(indices[split_begin:split_end])
			split_begin = split_end + 1
		except ValueError:
			break
	print(f"{strips_indices=}")

	delta = 200 / len(strips_indices)
	c = [255, 0, 0]
	for strip_indices in strips_indices:
		c[1] = c[1] + delta
		pygame.draw.lines(screen, c, False, [vertices[i].as_tuple() for i in strip_indices])


def gl_draw_triangles(screen, vertices: List[Point], indices: List[int]) -> None:
	c = [0, 0, 255]
	errors = dict()
	for i in range(0, len(indices), 3):
		try:
			t = Triangle(*map(lambda j: vertices[j], indices[i:i+3]))
			t = t.scale(0.8)
			pygame.draw.lines(screen, c, False, [p.as_tuple() for p in t.as_points_closed()])
		except IndexError as e:
			str_e = str(e)
			if str_e not in errors.keys():
				errors[str_e] = 0
			errors[str_e] = errors[str_e] + 1
	for error in errors:
		print(f"{error} (x{errors[error]})", file=sys.stderr)


def main():
	screen = pygame.display.set_mode((500, 500))
	pygame.display.set_caption("terrain grid prototype")
	pygame.font.init()

	line_fractions = Point(5, 5)
	edge_length = Point(400, 400)
	starting_point = Point(50, 50)
	draw_mode = DrawMode.TRIANGLE_STRIP_WITH_RESET_POINT

	keep_looping = True
	do_draw = True
	while keep_looping:
		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
				keep_looping = False

			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT:
					line_fractions.x = line_fractions.x + 1
				if event.key == pygame.K_RIGHT:
					line_fractions.x = line_fractions.x - 1
				if event.key == pygame.K_UP:
					line_fractions.y = line_fractions.y + 1
				if event.key == pygame.K_DOWN:
					line_fractions.y = line_fractions.y - 1
				if event.key == pygame.K_m:
					draw_mode = DrawMode.SEPARATE_TRIANGLES if draw_mode == DrawMode.TRIANGLE_STRIP_WITH_RESET_POINT else DrawMode.TRIANGLE_STRIP_WITH_RESET_POINT

				do_draw = True

		if do_draw:
			errors = dict()
			try:
				print(f"{draw_mode=}")
				screen.fill((0, 0, 0))
				generate_plane(screen, line_fractions, edge_length, starting_point, draw_mode)
				pygame.display.flip()
			except Exception as e:
				keep_looping = not isinstance(e, KeyboardInterrupt)
				str_e = str(e)
				if str_e not in errors:
					errors[str_e] = 0
				errors[str_e] = errors[str_e] + 1

			for str_e in errors:
				print(f"{str_e} (x{errors[str_e]})", file=sys.stderr)

			do_draw = False

	print("bye")
	pygame.font.quit()
	pygame.quit()


if __name__ == "__main__":
	main()