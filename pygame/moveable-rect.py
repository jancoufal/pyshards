import pygame


def main():
	pygame.init()
	pygame.display.set_caption("minimal program")

	screen_rect = pygame.Rect(0, 0, 500, 500)
	screen = pygame.display.set_mode(screen_rect.size)

	car_size = Vector2d(49, 90)
	car_surf = pygame.Surface(car_size.xy)
	car_surf.fill(pygame.Color("#cc000000"))
	for y, x in enumerate(range(0, car_size.x // 2)):
		car_surf.set_at((car_size.x // 2 + x, car_size.y - y), pygame.Color("#ffffff"))
		car_surf.set_at((car_size.x // 2 - x, car_size.y - y), pygame.Color("#ffffff"))

	car_loc = OrientedPoint2D(
		position=Vector2d(*screen_rect.center),
		direction=Vector2d(0, 5),
	)

	key_down_event = {
		pygame.K_UP: OrientedPoint2D.forward,
		pygame.K_DOWN: OrientedPoint2D.backward,
		# pygame.K_LEFT: lambda pos: (pos[0] - car_speed, pos[1]),
		# pygame.K_RIGHT: lambda pos: (pos[0] + car_speed, pos[1]),
	}

	print(key_down_event)

	while True:
		for event in pygame.event.get():

			screen.blit(car_surf, car_loc.position.xy)

			pygame.display.update()

			print(event)

			if event.type == pygame.KEYDOWN and event.key in key_down_event.keys():
				key_down_event[event.key](car_loc)

			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.unicode == 'q'):
				return


class Vector2d(object):
	def __init__(self, x, y):
		self._x, self._y = x, y

	@property
	def x(self):
		return self._x

	@property
	def y(self):
		return self._y

	@property
	def xy(self):
		return self.x, self.y

	def __add__(self, other):
		return Vector2d(self.x + other.x, self.y + other.y)

	def __sub__(self, other):
		return Vector2d(self.x - other.x, self.y - other.y)


class OrientedPoint2D(object):
	def __init__(self, position=Vector2d(0, 0), direction=Vector2d(1, 0)):
		self._pos = position
		self._dir = direction

	@property
	def position(self):
		return self._pos

	@property
	def direction(self):
		return self._dir

	def forward(self):
		self._pos += self._dir

	def backward(self):
		self._pos -= self._dir


if __name__ == "__main__":
	main()
