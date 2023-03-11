import sys
import logging
import socket
import socks
import time

SETTINGS = {
	"proxies": {
		"http": "http://emea-proxy.uk.oracle.com",
		"https": "http://emea-proxy.uk.oracle.com",
	},
	"irc": {
		"server": "irc.felk.cvut.cz",
		"port": 6667,
		"botnick": "xertex",
		"botpass": "xertex666",
		"botnickpass": "xertex666",
	},
	"logging": {
		"level": logging.DEBUG,
		"format": "%(asctime)s - %(levelname)s : %(message)s",
		"datefmt": "%Y-%m-%d %H:%M:%S",
	},
}

class IrcBot(object):

	ENCODING = "UTF-8"

	def __init__(self, logger):
		self._l = logging
		self._s = socks.socksocket()
		self._s.set_proxy(socks.HTTP, SETTINGS["proxies"]["http"], 80)
		self._irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def _send_line(self, text):
		self._irc.send(bytes(f"{text}\n", IrcBot.ENCODING))

	def connect(self, server, port, botnick, botpass, botnickpass):
		self._l.info(f"Connecting to {server}:{port}")
		self._irc.connect((server, port))

		# wait till the MOTD passes
		time.sleep(30)

		# user auth
		self._send_line(f"NICK {botnick}")
		self._send_line(f"USER {botnick} {botnick} {botnick} :python")
		self._send_line(f"NICKSERV {botnickpass} {botpass}")
		time.sleep(5)

	def join(self, channel):
		self._l.info(f"Joining {channel}")
		self._send_line(f"JOIN {channel}")

	def send(self, channel, message):
		self._send_line(f"PRIVMSG {channel} {message}")
	
	def get_response(self):
		time.sleep(1)
		resp = self._irc.recv(2048).decode(IrcBot.ENCODING)

		self._l.debug(resp)

		if resp.find("PING") != -1:
			self._send_line(f"PONG {resp.split().decode(IrcBot.ENCODING)[1]}\r")

		return resp


def main():
	logging.basicConfig(**SETTINGS["logging"])
	logger = logging.getLogger(__name__)
	logger.addHandler(logging.StreamHandler(sys.stdout))

	irc = IrcBot(logger)
	irc.connect(**SETTINGS["irc"])

	irc.join("#xertex")

	while(True):
		text = irc.get_response()
		logging.debug(f"irc> {text}")

if __name__ == "__main__":
	main()
