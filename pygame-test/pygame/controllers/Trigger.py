from .Base import ControllerBase


class ControllerTriggerHigh(ControllerBase):
	def __init__(self, ctrl_input, ctrl_high_threshold):
		super().__init__((ctrl_input, ctrl_high_threshold))

	def _update(self):
		return self._in[0].value >= self._in[1].value


class ControllerTriggerLow(ControllerBase):
	def __init__(self, ctrl_input, ctrl_low_threshold):
		super().__init__((ctrl_input, ctrl_low_threshold))

	def _update(self):
		return self._in[0].value <= self._in[1].value
