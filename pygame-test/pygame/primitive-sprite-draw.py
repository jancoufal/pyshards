import pygame


def main():
	pygame.init()
	pygame.display.set_caption("minimal program")
	screen = pygame.display.set_mode((500, 500))

	s = pygame.Surface((2, 2))
	s.set_at((0, 0), pygame.Color("#ff000000"))
	s.set_at((1, 0), pygame.Color("#00ff0000"))
	s.set_at((0, 1), pygame.Color("#0000ff00"))
	s.set_at((1, 1), pygame.Color("#ff800000"))

	screen.blit(s, (0, 0))

	pygame.display.update()
	pygame.display.flip()

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return


if __name__ == "__main__":
	main()
