from dataclasses import dataclass
from itertools import takewhile
import pygame

@dataclass
class Point():
	x: int
	y: int

	def as_tuple(self): return (self.x, self.y)
	def __add__(self, other): return Point(self.x + other.x, self.y + other.y)
	def __mul__(self, other): return Point(self.x * other.x, self.y * other.y)
	def __truediv__(self, other): return Point(self.x / other.x, self.y / other.y)
	def __repr__(self): return f"[{self.x},{self.y}]"


def generatePlane(screen, line_fractions: Point, edge_length: Point, starting_point: Point):
	print(f"{line_fractions=}")
	print(f"{edge_length=}")
	print(f"{starting_point=}")

	vertex_count = (line_fractions.x + 1) * (line_fractions.y + 1)
	print(f"{vertex_count=}")

	delta = edge_length / line_fractions
	print(f"{delta=}")

	vertices = []
	for x in range(line_fractions.x + 1):
		for y in range(line_fractions.y + 1):
			vertices.append(starting_point + delta * Point(x, y))
	print(f"{vertices=}")
	print(f"{len(vertices)=}")

	print("index mode: triangle strip with reset point")
	index_count = line_fractions.x * line_fractions.y * 2 + line_fractions.x - 1
	print(f"{index_count=}")
	indices = []
	reset_index = -1
	for x in range(line_fractions.x):
		for y in range(line_fractions.y + 1):
			indices.append((x + 0) * line_fractions.y + y + x + 0)
			indices.append((x + 1) * line_fractions.y + y + x + 1)
		indices.append(reset_index)
	print(f"{indices=}")
	print(f"{len(indices)=}")

	# draw with indices
	text_font = pygame.font.SysFont('Verdana', 10)
	for i, v in enumerate(vertices):
		v_text = text_font.render(str(i), True, (0, 200, 0))
		v_rect = v_text.get_rect()
		v_rect.center = v.as_tuple()
		screen.blit(v_text, v_rect)

	strips_indices = []
	split_begin = 0
	for i in indices:
		try:
			split_end = indices.index(-1, split_begin)
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

def main():
	screen = pygame.display.set_mode((500, 500))
	pygame.display.set_caption("terrain grid prototype")
	pygame.font.init()
	screen.fill((0, 0, 0))

	line_fractions = Point(5, 5)
	edge_length = Point(400, 400)
	starting_point = Point(50, 50)
	generatePlane(screen, line_fractions, edge_length, starting_point)
	pygame.display.flip()

	keep_drawing = True
	while keep_drawing:
		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
				keep_drawing = False

			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT:
					line_fractions.x = line_fractions.x + 1
				if event.key == pygame.K_RIGHT:
					line_fractions.x = line_fractions.x - 1
				if event.key == pygame.K_UP:
					line_fractions.y = line_fractions.y + 1
				if event.key == pygame.K_DOWN:
					line_fractions.y = line_fractions.y - 1

				screen.fill((0, 0, 0))
				generatePlane(screen, line_fractions, edge_length, starting_point)
				pygame.display.flip()

	print("bye")
	pygame.font.quit()
	pygame.quit()


if __name__ == "__main__":
	main()