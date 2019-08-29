# python3

import glob
from pathlib import Path
import pygame
import time


def main():
	files = sorted(glob.glob("data/images/*.img"))

	scan_heads(files)
	exit(2)

	pygame.init()
	pygame.display.set_caption("quarantine pix format reconstruction")
	screen_rect = pygame.Rect(0, 0, 320, 200)
	screen = pygame.display.set_mode(screen_rect.size)

	for f in files:
		content = Path(f).read_bytes()
		print(f"filename: {f}")
		print(f"    size: {len(content)}")
		print(f"    head: {content[0:6].decode('ansi')}")
		width = int.from_bytes(content[6:8], byteorder='little')
		print(f"   width: {width}")
		height = int.from_bytes(content[8:10], byteorder='little')
		print(f"  height: {height}")
		print(f"  pixel count: {width * height}")
		img_data = content[10:]
		print(f"  data size: {len(img_data)}")
		print("drawing...")

		img_surface = pygame.Surface((width, height), flags=0, depth=32)

		pix_array = pygame.PixelArray(img_surface)
		pix_idx = 0
		for b in img_data:
			pix_array[pix_pos(pix_idx)] = (
				map_to_range((b >> 4) & 0x03, 0, 0x3, 0, 0xff),
				map_to_range((b >> 2) & 0x03, 0, 0x3, 0, 0xff),
				map_to_range((b >> 0) & 0x03, 0, 0x3, 0, 0xff)
			)
			pix_idx += 1
		pix_array.close()

		screen.fill(pygame.color.Color("#00000000"))
		screen.blit(img_surface, img_surface.get_rect())
		pygame.display.flip()

		time.sleep(2)

	print("image loop ends...")

	done = False
	while not done:
		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.unicode == 'q'):
				done = True


def pix_pos(idx):
	x, y = idx % 320, idx // 320
	if y >= 200:
		raise RuntimeError("index out of range!")
	return x, y


def map_to_range(val, val_min, val_max, range_min, range_max):
	src_range = val_max - val_min
	dst_range = range_max - range_min
	src_val = val - val_min		# normalization
	src_pos = src_val / src_range
	return int(range_min + src_pos * dst_range)


def scan_heads(files):
	for f in files:
		content = Path(f).read_bytes()
		print(f"{f[12:]:12s}", end=": ")
		print(bytes(map(byte_val_to_printable_ansi_byte, content[10:800])).decode(encoding="ansi"))


def byte_val_to_printable_ansi_byte(b):
	if b in (0, ascii('\n'), ascii('\r')):
		return ord('.')
	return b


if __name__ == "__main__":
	main()
