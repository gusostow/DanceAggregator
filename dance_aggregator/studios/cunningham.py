import logging
from datetime import datetime
from dateutil import parser
from typing import List

import bs4
from bs4.element import Tag
import requests

from dance_aggregator.lib import DanceStudioScraper, Event

logger = logging.getLogger("dance_aggregator")


class Cunningham(DanceStudioScraper):
    def __init__(self):
        super().__init__(studio_name="Cunningham Trust")

    def event_from_row(self, row_soup: Tag) -> Event:
        spans = row_soup.find_all("span")

        time_raw: str = spans[0].text
        instructor: str = spans[2].text
        location: str = spans[4].text

        title = f"{instructor}'s Class"

        day_raw, times_raw = time_raw.split(",")[1:]
        start_raw, end_raw = times_raw.split(" -")
        start_datetime_raw = f"{day_raw} {start_raw}"
        end_datetime_raw = f"{day_raw} {end_raw.strip()}"

        start_datetime = parser.parse(start_datetime_raw)
        end_datetime = parser.parse(end_datetime_raw)

        event = Event(
            title=title,
            instructor=instructor,
            studio=self.studio_name,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            url="https://www.mercecunningham.org/activities/classes/",
            location=location,
        )
        return event

    def get_events(self) -> List[Event]:
        page_soup = bs4.BeautifulSoup(
            requests.get("https://www.mercecunningham.org/activities/classes/").content,
            features="lxml",
        )
        this_week_soup = page_soup.find("section", {"id": "schedule"})
        schedule_rows = this_week_soup.find_all(
            "div", {"class": "table__row filter-bar-content__item"}
        )
        output: List[Event] = []
        for row in schedule_rows:
            event = self.event_from_row(row)
            if event.start_datetime.date() >= datetime.today().date():
                output.append(event)
        return output
