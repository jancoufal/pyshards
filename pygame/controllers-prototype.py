import time
import pygame


def main():
	pygame.init()
	pygame.display.set_caption("minimal program")
	pygame.display.set_mode((240, 180))

	game_loop = GameLoopState()

	controller_mgr = ControllerManager()

	keys_pressed = controller_mgr.add(ControllerKeysPressed)

	key_forward = controller_mgr.add(ControllerKeyValue, (pygame.K_UP, ))
	key_forward_pressed = controller_mgr.add(ControllerKeyPressed, (keys_pressed, key_forward))

	key_backward = controller_mgr.add(ControllerKeyValue, (pygame.K_DOWN, ))
	key_backward_pressed = controller_mgr.add(ControllerKeyPressed, (keys_pressed, key_backward))

	time_ticks = controller_mgr.add(ControllerTimeTicks)
	time_delta = controller_mgr.add(ControllerTimeDelta, (time_ticks, ))

	event_type_handlers = {
		pygame.QUIT: lambda e: game_loop.stop(),
		pygame.KEYDOWN: lambda e: keys_pressed.add_key(e.key),
		pygame.KEYUP: lambda e: keys_pressed.remove_key(e.key),
	}

	game_loop.start()
	while game_loop.active:
		for event in pygame.event.get():

			print(event)
			print(game_loop)

			if event.type in event_type_handlers.keys():
				event_type_handlers[event.type](event)

			controller_mgr.update_all()

			print(keys_pressed)
			print(f"forward: {key_forward_pressed}, backward: {key_backward_pressed}")
			print(f"time ticks: {time_ticks}, time delta: {time_delta}")

		game_loop.update()


class GameLoopState(object):
	def __init__(self):
		self._active = False
		self._frames = 0
		self._start_time = time.perf_counter()

	def __str__(self):
		return f"fps: {self.fps:0.2f}, duration: {self.duration_sec:0.1f} sec, frames: {self.frame_count}"

	def start(self): self._active, self._frames, self._start_time = True, 0, time.perf_counter()
	def stop(self): self._active = False
	def update(self): self._frames += 1

	@property
	def active(self): return self._active
	@property
	def frame_count(self): return self._frames
	@property
	def duration_sec(self): return time.perf_counter() - self._start_time
	@property
	def fps(self): return self.frame_count / self.duration_sec


class ControllerManager(object):
	def __init__(self):
		# the key is going to be a "wave"
		self._controllers = dict()

	def add(self, controller_class, init_params=tuple()):

		print(f"Adding controller {controller_class} with init params {init_params}")

		if len(init_params) == 0:
			controller = controller_class()
			self._add_to_wave(0, controller)
		else:
			controller = controller_class(*init_params)
			self._add_to_wave(self._find_highest_wave(init_params) + 1, controller)

		return controller

	def update_all(self):
		for wave in sorted(self._controllers.keys()):
			for controller in self._controllers[wave]:
				controller.update()

	def _add_to_wave(self, wave, controller):
		if wave not in self._controllers.keys():
			self._controllers[wave] = set()
		self._controllers[wave].add(controller)

	def _find_highest_wave(self, input_controllers):
		for wave in range(max(self._controllers.keys()), -1, -1):
			if len(self._controllers[wave].intersection(input_controllers)):
				return wave
		return 0
		# raise RuntimeError("None of the input controllers is present in the manager!")


class ControllerBase(object):
	def __init__(self, input_controllers=tuple()):
		self._in = input_controllers
		self._out = None

	def __str__(self): return str(self._out)

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

	def add_key(self, key):
		self._out.add(key)

	def remove_key(self, key):
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
