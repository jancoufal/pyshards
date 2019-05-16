import time
from .Base import ControllerBase


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


