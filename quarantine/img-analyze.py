# python3

import struct
from pathlib import Path
import pygame
import numpy
from mode13h import Mode13h
from img_x import ImageX


def main():
	file1 = "data/images/loadscr.img"
	file2 = "data/images/screenshots/loading-screen.png"

	sur1 = ImageX(file1).surface
	sur2 = pygame.image.load(file2)

	print(sur1.get_bitsize())
	print(sur2.get_bitsize())
	print(sur2.get_palette())

	pa1 = pygame.PixelArray(sur1)
	pa2 = pygame.PixelArray(sur2)

	print(numpy.histogram(pa1, bins=256)[0])
	print(numpy.histogram(pa2, bins=256)[0])

	# print(pa1)
	# print(pa2)

	pa1.close()
	pa2.close()


if __name__ == "__main__":
	main()
