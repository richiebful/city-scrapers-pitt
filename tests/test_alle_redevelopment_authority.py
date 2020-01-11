from os.path import dirname, join
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from city_scrapers.spiders.alle_redevelopment_authority import AlleRedevelopmentAuthoritySpider

test_response = file_response(
    join(dirname(__file__), "files", "alle_redevelopment_authority.html"),
    url="https://www.alleghenycounty.us/\
    economic-development/authorities/meetings-reports/raac/meetings.aspx",
)
spider = AlleRedevelopmentAuthoritySpider()

freezer = freeze_time("2019-10-13")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()
