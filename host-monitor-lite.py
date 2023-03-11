import sys, logging
import time, datetime
import socket, requests

SETTINGS = {
	"data": {
		"keyname": "griffin-ntb",
	},
	"loop": {
		"max_allowed_exceptions": 5,
		"cooldown": {
			"switch_to_slow_after_iterations": 15, 
			"fast": 5,
			"slow": 30,
		},
	},
	"proxies": {
		"http": "http://emea-proxy.uk.oracle.com:80",
		"https": "http://emea-proxy.uk.oracle.com:80",
	},
	"logging": {
		"level": logging.DEBUG,
		"format": "%(asctime)s - %(levelname)s : %(message)s",
		"datefmt": "%Y-%m-%d %H:%M:%S",
	},
}

class MonitorData(object):
	@classmethod
	def create(cls):
		hostname = socket.gethostname()
		ip_list = socket.gethostbyname_ex(hostname)[-1]
		return cls(hostname, ip_list)

	@classmethod
	def createEmpty(cls):
		return cls("", list())

	def __init__(self, hostname, ip_list):
		self.hostname = hostname
		self.ip_list = ip_list

	def __eq__(self, other):
		return other.hostname == self.hostname and other.ip_list == self.ip_list

	def __str__(self):
		return f"Host: {self.hostname}, IP: {', '.join(self.ip_list)}"


class HostMonitor(object):
	def __init__(self):
		self._data = MonitorData.createEmpty()

	def pollData(self):
		new_data = MonitorData.create()
		if new_data != self._data:
			self._data = new_data
			return self._data
		else:
			return None


class PythonAnywhereWriter(object):

	URL = "http://griffin42.pythonanywhere.com/post/"

	def write(self, data:MonitorData):
		res = requests.post(
			url=f"{PythonAnywhereWriter.URL}{SETTINGS['data']['keyname']}/",
			proxies=SETTINGS["proxies"] if len(data.ip_list) > 1 else None,
			json={
				"time": str(datetime.datetime.now()),
				"host": data.hostname,
				"ip_list": data.ip_list,
			}
		)

		if not res.ok:
			raise RuntimeError("Failed to update python anywhere app. " + str(res))


class Cooldown(object):
	@classmethod
	def create(cls, cooldown_settings):
		return cls(
			cooldown_settings["fast"],
			cooldown_settings["slow"],
			cooldown_settings["switch_to_slow_after_iterations"]
		)

	def __init__(self, fast_timeout, slow_timeout, slow_countdown):
		self._fast = fast_timeout
		self._slow = slow_timeout
		self._slow_countdown = slow_countdown
		self._switched_to_slow = False

	def update(self):
		if not self._switched_to_slow and self._slow_countdown > 0:
			self._slow_countdown -= 1

		if not self._switched_to_slow and self._slow_countdown == 0:
			self._switched_to_slow = True

		return self.get_cooldown()

	def get_cooldown(self):
		return self._slow if self._switched_to_slow else self._fast

	def sleep(self):
		time.sleep(self.get_cooldown())


class LoopState(object):
	@classmethod
	def create(cls, logger, settings):
		return cls(logger, settings["max_allowed_exceptions"])

	def __init__(self, logger, max_allowed_incessant_exceptions):
		self._should_iterate = True
		self._l = logger
		self._iter_count = 0
		self._exception_count = 0
		self._allowed_incessant_exceptions = max_allowed_incessant_exceptions

	def should_iterate(self):
		return self._should_iterate

	def please_stop(self):
		self._l.debug("Loop state asked to stop iterating.")
		self._should_iterate = False

	def iteration_increment(self):
		self._iter_count += 1

	def get_iteration_count(self):
		return self._iter_count

	def on_exception(self):
		self._exception_count += 1
		if self._exception_count >= self._allowed_incessant_exceptions:
			self._l.warn(f"Number of incessant exceptions hits the threshold ({self._allowed_incessant_exceptions}).")
			self._should_iterate = False

	def exception_count_reset(self):
		self._exception_count = 0
	

def main():
	logging.basicConfig(**SETTINGS["logging"])
	logger = logging.getLogger(__name__)

	host_monitor = HostMonitor()
	data_writer = PythonAnywhereWriter()
	cooldown = Cooldown.create(SETTINGS["loop"]["cooldown"])
	writer_state = LoopState.create(logger, SETTINGS["loop"])
	data_to_send = None

	while(writer_state.should_iterate()):
		try:

			# throw away data_to_send if there are new one
			new_data = host_monitor.pollData()
			if new_data is not None:
				data_to_send = new_data

			if data_to_send is not None:
				data_writer.write(data_to_send)
				data_to_send = None

			writer_state.exception_count_reset()
		except:
			logger.error(logging.Formatter().formatException(sys.exc_info()))
			writer_state.on_exception()

		try:
			if writer_state.should_iterate():
				cooldown.update()
				logger.debug(f"Going to sleep for {cooldown.get_cooldown()} seconds.")
				cooldown.sleep()
				writer_state.iteration_increment()
		except KeyboardInterrupt:
			logger.info("Keyboard interrupt.")
			writer_state.please_stop()


if __name__ == "__main__":
	main()
