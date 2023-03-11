import requests
import socket
import time


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
		self._hostname = hostname
		self._ip_list = ip_list

	def __eq__(self, other):
		return other._hostname == self._hostname and other._ip_list == self._ip_list

	def __str__(self):
		return f"Host: {self._hostname}, IP: {', '.join(self._ip_list)}"


ORACLE_PROXY = "http://emea-proxy.uk.oracle.com:80"

proxy_dict = {
	"http": ORACLE_PROXY,
	"https": ORACLE_PROXY,
}

res = requests.post(
	"http://griffin42.pythonanywhere.com/post/ksodfsdf/",
	# timeout=30,
	json={"time": time.time(), "ips": str(MonitorData.create())},
	proxies=proxy_dict
)

print(res)

