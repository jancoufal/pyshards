from scrapper_enum import ScrapSource
from scrapper_holders import ScrapperSettings
import scrapper_impl


def create_scrapper(source: ScrapSource, settings: ScrapperSettings):
	scrapper_classes = {
		ScrapSource.ROUMEN: scrapper_impl.Roumen,
		ScrapSource.ROUMEN_MASO: scrapper_impl.RoumenMaso,
	}

	scrapper_class = scrapper_classes.get(source, scrapper_impl.Null)
	return scrapper_class(settings)
