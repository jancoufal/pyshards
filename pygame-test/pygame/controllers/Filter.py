from .Base import ControllerBase


class ControllerFilterLowLimit(ControllerBase):
	def __init__(self, ctrl_input, ctrl_low_limit):
		super().__init__((ctrl_input, ctrl_low_limit))

	def _update(self):
		return max(self._in[0].value, self._in[1].value)


class ControllerFilterHighLimit(ControllerBase):
	def __init__(self, ctrl_input, ctrl_hi_limit):
		super().__init__((ctrl_input, ctrl_hi_limit))

	def _update(self):
		return min(self._in[0].value, self._in[1].value)


class ControllerFilterBandLimit(ControllerBase):
	def __init__(self, ctrl_input, ctrl_low_limit, ctrl_hi_limit):
		super().__init__((ctrl_input, ctrl_low_limit, ctrl_hi_limit))

	def _update(self):
		return min(max(self._in[0].value, self._in[1].value), self._in[2].value)


class ControllerFilterSchmittTrigger(ControllerBase):
	def __init__(self, ctrl_input, ctrl_low_threshold, ctrl_hi_threshold, ctrl_low_output, ctrl_hi_output, ctrl_init_output):
		super().__init__((ctrl_input, ctrl_low_threshold, ctrl_hi_threshold, ctrl_low_output, ctrl_hi_output, ctrl_init_output))
		self._output_control = ctrl_init_output

	def _update(self):
		if self._in[0].value <= self._in[1].value:
			self._output_current = self._in[3]
		elif self._in[0].value >= self._in[2].value:
			self._output_current = self._in[4]

		return self._output_current.value
