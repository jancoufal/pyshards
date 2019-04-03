file = r"d:\configuration.v3_test.json"


class StateElement(object):
	def __init__(self, event_on, event_off):
		self.switched_now = False
		self.powered = False
		self.event_on = event_on
		self.event_off = event_off

	def switch(self, new_state=None, *args, **kwargs):
		if type(new_state) is bool:
			self.switched_now = self.powered != new_state
			self.powered = new_state
		else:
			self.switched_now = True
			self.powered = not self.powered

		# event
		if self.switched_now:
			if self.powered and callable(self.event_on):
				self.event_on(*args, **kwargs)
			if not self.powered and callable(self.event_off):
				self.event_off(*args, **kwargs)

	def tick(self):
		self.switched_now = False


class StateBoard(object):
	def __init__(self):
		self.signals = {}
		self.last_signaled_key = None

	def add_signaler(self, name, signal_fn, state_element):
		self.signals[name] = {'fn': signal_fn, 'state': state_element}

	def signal(self, token):
		# reset last signaler
		if self.last_signaled_key in self.signals:
			self.signals[self.last_signaled_key]['state'].tick()

		for key in self.signals:
			if self.signals[key]['fn'](token):
				self.last_signaled = key
				self.signals[key]['state'].switch()


class TapeMachine(object):
	def __init__(self, text_tape):
		self.tape = text_tape
		self.state = StateBoard()
		self.state.add_signaler('string', self.signalString, StateElement(self.onStringStart, self.onStringEnd))
		self.state.add_signaler('number', self.signalNumber, StateElement(self.onNumberStart, self.onNumberEnd))

	def signalString(self, token):
		return token == '"'

	def onStringStart(self, *args, **kwargs):
		print('<^>', end='')

	def onStringEnd(self, *args, **kwargs):
		print('<$>', end='')

	def signalNumber(self, token):
		return token.isdigit()

	def onNumberStart(self, *args, **kwargs):
		print('[[', end='')

	def onNumberEnd(self, *args, **kwargs):
		print(']]', end='')

	def play(self):
		for ch in self.tape:
			self.state.signal(ch)

			# if self.state.switched_on('"'):
			#	yield '<span style="color: red">'

			yield ch

	# if  self.state.switched_off('"'):
	#	yield '</span>'


def main():
	with open(file, 'rt') as json_file:
		tape = TapeMachine(json_file.read())
		for ch in tape.play():
			print(ch, end='')

	print('ok')


if __name__ == '__main__':
	main()
