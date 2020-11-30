import struct
from pathlib import Path
import pygame
from mode13h import Mode13h


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
