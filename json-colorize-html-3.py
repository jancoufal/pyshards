file = r"d:\configuration.v3_test.json"


class TapeCassette(object):
	def __init__(self, cassette_content):
		self.data = cassette_content
		self.length = len(self.data)

	def read(self, pos):
		return self.data[pos] if 0 <= pos < self.length else None


class TapeTrackerCallback(object):
	def __init__(self, type, fn, call_result):
		self.type = type  # on/off
		self.fn = fn  # function reference
		self.result = call_result  # self explain name :)

	def __str__(self):
		# return 'type => {0:s}, fn => {1:s}, result => {2:s}'.format(str(self.type), str(self.fn), str(self.result))
		return '{{ type => {0:s}, result => {1:s} }}'.format(str(self.type), str(self.result))


class TapeTrackerResult(object):
	def __init__(self, name, now_tracking, callback_hit, callback, event):
		self.name = name
		self.now_tracking = now_tracking
		self.callback = callback
		self.callback_hit = callback_hit
		self.event = event

	def __str__(self):
		return '{ name: ' + self.name \
			   + ', now_tracking: ' + ('yes' if self.now_tracking else 'no') \
			   + ', callback => ' + str(self.callback) \
			   + ', event => ' + str(self.event) \
			   + ' }'


class TapeTracker(object):
	def __init__(self, tape_machine, name, track_on, track_off, event_on, event_off):
		self.tape_machine = tape_machine
		self.name = name
		self.now_tracking = False
		self.callback = {'on': track_on, 'off': track_off}
		self.events = {'on': event_on, 'off': event_off}

	def track(self, *args, **kwargs):
		call_type = None  # on/off
		callback_hit = None
		callback_result = None  # callback result
		event_result = None  # event result

		# turn tracking on?
		if not self.now_tracking:
			call_type = 'on'
			callback_result = self.callback['on'](self.tape_machine)
			if callback_result:
				event_result = self.events['on'](*args, **kwargs)
				self.now_tracking = True
				callback_hit = True

		# turn tracking off?
		elif self.now_tracking:
			call_type = 'off'
			callback_result = self.callback['off'](self.tape_machine)
			if callback_result:
				event_result = self.events['off'](*args, **kwargs)
				self.now_tracking = False
				callback_hit = True

		return TapeTrackerResult(self.name, self.now_tracking, callback_hit,
								 TapeTrackerCallback(call_type, self.callback[call_type], callback_result),
								 TapeTrackerCallback(call_type, self.events[call_type], event_result))


class TapeTrackers(object):
	def __init__(self):
		self.trackers = []

	def add(self, tape_machine, name, ton, toff, eon, eoff):
		self.trackers.append(TapeTracker(tape_machine, name, ton, toff, eon, eoff))

	def track(self, *args, **kwargs):
		for idx in range(len(self.trackers)):
			tracker_result = self.trackers[idx].track(*args, **kwargs)
			if tracker_result.callback_hit:
				return tracker_result
		return None


class TapeTrackerJson(object):
	@staticmethod
	def signal_string(tape_machine):
		return tape_machine.read_tape() == '"'

	@staticmethod
	def event_string_start(*args, **kwargs):
		return '^'

	@staticmethod
	def event_string_end(*args, **kwargs):
		return '$'

	@staticmethod
	def signal_number(tape_machine):
		return tape_machine.read_tape().isdigit() and not tape_machine.read_tape(1).isdigit()

	@staticmethod
	def event_number_start(*args, **kwargs):
		return '<'

	@staticmethod
	def event_number_end(*args, **kwargs):
		return '>'

	@staticmethod
	def generate(tape_machine):
		tape_trackers = TapeTrackers()

		tape_trackers.add(tape_machine, 'string',
						  TapeTrackerJson.signal_string, TapeTrackerJson.signal_string,
						  TapeTrackerJson.event_string_start, TapeTrackerJson.event_string_end)

		tape_trackers.add(tape_machine, 'number',
						  TapeTrackerJson.signal_number, TapeTrackerJson.signal_number,
						  TapeTrackerJson.event_number_start, TapeTrackerJson.event_number_end)

		return tape_trackers


class TapeMachine(object):
	def __init__(self):
		self.trackers = {}  # TapeTrackerJson.generate(self)
		self.tape = None
		self.tape_pos = None

	def load_cassette(self, tape):
		if not isinstance(tape, TapeCassette):
			raise TypeError('TapeMachine can play only TapeCassette')

		self.tape = tape
		self.tape_pos = 0

	def add_tracker(self):
		pass

	def get_tape_pos(self):
		return self.tape_pos

	def read_tape(self, relative_to_head_position=0):
		return self.tape[self.tape_pos + relative_to_head_position]

	def play(self):

		for self.tape_pos in range(self.tape_len):
			res = self.trackers.track()

			if res is not None:

				late_result = res.name == 'string' and not res.now_tracking and res.event.type == 'off'

				if not late_result and res.event.result is not None:
					yield res.event.result

			yield self.read_tape()

			if res is not None:
				if late_result and res.event.result is not None:
					yield res.event.result


def main():
	tape = TapeMachine()
	with open(file, 'rt') as json_file:
		cassette = TapeCassette(json_file.read())
		tape.load_cassette(cassette)

		'''
		for ch in tape.play():
			print(ch, end = '')
		'''

	print('ok')


if __name__ == '__main__':
	main()
