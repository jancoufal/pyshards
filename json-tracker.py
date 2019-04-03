from sys import argv
from enum import Enum

file = r"d:\detection_submit.v3.json"
file = r"d:\configuration.v3.json"
file = r"d:\configuration.v3-b.json"


def yesno(condition):
	return 'yes' if condition else 'no'


class TapeCassette(object):
	def __init__(self, cassette_content):
		self.data = cassette_content
		self.length = len(self.data)

	def read(self, pos):
		return self.data[pos] if 0 <= pos < self.length else None


class TapeTrackerState(Enum):
	Nothing = 0
	Starting = 1
	Continuing = 2
	Finishing = 3

	@staticmethod
	def next_state(value):
		if value == TapeTrackerState.Starting:
			return TapeTrackerState.Continuing

		if value == TapeTrackerState.Finishing:
			return TapeTrackerState.Nothing


class TapeTrackerResults(object):
	def __init__(self):
		self.results = []

	def move(self, result):
		self.results.extend(result.results)
		del result.results[:]

	def push(self, result):
		self.results.append(result)

	def pop_all(self):
		while len(self.results):
			yield self.results.pop()


class TapeTracker(object):
	def __init__(self):
		self.tape_machine = None

	def set_tape_machine(self, tape_machine):
		self.tape_machine = tape_machine


class TapeTrackerHtmlize(TapeTracker):
	def __init__(self):
		TapeTracker.__init__(self)
		self.state_string = TapeTrackerState.Nothing
		self.state_number = TapeTrackerState.Nothing
		self.results = TapeTrackerResults()
		self.late_results = TapeTrackerResults()

	def detect_string(self):

		if self.state_string == TapeTrackerState.Starting:
			self.state_string = TapeTrackerState.Continuing

		if self.state_string == TapeTrackerState.Finishing:
			self.state_string = TapeTrackerState.Nothing

		token = self.tape_machine.read_tape()

		if token == '"':
			if self.state_string == TapeTrackerState.Nothing:
				self.state_string = TapeTrackerState.Starting
				self.results.push('<span style="color: #800000;">')
			elif self.state_string in (TapeTrackerState.Starting, TapeTrackerState.Continuing):
				self.state_string = TapeTrackerState.Finishing
				self.late_results.push('</span>')

	def detect_number(self):
		if self.state_string not in (TapeTrackerState.Starting, TapeTrackerState.Continuing):

			if self.state_number == TapeTrackerState.Starting:
				self.state_number = TapeTrackerState.Continuing

			if self.state_number == TapeTrackerState.Finishing:
				self.state_number = TapeTrackerState.Nothing

			token = self.tape_machine.read_tape()

			if token.isdigit() and self.state_number == TapeTrackerState.Nothing:
				self.state_number = TapeTrackerState.Starting
				self.results.push('<span style="color: #ff8000;">')

			if not token.isdigit() and token != '.' and self.state_number in (
			TapeTrackerState.Starting, TapeTrackerState.Continuing):
				self.state_number = TapeTrackerState.Finishing
				self.results.push('</span>')
		else:
			self.state_number = TapeTrackerState.Nothing

	def track(self):
		# late results
		self.results.move(self.late_results)

		# detectors (order is important!)
		self.detect_string()
		self.detect_number()

		return self.results


class TapeTrackerCppAvgString(TapeTracker):
	def __init__(self):
		TapeTracker.__init__(self)
		self.results = TapeTrackerResults()
		self.late_results = TapeTrackerResults()

	def detect_quote(self):
		token = self.tape_machine.read_tape()

		if token == '"':
			self.results.push('\\')

	def detect_newline(self):
		token = self.tape_machine.read_tape()

		if self.tape_machine.read_tape(-1) == None:
			self.results.push('AVG_TEXT("')

		if token == '\n':
			self.results.push('")')
			self.late_results.push('AVG_TEXT("')

		if self.tape_machine.read_tape(1) == None:
			self.late_results.push('")')

	def track(self):
		# late results
		self.results.move(self.late_results)

		self.detect_quote()
		self.detect_newline()

		return self.results


class TapeTrackers(object):
	def __init__(self):
		self.trackers = []

	def add(self, tape_machine, tracker):
		tracker.set_tape_machine(tape_machine)
		self.trackers.append(tracker)

	def track(self):
		return [tracker.track() for tracker in self.trackers]


class TapeMachine(object):
	def __init__(self):
		self.trackers = TapeTrackers()

	def load_cassette(self, tape):
		self.tape = tape
		self.tape_pos = 0

	def add_tracker(self, tracker):
		self.trackers.add(self, tracker)

	def get_tape_pos(self):
		return self.tape_pos

	def read_tape(self, position_divergence=0):
		return self.tape.read(self.tape_pos + position_divergence)

	def play(self):
		for self.tape_pos in range(self.tape.length):
			note = self.read_tape()

			for tracker_results in self.trackers.track():
				for tracker_result in tracker_results.pop_all():
					yield tracker_result

			yield note

		# flush trackers
		for tracker_results in self.trackers.track():
			for tracker_result in tracker_results.pop_all():
				yield tracker_result


def main():
	if len(argv) < 2:
		print('usage:', argv[0], '<file>')
		return

	tape = TapeMachine()
	with open(argv[1], 'rt') as json_file:
		cassette = TapeCassette(json_file.read())
		tape.load_cassette(cassette)
		# tape.add_tracker(TapeTrackerHtmlize())
		tape.add_tracker(TapeTrackerCppAvgString())

		for note in tape.play():
			print(note, end='')


# print('ok')

if __name__ == '__main__':
	main()
