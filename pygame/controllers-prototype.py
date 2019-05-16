import pygame
from controllers.GameLoopState import GameLoopState
from controllers.Manager import ControllersManager
from controllers.Time import *
from controllers.Input import *


def main():

	pygame.init()
	pygame.display.set_caption("minimal program")
	pygame.display.set_mode((240, 180))

	game_loop = GameLoopState()

	ctrl_mgr = ControllersManager()

	keys_pressed = ctrl_mgr.add(ControllerKeysPressed)

	key_quit = ctrl_mgr.add(ControllerKeyValue, (pygame.K_q,))
	key_quit_pressed = ctrl_mgr.add(ControllerKeyPressed, (keys_pressed, key_quit))

	key_forward = ctrl_mgr.add(ControllerKeyValue, (pygame.K_UP,))
	key_forward_pressed = ctrl_mgr.add(ControllerKeyPressed, (keys_pressed, key_forward))

	key_backward = ctrl_mgr.add(ControllerKeyValue, (pygame.K_DOWN,))
	key_backward_pressed = ctrl_mgr.add(ControllerKeyPressed, (keys_pressed, key_backward))

	time_ticks = ctrl_mgr.add(ControllerTimeTicks)
	time_delta = ctrl_mgr.add(ControllerTimeDelta, (time_ticks, ))

	print(ctrl_mgr)

	event_type_handlers = {
		pygame.QUIT: lambda e: game_loop.stop(),
		pygame.KEYDOWN: lambda e: keys_pressed.key_pressed(e.key),
		pygame.KEYUP: lambda e: keys_pressed.key_released(e.key),
	}

	game_loop.start()
	while game_loop.active:
		for event in pygame.event.get():

			print(event)
			print(game_loop)

			if event.type in event_type_handlers.keys():
				event_type_handlers[event.type](event)

			ctrl_mgr.update()

			if key_quit_pressed.value:
				game_loop.stop()

			print(keys_pressed)
			print(f"forward: {key_forward_pressed}, backward: {key_backward_pressed}")
			print(f"time ticks: {time_ticks}, time delta: {time_delta}")

		ctrl_mgr.update()
		game_loop.update()


if __name__ == "__main__":
	main()
