class FilterLowStop(object):
	def __init__(self, low_limit, value_on_low):
		self._limit = low_limit
		self._value = value_on_low

	def __call__(self, value):
		return value if value >= self._limit else self._value


class FilterHighStop(object):
	def __init__(self, hi_limit, value_on_hi):
		self._limit = hi_limit
		self._value = value_on_hi

	def __call__(self, value):
		return value if value <= self._limit else self._value


class FilterBandStop(object):
	def __init__(self, low_limit, value_on_low, hi_limit, value_on_hi):
		self._stop_low = FilterLowStop(low_limit, value_on_low)
		self._stop_high = FilterHighStop(hi_limit, value_on_hi)

	def __call__(self, value):
		return self._stop_high(self._stop_low(value))


class FilterSchmittTrigger(object):
	def __init__(self, low_threshold, hi_threshold, low_output, hi_output, init_output=0):
		self._threshold_low = low_threshold
		self._threshold_hi = hi_threshold
		self._output_low = low_output
		self._output_hi = hi_output
		self._output_current = init_output

	def __call__(self, value):
		if value <= self._threshold_low:
			self._output_current = self._output_low
		elif value >= self._threshold_hi:
			self._output_current = self._output_hi

		return self._output_current

