import time


class GameLoopState(object):
	def __init__(self):
		self._active = False
		self._frames = 0
		self._start_time = time.perf_counter()

	def __str__(self):
		return f"fps: {self.fps:0.2f}, duration: {self.duration_sec:0.1f} sec, frames: {self.frame_count}"

	def start(self):
		self._active = True
		self._frames = 0
		self._start_time = time.perf_counter()

	def stop(self):
		self._active = False

	def update(self):
		self._frames += 1

	@property
	def active(self):
		return self._active

	@property
	def frame_count(self):
		return self._frames

	@property
	def duration_sec(self):
		return time.perf_counter() - self._start_time

	@property
	def fps(self):
		return self.frame_count / self.duration_sec
