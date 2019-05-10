import pygame


def main():
	pygame.init()
	pygame.display.set_caption("minimal program")
	screen = pygame.display.set_mode((500, 500))

	car_width = 49
	s = pygame.Surface((car_width, 100))
	s.fill(pygame.Color("#cc000000"))
	for y, x in enumerate(range(0, car_width // 2)):
		s.set_at((car_width // 2 + x, y), pygame.Color("#ffffff"))
		s.set_at((car_width // 2 - x, y), pygame.Color("#ffffff"))

	car_pos = (0, 0)

	car_speed = 10
	key_down_event = {
		pygame.K_UP: lambda pos: (pos[0], pos[1] - car_speed),
		pygame.K_DOWN: lambda pos: (pos[0], pos[1] + car_speed),
		pygame.K_LEFT: lambda pos: (pos[0] - car_speed, pos[1]),
		pygame.K_RIGHT: lambda pos: (pos[0] + car_speed, pos[1]),
	}

	while True:
		for event in pygame.event.get():

			screen.blit(s, car_pos)

			pygame.display.update()

			print(event)

			if event.type == pygame.KEYDOWN and event.key in key_down_event.keys():
				car_pos = key_down_event[event.key](car_pos)

			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.unicode == 'q'):
				return


if __name__ == "__main__":
	main()
