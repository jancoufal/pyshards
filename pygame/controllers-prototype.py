import pygame


def main():
	pygame.init()
	pygame.display.set_caption("minimal program")
	pygame.display.set_mode((240, 180))

	loop_state = LoopState()

	keys_pressed = CtrlKeysPressed()
	event_type_handlers = {
		pygame.QUIT: lambda e: loop_state.stop(),
		pygame.KEYDOWN: lambda e: keys_pressed.add_key(e.key),
		pygame.KEYUP: lambda e: keys_pressed.remove_key(e.key),
	}

	while loop_state.active:
		for event in pygame.event.get():

			print(event)

			if event.type in event_type_handlers.keys():
				event_type_handlers[event.type](event)

			print(keys_pressed)


class LoopState(object):
	def __init__(self):
		self._active = True
		# self._frames = 0

	@property
	def active(self):
		return self._active

	def stop(self):
		self._active = False


class Ctrl0(object):
	def __init__(self, update_fn):
		self._up_fn = update_fn
		self._out = None

	@property
	def value(self): return self._out
	def update(self): self._out = self._up_fn()


class CtrlKeysPressed(Ctrl0):
	def __init__(self):
		super().__init__(None)
		self._out = set()

	def __str__(self):
		return f"CtrlKeysPressed({','.join(map(str, self._out))!s})"

	def add_key(self, key):
		self._out.add(key)

	def remove_key(self, key):
		self._out.remove(key)


class Ctrl1(object):
	def __init__(self, update_fn):
		self._up_fn = update_fn
		self._out = None
		self._in1 = None

	@property
	def value(self): return self._out
	def set_in1(self, ctrl1): self._in1 = ctrl1
	def update(self): self._out = self._up_fn(self._in1.value)


if __name__ == "__main__":
	main()
