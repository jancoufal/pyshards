class ControllerBase(object):
	def __init__(self, input_controllers=tuple()):
		self._in = input_controllers
		self._out = None
		self._back_write = set()

	def __str__(self):
		return str(self._out)

	def add_back_writes(self, controllers):
		self._back_write.update(controllers)

	@property
	def value(self):
		return self._out

	def update(self):
		self._out = self._update()

		# back write
		for c in self._back_write:
			c._out = self._out

	def _update(self):
		error_message = f"You have to derive from the {self.__class__.__name__} class and define your own _update() method."
		raise NotImplementedError(error_message)


class ControllerStaticValue(ControllerBase):
	def __init__(self, value):
		super().__init__()
		self._value = value

	def _update(self):
		return self._value
