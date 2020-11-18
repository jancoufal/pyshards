from .sources import Source
from .settings import Settings
from .impl import noop, roumen


def create(source: Source, settings: Settings):
	scrapper_classes = {
		Source.ROUMEN: roumen.Roumen,
		# Source.ROUMEN_MASO: scrapper_impl.RoumenMaso,
	}

	scrapper_class = scrapper_classes.get(source, noop.Null)
	return scrapper_class(settings)
