from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
import pdfquery
import logging
import datetime
import re
import requests
import io

class PaUtilitySpider(CityScrapersSpider):
    name = "pa_utility"
    agency = "PA Utility Commission"
    timezone = "America/New_York"
    allowed_domains = ["www.puc.state.pa.us"]
    start_urls = ["http://www.puc.state.pa.us/about_puc/public_meeting_calendar.aspx"]
    month_names = [
        "January", "February", "March", "April", "May", "June", "July", "August", "September",
        "October", "November", "December"
    ]

    def parse(self, response):
        """
        parse yields meeting items scraped from the PDFs
        """
        now = datetime.datetime.now()
        years = [2021]
#        years = [now.year, now.year + 1]
        for year in years:
            mtg_generator = self.parse_pdf(year)
            for mtg in mtg_generator:
                yield mtg

    def parse_pdf(self, year):
        #load pdf from url and place into file-like object
        pdf_url = 'http://www.puc.state.pa.us/General/pm_agendas/{0}/{0}_PM_Schedule.pdf'.format(year)
        resp = requests.get(pdf_url, stream=True)
        if not resp.ok:
            return
        resp.raw.decode_content = True
        contents = bytearray()
        for chunk in resp.iter_content(chunk_size=128):
            contents += chunk
        fp = io.BytesIO(contents)
        pdf = pdfquery.PDFQuery(fp)
        pdf.load()
        selections = [pdf.pq('LTTextLineHorizontal:contains("{0}")'.format(m)) for m in self.month_names]
        logging.debug(selections[0])
        monthly_dates = [s.text() for s in selections]
        str_dates = []
        for d in monthly_dates:
            str_dates += re.split('(?<=\d) ', d)

        dt_dates = []
        for d in str_dates:
            try:
                dt_dates.append(datetime.datetime.strptime(d, '%B %d, %Y'))
            except:
                continue
        
        for dt in dt_dates:
            meeting = Meeting(
                title=self._parse_title(None),
                description=self._parse_description(None),
                classification=self._parse_classification(None),
                start=self._parse_start(dt),
                time_notes=self._parse_time_notes(None),
                location=self._parse_location(None),
                source=self._parse_source(None),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

       
    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return "Public Meeting"

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return self._parse_time_notes(item)

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, dt):
        """Parse start datetime as a naive datetime object."""
        return datetime.datetime.combine(dt.date(), datetime.time(10, 0, 0))

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return "The Commission holds Public Meetings on Thursdays (unless otherwise noted) at 10 AM in Hearing Room No. 1 at the Commonwealth Keystone Building in Harrisburg."

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "400 North St, Harrisburg, PA 17120",
            "name": "Commonwealth Keystone Building, Hearing Room No. 1"
        }

    def _parse_source(self, response):
        """Parse or generate source."""
        return self.start_urls[0]
