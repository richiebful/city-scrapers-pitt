import datetime
import logging
import re
import time

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class AlleRedevelopmentAuthoritySpider(CityScrapersSpider):
    name = "alle_redevelopment_authority"
    agency = "Redevelopment Authority of Allegheny County"
    timezone = "America/New_York"
    allowed_domains = ["www.alleghenycounty.us"]
    start_urls = [
        "https://www.alleghenycounty.us/economic-development/\
        authorities/meetings-reports/raac/meetings.aspx"
    ]
    month_names = [
        "January", "February", "March", "April", "May", "June", "July", "August", "September",
        "October", "November", "December"
    ]
    month_names_regex = '|'.join(month_names)

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        paras = response.xpath('//p/text()').extract()
        text = '\n'.join(paras)
        meeting_time = self.parse_time(text)

        for paragraph in response.xpath('//p/text()').extract():
            match = re.match(self.month_names_regex, paragraph.strip())
            if not match:
                continue
            else:
                str_meeting_date = paragraph.strip()
                meeting_date = datetime.datetime.strptime(str_meeting_date, '%B %d, %Y')
                meeting = Meeting(
                    title=self.parse_title(paragraph),
                    description=self.parse_description(paragraph),
                    start=self.parse_start(meeting_date, meeting_time),
                    location=self.parse_location(paragraph),
                    source=self.parse_source(response)
                )
                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)
                yield meeting

    def parse_title(self, item):
        """Parse or generate meeting title."""
        return "Meeting"

    def parse_description(self, item):
        """Parse or generate meeting description."""
        return "Monthly meeting"

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return BOARD

    def parse_time(self, item):
        """Parse start datetime as a naive datetime object."""
        time_regex = re.search(r'\d{1,2}:\d{2}[AP]M', item)
        if time_regex:
            logging.debug(time_regex.group(0))
            tm_struct = time.strptime(time_regex.group(0), '%I:%M%p')
            return datetime.time(*tm_struct[3:6])
        else:
            return None

    def parse_start(self, meeting_date, meeting_time):
        return datetime.datetime.combine(meeting_date.date(), meeting_time)
        """Parse or generate location."""
        return {
            "address": "Allegheny County Economic Development",
            "name":
                "Board Room, Suite 900\nChatham One,\
                 112 Washington Place\nPittsburgh, PA 15219",
        }

    def parse_source(self, response):
        """Parse or generate source."""
        return response.url
