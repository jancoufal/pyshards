import time
import pygame


def main():
	pygame.init()
	pygame.display.set_caption("minimal program")
	pygame.display.set_mode((240, 180))

	game_loop = GameLoopState()

	keys_pressed = CtrlKeysPressed()

	up_pressed = Ctrl1(lambda c0: pygame.K_UP in c0)
	up_pressed.set_in1(keys_pressed)

	down_pressed = Ctrl1(lambda c0: pygame.K_DOWN in c0)
	down_pressed.set_in1(keys_pressed)

	event_type_handlers = {
		pygame.QUIT: lambda e: game_loop.stop(),
		pygame.KEYDOWN: lambda e: keys_pressed.add_key(e.key),
		pygame.KEYUP: lambda e: keys_pressed.remove_key(e.key),
	}

	time_ticks = CtrlTimeTicks()
	time_delta = CtrlTimeDelta()
	time_delta.set_in1(time_ticks)

	game_loop.start()
	while game_loop.active:
		for event in pygame.event.get():

			print(event)
			print(game_loop)

			if event.type in event_type_handlers.keys():
				event_type_handlers[event.type](event)

			up_pressed.update()
			down_pressed.update()
			time_ticks.update()
			time_delta.update()

			print(keys_pressed)
			print(f"up: {up_pressed}, down: {down_pressed}")
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


class Ctrl0(object):
	def __init__(self, update_fn):
		self._up_fn = update_fn
		self._out = None

	def __str__(self): return str(self._out)
	@property
	def value(self): return self._out
	def update(self): self._out = self._up_fn()


class CtrlKeysPressed(Ctrl0):
	def __init__(self):
		super().__init__(lambda _: _)
		self._out = set()

	def __str__(self):
		return f"CtrlKeysPressed({','.join(map(str, self._out))!s})"

	def add_key(self, key):
		self._out.add(key)

	def remove_key(self, key):
		self._out.remove(key)


class CtrlTimeTicks(Ctrl0):
	def __init__(self):
		super().__init__(lambda: time.perf_counter())


class Ctrl1(Ctrl0):
	def __init__(self, update_fn):
		super().__init__(update_fn)
		self._in1 = None

	def set_in1(self, ctrl1): self._in1 = ctrl1
	def update(self): self._out = self._up_fn(self._in1.value)


class CtrlTimeDelta(Ctrl1):
	def __init__(self):
		super().__init__(lambda time_ticks: self._update(time_ticks))
		self._last_ticks = 0

	def _update(self, time_ticks):
		delta = time_ticks - self._last_ticks
		self._last_ticks = time_ticks
		return delta


if __name__ == "__main__":
	main()
