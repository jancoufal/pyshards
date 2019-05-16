class ControllerBase(object):
	def __init__(self, input_controllers=tuple()):
		self._in = input_controllers
		self._out = None

	def __str__(self):
		return str(self._out)

	@property
	def value(self):
		return self._out

	def update(self):
		self._out = self._update()

	def _update(self):
		error_message = f"You have to derive from the {self.__class__.__name__} class and define your own _update() method."
		raise NotImplementedError(error_message)
