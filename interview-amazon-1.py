# https://www.youtube.com/watch?v=zGv3hOORxh0

import pygame
import random
from enum import Enum


def main():
	pygame.init()
	pygame.display.set_caption("rectangle overlapping")

	screen_rect = pygame.Rect(0, 0, 1010, 1010)
	screen = pygame.display.set_mode(screen_rect.size)

	boundaries = (-500 * 0, -500 * 0, 500, 500)
	translate_by = MyPoint(screen_rect.width // 2, screen_rect.height // 2)

	done = False
	draw = True
	while not done:

		if draw:
			draw = False

			r1 = get_random_rect(*boundaries, ColorEnum.RECT_ORANGE)
			r2 = get_random_rect(*boundaries, ColorEnum.RECT_BLUE)
			r3 = get_overlapped_rect(r1, r2, ColorEnum.RECT_GREEN)

			print(f"{r1}, {r2}, {r3}")

			# map to viewport
			r1 = r1.move(*translate_by.xy)
			r2 = r2.move(*translate_by.xy)
			r3 = r3.move(*translate_by.xy)

			screen.fill(ColorEnum.BACKGROUND.color)

			if r3 is not None:
				draw_rect(screen, r3, width=0)
			draw_rect(screen, r1)
			draw_rect(screen, r2)

			draw_axes(screen, translate_by)

			pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.unicode == 'q'):
				done = True

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN:
					draw = True


def draw_rect(surface, my_rect, width=1):
	pygame.draw.rect(surface, my_rect.color.color, my_rect.get_pygame_rect(), width)
	pygame.draw.circle(surface, my_rect.color.color, my_rect.p1.xy, 3, 1)


def draw_axes(surface, translate):
	pygame.draw.line(
		surface,
		ColorEnum.AXIS_X.color,
		(0, translate.y),
		(surface.get_height(), translate.y)
	)
	pygame.draw.line(
		surface,
		ColorEnum.AXIS_X.color,
		(translate.x, 0),
		(translate.x, surface.get_width())
	)


def get_random_rect(x_min, y_min, x_max, y_max, color_enum):
	x = sorted((random.randint(x_min, x_max), random.randint(x_min, x_max)))
	y = sorted((random.randint(y_min, y_max), random.randint(y_min, y_max)))
	return MyRect(x[0], y[0], x[1], y[1], color_enum)


def get_overlapped_rect(r1, r2, color_enum):
	return MyRect(
		min(r1.p1.x, r2.p1.x),
		min(r1.p2.y, r2.p1.y),
		max(r1.p1.x, r2.p1.x),
		max(r1.p2.y, r2.p1.y),
		color_enum
	)


class MyPoint(object):
	def __init__(self, x, y):
		self._x = x
		self._y = y

	def __str__(self):
		return f"point({self.x}, {self.y})"

	@property
	def x(self): return self._x

	@property
	def y(self): return self._y

	@property
	def xy(self): return self.x, self.y

	def move(self, x, y):
		return MyPoint(self.x + x, self.y + y)


class MyRect(object):
	def __init__(self, x1, y1, x2, y2, color_enum):
		self._clr = color_enum
		self._p1 = MyPoint(x1, y1)
		self._p2 = MyPoint(x2, y2)
		self._normalize_points()

	@classmethod
	def from_points(cls, p1, p2, color_enum):
		return cls(*(*p1.xy, *p2.xy, color_enum))

	def __str__(self):
		return f"rectangle({self.p1}, {self.p2}, {self.color})"

	def _normalize_points(self):
		p1 = MyPoint(min(self.p1.x, self.p2.x), min(self.p1.y, self.p2.y))
		p2 = MyPoint(max(self.p1.x, self.p2.x), max(self.p1.y, self.p2.y))
		self._p1, self._p2 = p1, p2

	def get_pygame_rect(self):
		return pygame.Rect(
			min(self.p1.x, self.p2.x),
			min(self.p1.y, self.p2.y),
			abs(self.p1.x - self.p2.x),
			abs(self.p1.y - self.p2.y)
		)

	@property
	def p1(self): return self._p1

	@property
	def p2(self): return self._p2

	@property
	def color(self): return self._clr

	def move(self, x, y):
		return MyRect.from_points(self._p1.move(x, y), self._p2.move(x, y), self.color)


class ColorEnum(Enum):
	BACKGROUND = pygame.color.Color("#00000000")
	RECT_ORANGE = pygame.color.Color("#ff8800")
	RECT_BLUE = pygame.color.Color("#0088ff")
	RECT_GREEN = pygame.color.Color("#00ff88")
	AXIS_X = pygame.color.Color("#cccccc")
	AXIS_Y = pygame.color.Color("#cccccc")

	def __init__(self, color):
		self._color = color

	@property
	def color(self):
		return self._color


if __name__ == '__main__':
	main()
