from datetime import date, datetime, time
from typing import List, Tuple

import bs4
from bs4.element import ResultSet, Tag
import requests

from dance_aggregator.lib import DanceStudioScraper, Event


def get_event_soups(date: date) -> ResultSet:
    date_str = date.strftime("%Y-%m-%d")

    url = f"https://gibneydance.org/calendar/{date_str}/"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(
            f"Gibney responded with status code {response.status_code} - {response.content}"
        )

    soup = bs4.BeautifulSoup(response.content, features="html.parser")
    return soup.find_all(attrs={"class": "type-tribe_events"})


def parse_time_range(timerange: str) -> Tuple[time, time]:
    start, end = timerange.split(" – ")
    fmt = "%I:%M %p"
    start_time, end_time = (
        datetime.strptime(start, fmt).time(),
        datetime.strptime(end, fmt).time(),
    )
    return start_time, end_time


def make_event_record(studio_name: str, event_date: date, event_soup: Tag) -> Event:
    title = event_soup.find(
        name="h2", attrs={"class": "tribe-events-list-event-title"}
    ).text.strip()

    url = event_soup.a.get("href")

    info_box = event_soup.find(name="div", attrs={"class": "tribe-events-event-meta"})

    time_range: str = info_box.div.text.strip()
    start_time, end_time = parse_time_range(time_range)

    price: str = info_box.find_all(name="p")[1].text.strip()

    # Need to follow link to get location
    event_page_soup = bs4.BeautifulSoup(
        requests.get(url).content, features="html.parser"
    )
    info_paragraphs = event_page_soup.find_all("p")
    location = info_paragraphs[2].a.text.strip()

    return Event(
        title=title,
        url=url,
        date=event_date,
        start_time=start_time,
        end_time=end_time,
        price=price,
        studio=studio_name,
        location=location,
    )


class Gibney(DanceStudioScraper):
    def __init__(self, *args, **kwargs):
        super().__init__(studio_name="Gibney Dance")

    def scrape_date(self, target_date: date) -> List[Event]:
        event_soups = get_event_soups(target_date)
        records = [
            make_event_record(self.studio_name, target_date, soup)
            for soup in event_soups
        ]
        return records
