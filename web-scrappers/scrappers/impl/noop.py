from ..settings import Settings
from ..result import Result

class Null(object):
	def __init__(self, settings: Settings):
		pass

	def scrap(self):
		result = Result()
		result.on_scrapping_finished()
		return result
