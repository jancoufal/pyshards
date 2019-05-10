import pygame
import math


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
		initial_rotation=0,
		rotation_angle_step=5,
	)

	key_type_events = {
		pygame.KEYDOWN: lambda _keys_pressed, _event: _keys_pressed.add(_event.key),
		pygame.KEYUP: lambda _keys_pressed, _event: _keys_pressed.remove(_event.key),
	}

	keys_active = set()

	key_mappings = {
		pygame.K_UP: OrientedPoint2D.forward,
		pygame.K_DOWN: OrientedPoint2D.backward,
		pygame.K_LEFT: OrientedPoint2D.turn_left,
		pygame.K_RIGHT: OrientedPoint2D.turn_right,
	}

	timer = PrimitiveTimer(
		timeout=25
	)

	while True:

		if timer:

			for key in keys_active:
				if key in key_mappings.keys():
					key_mappings[key](car_loc)

			car_rot = pygame.transform.rotate(car_surf, car_loc.rotation_angle)
			screen.blit(car_rot, car_loc.position.xy)

			pygame.display.update()

		for event in pygame.event.get():

			if event.type in key_type_events.keys():
				key_type_events[event.type](keys_active, event)

			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.unicode == 'q'):
				return


class Vector2d(object):
	def __init__(self, x, y):
		self._x, self._y = x, y

	def __str__(self):
		return f"vec({self.x, self.y})"

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

	@classmethod
	def rotate(cls, vector2d, degrees):
		x, y, r = vector2d.x, vector2d.y, math.radians(degrees)
		return cls(
			x * math.cos(r) + y * math.sin(r),
			-x * math.sin(r) + y * math.cos(r)
		)


class OrientedPoint2D(object):
	def __init__(self, position=Vector2d(0, 0), direction=Vector2d(1, 0), initial_rotation=0, rotation_angle_step=5):
		self._pos = position
		self._dir_initial = direction
		self._dir_actual = direction
		self._angle_step = rotation_angle_step
		self._angle_actual = initial_rotation

	def __str__(self):
		return f"orientedPoint2D(pos => {self.position}, dir => {self.direction}, angle => {self.rotation_angle})"

	@property
	def position(self):
		return self._pos

	@property
	def direction(self):
		return self._dir_actual

	@property
	def rotation_angle(self):
		return self._angle_actual

	def forward(self):
		self._pos += self.direction

	def backward(self):
		self._pos -= self.direction

	def turn_left(self):
		self._rotate(self._angle_step)

	def turn_right(self):
		self._rotate(-self._angle_step)

	def _rotate(self, step):
		self._angle_actual += step
		self._angle_actual %= 360
		self._dir_actual = Vector2d.rotate(self._dir_initial, self._angle_actual)


class PrimitiveTimer(object):
	def __init__(self, timeout=250):
		self._ticks = 0
		self._timeout = timeout
		self.reset()

	@property
	def ticks_elapsed(self):
		return pygame.time.get_ticks() - self._ticks

	def reset(self):
		self._ticks = pygame.time.get_ticks()

	def __bool__(self):
		if self.ticks_elapsed > self._timeout:
			self.reset()
			return True
		return False


if __name__ == "__main__":
	main()
