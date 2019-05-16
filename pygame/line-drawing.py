import pygame
import math
import numpy
import random


def main():
	pygame.init()
	pygame.display.set_caption("line drawings")

	screen_rect = pygame.Rect(0, 0, 500, 500)
	screen = pygame.display.set_mode(screen_rect.size)

	# affine vector
	quad = (
		Vector3.affine(0, 0),
		Vector3.affine(100, 0),
		Vector3.affine(100, 100),
		Vector3.affine(0, 100),
	)

	done = False
	clock = pygame.time.Clock()
	loop = 0

	bkg = pygame.color.Color("#00000000")
	clr = pygame.color.Color("#ff8800")

	while not done:

		# clock.tick(10)

		# animate
		vertices = list(quad)

		# m = Matrix3x3.get_identity()
		# m = Matrix3x3.get_translate(loop, loop)

		# m = Matrix3x3.get_scale(loop / 100.0, loop / 200.0)
		m = Matrix3x3.get_rotate(loop / 100.0)
		# m = Matrix3x3.get_shear_x(loop / 1.0)
		# m = Matrix3x3.get_shear_y(loop / 1.0)
		# m = Matrix3x3.get_shear(loop / 1.0, loop / 2.0)
		# m = Matrix3x3.get_reflect_y()
		vertices = list(map(lambda v: v.transform(m), vertices))

		# center the image
		m = Matrix3x3.get_translate(*screen_rect.center)
		vertices = list(map(lambda v: v.transform(m), vertices))

		# random color
		clr = pygame.color.Color(*(pygame.color.THECOLORS[random.choice(list(pygame.color.THECOLORS.keys()))]))

		# screen.fill(bkg)
		pygame.draw.aalines(screen, clr, True, tuple(map(Vector3.get_xy, vertices)), 1)
		pygame.display.flip()

		for event in pygame.event.get():

			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.unicode == 'q'):
				done = True

		loop += 1


class Vector3(object):
	def __init__(self, x, y, z):
		self._xyz = (x, y, z)

	def __str__(self):
		return f"Vector3({self.x}, {self.y}, {self.z})"

	@classmethod
	def affine(cls, x, y):
		return cls(x, y, 1)

	@property
	def x(self): return self._xyz[0]

	@property
	def y(self): return self._xyz[1]

	@property
	def z(self): return self._xyz[2]

	@property
	def xyz(self): return self._xyz

	@property
	def xy(self):
		return self.xyz[:2]

	def get_xy(self):
		return self.xy

	def __len__(self):
		return numpy.sqrt(self.x * self.x + self.y * self.y)

	def transform(self, matrix3x3):
		return Vector3(*numpy.matmul(self.xyz, matrix3x3.as_array))


class Matrix3x3(object):
	def __init__(self, a0, a1, a2, b0, b1, b2, c0, c1, c2):
		self._mat = [[a0, b0, c0], [a1, b1, c1], [a2, b2, c2]]

	def __str__(self):
		return f"matrix([{self._mat[0]!s}], {self._mat[1]!s}], {self._mat[2]!s}])"

	@property
	def as_array(self):
		return self._mat

	@classmethod
	def get_identity(cls):
		return cls(
			1, 0, 0,
			0, 1, 0,
			0, 0, 1
		)

	@classmethod
	def get_translate(cls, x, y):
		return cls(
			1, 0, x,
			0, 1, y,
			0, 0, 1
		)

	@classmethod
	def get_scale(cls, w, h):
		return cls(
			w, 0, 0,
			0, h, 0,
			0, 0, 1
		)

	@classmethod
	def get_rotate(cls, angle):
		r = math.radians(angle)
		c, s = math.cos(r), math.sin(r)
		return cls(
			c, s, 0,
			-s, c, 0,
			0, 0, 1
		)

	@classmethod
	def get_shear(cls, angle_x, angle_y):
		t_phi = math.tan(math.radians(angle_x))
		t_psi = math.tan(math.radians(angle_y))
		return cls(
			1, t_phi, 0,
			t_psi, 1, 0,
			0, 0, 1
		)

	@classmethod
	def get_shear_x(cls, angle):
		return cls.get_shear(angle, 0)

	@classmethod
	def get_shear_y(cls, angle):
		return cls.get_shear(0, angle)

	@classmethod
	def _get_reflect(cls, reflect_x, reflect_y):
		return cls(
			reflect_x, 0, 0,
			0, reflect_y, 0,
			0, 0, 1
		)

	@classmethod
	def get_reflect(cls):
		return cls._get_reflect(-1, -1)

	@classmethod
	def get_reflect_x(cls):
		return cls._get_reflect(1, -1)

	@classmethod
	def get_reflect_y(cls):
		return cls._get_reflect(-1, 1)


if __name__ == "__main__":
	main()
