import time
import pygame


def main():
	pygame.init()
	pygame.display.set_caption("minimal program")
	pygame.display.set_mode((240, 180))

	game_loop = GameLoopState()

	ctrl_mgr = ControllerManager()

	keys_pressed = ctrl_mgr.add(ControllerKeysPressed)

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

			print(keys_pressed)
			print(f"forward: {key_forward_pressed}, backward: {key_backward_pressed}")
			print(f"time ticks: {time_ticks}, time delta: {time_delta}")

		ctrl_mgr.update()
		game_loop.update()


class GameLoopState(object):
	def __init__(self):
		self._active = False
		self._frames = 0
		self._start_time = time.perf_counter()

	def __str__(self):
		return f"fps: {self.fps:0.2f}, duration: {self.duration_sec:0.1f} sec, frames: {self.frame_count}"

	def start(self):
		self._active = True
		self._frames = 0
		self._start_time = time.perf_counter()

	def stop(self):
		self._active = False

	def update(self):
		self._frames += 1

	@property
	def active(self):
		return self._active

	@property
	def frame_count(self):
		return self._frames

	@property
	def duration_sec(self):
		return time.perf_counter() - self._start_time

	@property
	def fps(self):
		return self.frame_count / self.duration_sec


class ControllerManager(object):

	class WaveContainer(object):
		def __init__(self):
			self._controllers = list()

		def __iter__(self):
			yield from self._controllers

		def contains_any(self, items):
			return len(set(self._controllers).intersection(items)) > 0

		def append(self, controller):
			self._controllers.append(controller)

	def __init__(self):
		self._waves = list()

	def __str__(self):
		ret = ""
		for idx, wave in enumerate(self._waves):
			ret += f"wave #{idx}:\n"
			for controller in wave:
				ret += f"\t{controller!r}\n"
		return ret

	def add(self, controller_class, init_params=None):
		if init_params is None:
			controller = controller_class()
			self._add_to_wave(0, controller)
		else:
			controller = controller_class(*init_params)
			self._add_to_wave(self._find_highest_wave(init_params) + 1, controller)

		return controller

	def update(self):
		for wave in self._waves:
			for controller in wave:
				controller.update()

	def _add_to_wave(self, wave_index, controller):
		if len(self._waves) <= wave_index:
			new_waves_count = len(self._waves) - wave_index + 1
			self._waves.extend([ControllerManager.WaveContainer() for _ in range(new_waves_count)])
		self._waves[wave_index].append(controller)

	def _find_highest_wave(self, input_controllers):
		# search in backwards
		for wave_index in range(len(self._waves) - 1, -1, -1):
			if self._waves[wave_index].contains_any(input_controllers):
				return wave_index

		return -1
		# raise RuntimeError("None of the input controllers is present in the manager!")


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
