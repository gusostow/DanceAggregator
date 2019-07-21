import pytz
from dateutil import parser
from typing import List

import bs4
from bs4.element import Tag
import requests

from dance_aggregator.lib import DanceStudioScraper, Event


def make_event_record(studio_name: str, row_soup: Tag) -> Event:
    title = row_soup.find("span", {"class": "classname"}).text.strip()
    instructor = row_soup.find("td", {"class": "trainer"}).text.strip()

    eastern = pytz.timezone("US/Eastern")

    start_time = (
        row_soup.find("span", attrs={"class": "hc_starttime"})
        .get("data-datetime")
        .replace('"', "")
    )
    start_datetime = eastern.localize(parser.parse(start_time, ignoretz=True))
    end_time = (
        row_soup.find("span", attrs={"class": "hc_endtime"})
        .get("data-datetime")
        .replace('"', "")
    )
    end_datetime = eastern.localize(parser.parse(end_time, ignoretz=True))

    url = row_soup.find("span", {"class": "classname"}).a.get("data-url")

    class_page_soup = bs4.BeautifulSoup(requests.get(url).content, features="lxml")
    location = class_page_soup.find(
        "div", {"class": "class_description"}
    ).span.text.split(": ")[-1]

    return Event(
        title=title,
        url=url,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        studio=studio_name,
        instructor=instructor,
        location=location,
    )


class Gibney(DanceStudioScraper):
    def __init__(self):
        super().__init__(studio_name="Gibney Dance")
        self.soup = bs4.BeautifulSoup(
            requests.get(
                "https://widgets.healcode.com/widgets/schedules/00108315175.json?mobile=false&version=0.1"
            ).json()["contents"],
            features="lxml",
        )

    def get_events(self) -> List[Event]:
        event_soups = [
            soup
            for soup in self.soup.find_all("tr")
            if soup.get("class").pop() != "schedule_header"
        ]

        events = []
        for event_row in event_soups:
            events.append(make_event_record(self.studio_name, event_row))
        return events
