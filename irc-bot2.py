#! /usr/bin/env python
#
# Example program using irc.bot.
#
# Joel Rosdahl <joel@rosdahl.net>

import sys, socket
import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
import logging

# ugly global/singleton logger
l = None

SETTINGS = {
	"logging": {
		"level": logging.DEBUG,
		"format": "%(asctime)s - %(levelname)s : %(message)s",
		"datefmt": "%Y-%m-%d %H:%M:%S",
	},
	"irc": {
		"server": "irc.felk.cvut.cz",
		"port": 6667,
		"nickname": "xerbot",
		"channel": "#xertex",
	},
	"proxies": {
		"http": "http://emea-proxy.uk.oracle.com",
		"https": "http://emea-proxy.uk.oracle.com",
	},
}


class TestBot(irc.bot.SingleServerIRCBot):
	def __init__(self, channel, nickname, server, port=6667):
		l.debug(f"Bot > init: {channel=}, {nickname=}, {server=}, {port=}")
		irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
		self.channel = channel

	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + "_")

	def on_welcome(self, c, e):
		l.debug(f"Bot > on_welcone: joining {self.channel=}")
		c.join(self.channel)

	def on_privmsg(self, c, e):
		l.debug(f"Bot > on_privmsg: {e.arguments=}")
		self.do_command(e, e.arguments[0])

	def on_pubmsg(self, c, e):
		l.debug(f"Bot > on_pubmsg: {e.arguments=}")
		a = e.arguments[0].split(":", 1)
		if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()):
			self.do_command(e, a[1].strip())
		return

	def on_dccmsg(self, c, e):
		# non-chat DCC messages are raw bytes; decode as text
		l.debug(f"Bot > on_dccmsg: {e.arguments=}")
		text = e.arguments[0].decode('utf-8')
		c.privmsg("You said: " + text)

	def on_dccchat(self, c, e):
		l.debug(f"Bot > on_dccchat: {e.arguments=}")		
		if len(e.arguments) != 2:
			return
		args = e.arguments[1].split()
		if len(args) == 4:
			try:
				address = ip_numstr_to_quad(args[2])
				port = int(args[3])
			except ValueError:
				return
		self.dcc_connect(address, port)

	def do_command(self, e, cmd):
		l.debug(f"Bot > do_command: {e.source.nick=}, {cmd=}")
		nick = e.source.nick
		c = self.connection

		if cmd == "disconnect":
			self.disconnect()
		elif cmd == "die":
			self.die()
		elif cmd == "hi":
			c.notice(nick, "hi")
		elif cmd == "host":
			c.notice(nick, socket.gethostname())
		elif cmd == "ip":
			c.notice(nick, ", ".join(socket.gethostbyname_ex(socket.gethostname())[-1]))
		else:
			c.notice(nick, "Not understood: " + cmd)


def main():
	global l
	logging.basicConfig(**SETTINGS["logging"])
	l = logging.getLogger(__name__)
	# l.addHandler(logging.StreamHandler(sys.stdout))

	l.info("Initializing bot...")
	bot = TestBot(**SETTINGS["irc"])

	l.info("Running bot...")
	bot.start()

	l.info("Finished.")

if __name__ == "__main__":
	main()
