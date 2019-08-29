# python3

import glob
from pathlib import Path
import struct
import pygame
import time


def main():
	img_files = sorted(glob.glob("data/images/*.img"))

	# preload images
	imgs = [ImageX(f) for f in img_files]

	mode_13h_zoom = 4

	pygame.init()
	pygame.display.set_caption("quarantine pix format reconstruction")
	screen = pygame.display.set_mode(Mode13h.as_rect(mode_13h_zoom).size)

	img_idx = 0

	done = False
	while not done:
		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.unicode == 'q'):
				done = True

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					img_idx -= 1
				if event.key == pygame.K_RIGHT:
					img_idx += 1

				img_idx %= len(imgs)
				imgx = imgs[img_idx]

				pygame.display.set_caption(str(imgx))

				scaled_surface = pygame.transform.scale(imgx.surface, Mode13h.as_rect(mode_13h_zoom).size)

				screen.fill(pygame.color.Color("#00000000"))
				screen.blit(scaled_surface, Mode13h.as_rect(mode_13h_zoom))
				pygame.display.flip()


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


class ImageX(object):

	STRUCT_FMT_HEAD = "6sHH"

	def __init__(self, filename):
		self.filename = filename
		self.raw_data = Path(self.filename).read_bytes()
		head_struct = struct.unpack_from(ImageX.STRUCT_FMT_HEAD, self.raw_data)
		self.imagex = head_struct[0]
		self.width = head_struct[1]
		self.height = head_struct[2]
		self.surface = pygame.Surface((self.width, self.height), flags=0, depth=32)
		self._fill_surface()

	def _fill_surface(self):
		pix_array = pygame.PixelArray(self.surface)

		offset = struct.calcsize(ImageX.STRUCT_FMT_HEAD)
		pix_idx = 0
		for s in struct.iter_unpack("B", self.raw_data[offset:]):
			b = s[0]
			clr_idx = Mode13h.map_range_value_to_range(b, 0x0, 0xff, 0x0, 0xff)
			pix_array[Mode13h.index_to_xy(pix_idx)] = (clr_idx, clr_idx, clr_idx)
			pix_idx += 1
		pix_array.close()

	def __str__(self):
		return f"{self.filename} > {self.width} x {self.height}"


if __name__ == "__main__":
	main()
