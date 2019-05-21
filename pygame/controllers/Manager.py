class ControllersManager(object):

	def __init__(self):
		self._waves = list()

	def __str__(self):
		ret = ""
		for idx, wave in enumerate(self._waves):
			ret += f"wave #{idx}:\n"
			for controller in wave:
				ret += f"\t{controller!r}\n"
		return ret

	def add(self, controller_class, init_params=None, back_write=tuple()):
		if init_params is None:
			controller = controller_class()
			self._add_to_wave(0, controller)
		else:
			controller = controller_class(*init_params)
			self._add_to_wave(self._find_highest_wave(init_params) + 1, controller)

		controller.add_back_writes(back_write)

		return controller

	def update(self):
		for wave in self._waves:
			for controller in wave:
				controller.update()

	def _add_to_wave(self, wave_index, controller):
		if len(self._waves) <= wave_index:
			new_waves_count = len(self._waves) - wave_index + 1
			self._waves.extend([list() for _ in range(new_waves_count)])
		self._waves[wave_index].append(controller)

	def _find_highest_wave(self, input_controllers):
		# search in backwards
		for wave_index in range(len(self._waves) - 1, -1, -1):
			if ControllersManager._contains_any_of(self._waves[wave_index], input_controllers):
				return wave_index

		return -1
		# raise RuntimeError("None of the input controllers is present in the manager!")

	@staticmethod
	def _contains_any_of(haystack, items):
		return len(set(haystack).intersection(items)) > 0
