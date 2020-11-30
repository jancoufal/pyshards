import pygame


class Mode13h(object):
	WIDTH = 320
	HEIGHT = 200

	@staticmethod
	def index_to_xy(index):
		x, y = index % Mode13h.WIDTH, index // Mode13h.WIDTH
		if y >= Mode13h.HEIGHT:
			raise RuntimeError(f"Index {index} out of range (=> [{x}:{y}])!")
		return x, y

	@staticmethod
	def as_rect(mult_factor=1):
		return pygame.Rect(0, 0, mult_factor * Mode13h.WIDTH, mult_factor * Mode13h.HEIGHT)

	@staticmethod
	def map_range_value_to_range(src_val, src_min, src_max, dst_min, dst_max):
		src_range = src_max - src_min
		dst_range = dst_max - dst_min
		norm_val = src_val - src_min  # normalization
		src_percent = norm_val / src_range
		return int(dst_min + src_percent * dst_range)


