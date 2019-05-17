from .Base import ControllerBase


class ControllerMinus(ControllerBase):
	def __init__(self, ctrl_input):
		super().__init__((ctrl_input, ))

	def _update(self):
		return - self._in[0].value


class ControllerSum(ControllerBase):
	def __init__(self, *controls):
		super().__init__(controls)

	def _update(self):
		return sum(map(ControllerBase.value.fget, self._in))
