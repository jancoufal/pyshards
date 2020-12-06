import typing
from ..settings import Settings
from ..sources import Source


class Base(object):
	def __init__(self, source: Source, settings: Settings):
		self._settings = settings
		self._source = source
