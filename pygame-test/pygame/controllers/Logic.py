from .Base import ControllerBase


class ControllerSwitch(ControllerBase):
	def __init__(self, ctrl_switch, ctrl_on_false, ctrl_on_true):
		super().__init__((ctrl_switch, ctrl_on_false, ctrl_on_true))

	def _update(self):
		return self._in[2].value if self._in[0].value else self._in[1].value

