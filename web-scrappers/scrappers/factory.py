from .sources import Source
from .settings import Settings
from .impl import Null, Roumen


def create(source: Source, settings: Settings):
	scrapper_classes = {
		Source.ROUMEN: Roumen,
		# Source.ROUMEN_MASO: RoumenMaso,
	}

	scrapper_class = scrapper_classes.get(source, Null)
	return scrapper_class(settings)
