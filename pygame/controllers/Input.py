from .Base import ControllerBase


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
