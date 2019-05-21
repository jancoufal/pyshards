from .Base import ControllerBase


class ControllerGeneratorIncrement(ControllerBase):
	def __init__(self, ctrl_increment_value, ctrl_init_value):
		super().__init__((ctrl_increment_value, ctrl_init_value))
		self._out = None

	def _update(self):
		return self._in[1].value if self._out is None else self._out + self._in[0].value


class ControllerGeneratorDecrement(ControllerBase):
	def __init__(self, ctrl_decrement_value, ctrl_init_value):
		super().__init__((ctrl_decrement_value, ctrl_init_value))
		self._out = None

	def _update(self):
		return self._in[1].value if self._out is None else self._out - self._in[0].value
