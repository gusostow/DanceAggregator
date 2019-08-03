import logging
import pytz
import re
from datetime import date, datetime, timedelta
from dateutil import parser
from typing import Optional, List

import bs4
from bs4.element import Tag
import requests

from dance_aggregator.lib import DanceStudioScraper, Event

logger = logging.getLogger("dance_aggregator")


class DanceWave(DanceStudioScraper):
    def __init__(self):
        super().__init__(studio_name="Dancewave")
        self.calendar_id = "2n577qjvg1bdoorj12d0hhh75o@group.calendar.google.com"

    def make_event_record(self, event_div: Tag) -> Optional[Event]:
        title = event_div.find("span", {"class": "simcal-event-title"}).text
        try:
            instructor = event_div.find(
                "div", {"class": "simcal-event-description"}
            ).p.text

            eastern = pytz.timezone("US/Eastern")
            start_datetime = eastern.localize(
                parser.parse(
                    event_div.find("span", {"class": "simcal-event-start-date"}).get(
                        "content"
                    ),
                    ignoretz=True,
                )
            )
            end_datetime = eastern.localize(
                parser.parse(
                    event_div.find("span", {"class": "simcal-event-end-time"}).get(
                        "content"
                    ),
                    ignoretz=True,
                )
            )
        except AttributeError:  # "Dance wave is closed"
            logger.warning(f"Unable to parse event: '{title}'")
            return None
        location = event_div.find("span", {"class": "simcal-event-address"}).meta.get(
            "content"
        )
        event = Event(
            title=title,
            instructor=instructor,
            studio=self.studio_name,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            url="https://dancewave.org/adult-classes/",
            location=location,
        )
        return event

    def get_events(self) -> List[Event]:
        calendar_soup = bs4.BeautifulSoup(
            requests.get("https://dancewave.org/adult-classes/").content,
            features="lxml",
        )

        event_divs = calendar_soup.find_all(
            "div", {"class": re.compile(r"^simcal-fullcal-qtip-id")}
        )

        max_event_datetime = datetime.today() + timedelta(days=60)
        events: List[Event] = []
        for event_div in event_divs:
            event = self.make_event_record(event_div)
            if event is not None:
                if event.start_datetime.replace(tzinfo=None) > max_event_datetime:
                    break
                elif event.start_datetime.date() >= date.today():
                    events.append(event)
        return events
