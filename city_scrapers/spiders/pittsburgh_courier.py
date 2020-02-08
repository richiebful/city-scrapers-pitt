from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
import logging
import scrapy


class PittsburghCourierSpider(CityScrapersSpider):
    name = "pittsburgh_courier"
    agency = "New Pittsburgh Courier"
    timezone = "America/New_York"
    url_template = "https://newpittsburghcourier.com/category/classifieds/page/{0}/"

    def start_requests(self):
        try:
            for i in range(1, 100):
                url = self.url_template.format(str(i))
                logging.debug(url)
                yield scrapy.Request(url, self.parse_toc)
        except Exception as e:
            raise e

    def parse_toc(self, response):
        """
        Parse 'table of contents' pages to get to weekly
        meetings
        """
        for url in response.xpath("a[contains(@title, 'Meetings')]/@href").extract():
            yield scrapy.Request(url, self.parse_meeting)

    def parse_meeting(self, response):
        yield response.url

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return ""

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        return None

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
