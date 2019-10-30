# https://www.youtube.com/watch?v=zGv3hOORxh0

import pygame
import random
from enum import Enum


def main():
	pygame.init()
	pygame.display.set_caption("rectangle overlapping")

	screen_rect = pygame.Rect(0, 0, 1010, 1010)
	screen = pygame.display.set_mode(screen_rect.size)

	boundaries = (-500, -500, 500, 500)
	translate_xy = screen_rect.width // 2, screen_rect.height // 2

	done = False
	draw = True
	while not done:

		if draw:
			draw = False

			r1 = get_random_rect(*boundaries)
			r2 = get_random_rect(*boundaries)
			r3 = get_overlapped_rect(r1, r2)

			# convert to pygame rects
			r1 = r1.get_pygame_rect().move(translate_xy)
			r2 = r2.get_pygame_rect().move(translate_xy)
			r3 = r3.get_pygame_rect().move(translate_xy)

			screen.fill(ColorEnum.BACKGROUND.color)

			if r3 is not None:
				pygame.draw.rect(screen, ColorEnum.RECT_C.color, r3)

			pygame.draw.rect(screen, ColorEnum.RECT_A.color, r1, 1)
			pygame.draw.rect(screen, ColorEnum.RECT_B.color, r2, 1)

			pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.unicode == 'q'):
				done = True

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_RETURN:
					draw = True


def get_random_rect(x_min, y_min, x_max, y_max):
	x = sorted((random.randint(x_min, x_max), random.randint(x_min, x_max)))
	y = sorted((random.randint(y_min, y_max), random.randint(y_min, y_max)))
	return MyRect(*(*x, *y))


def get_overlapped_rect(r1, r2):
	return MyRect(
		min(r1.p1.x, r2.p1.x),
		min(r1.p2.y, r2.p1.y),
		max(r1.p1.x, r2.p1.x),
		max(r1.p2.y, r2.p1.y)
	)


class MyPoint(object):
	def __init__(self, x, y):
		self._x = x
		self._y = y

	@property
	def x(self): return self._x

	@property
	def y(self): return self._y

	@property
	def xy(self): return self.x, self.y

class MyRect(object):
	def __init__(self, x1, y1, x2, y2):
		self._p1 = MyPoint(x1, y1)
		self._p2 = MyPoint(x2, y2)

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


class ColorEnum(Enum):
	BACKGROUND = pygame.color.Color("#00000000")
	RECT_A = pygame.color.Color("#ff8800")
	RECT_B = pygame.color.Color("#0088ff")
	RECT_C = pygame.color.Color("#00ff88")
	AXIS_X = pygame.color.Color("#cccccc")
	AXIS_Y = pygame.color.Color("#cccccc")

	def __init__(self, color):
		self._color = color

	@property
	def color(self):
		return self._color


if __name__ == '__main__':
	main()
