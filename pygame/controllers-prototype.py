import time
import pygame
from controllers.GameLoopState import GameLoopState
from controllers.ControllersManager import ControllersManager


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


class ControllerBase(object):
	def __init__(self, input_controllers=tuple()):
		self._in = input_controllers
		self._out = None

	def __str__(self):
		return str(self._out)

	@property
	def value(self):
		return self._out

	def update(self):
		self._out = self._update()

	def _update(self):
		error_message = f"You have to derive from the {self.__class__.__name__} class and define your own _update() method."
		raise NotImplementedError(error_message)


class ControllerKeysPressed(ControllerBase):
	def __init__(self):
		super().__init__()
		self._out = set()

	def __str__(self):
		return f"CtrlKeysPressed({','.join(map(str, self._out))})"

	def _update(self):
		return self._out

	def key_pressed(self, key):
		self._out.add(key)

	def key_released(self, key):
		self._out.remove(key)


class ControllerKeyValue(ControllerBase):
	def __init__(self, key):
		super().__init__()
		self._key = key

	def _update(self):
		return self._key


class ControllerKeyPressed(ControllerBase):
	def __init__(self, ctrl_keys_pressed, ctrl_key):
		super().__init__((ctrl_keys_pressed, ctrl_key))

	def _update(self):
		return self._in[1].value in self._in[0].value


class ControllerTimeTicks(ControllerBase):
	def _update(self):
		return time.perf_counter()


class ControllerTimeDelta(ControllerBase):
	def __init__(self, ctrl_time_ticks):
		super().__init__((ctrl_time_ticks, ))
		self._last_ticks = 0

	def _update(self):
		delta = self._in[0].value - self._last_ticks
		self._last_ticks = self._in[0].value
		return delta


if __name__ == "__main__":
	main()
