import logging
import re
from datetime import datetime, timedelta
from dateutil import parser
from typing import List

import bs4
from bs4.element import Tag
import requests

from dance_aggregator.lib import DanceStudioScraper, Event

logger = logging.getLogger("dance_aggregator")


class MarkMorris(DanceStudioScraper):
    def __init__(self):
        super().__init__(studio_name="Mark Morris")

    def make_event_record(self, session_soup: Tag) -> Event:
        title = session_soup.find("div", {"class": "bw-session__name"}).text.strip()

        instructor = session_soup.find(
            "div", {"class": "bw-session__staff"}
        ).text.strip()
        if "substitute" in instructor:
            instructor = " ".join(instructor.split("            "))
        start_datetime = parser.parse(
            session_soup.find("time", {"class": "hc_starttime"}).get("datetime")
        )
        end_datetime = parser.parse(
            session_soup.find("time", {"class": "hc_endtime"}).get("datetime")
        )
        location_tag = session_soup.find("div", {"class": "bw-session__room"})
        address = "3 Lafayette Avenue Brooklyn, NY 11217-1415"
        if location_tag is not None:
            room = location_tag.text.strip()
            location = f"{room}, {address}"
        else:
            location = address

        event = Event(
            title=title,
            instructor=instructor,
            studio=self.studio_name,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            url="https://markmorrisdancegroup.org/adult-class-schedule/",
            location=location,
        )
        return event

    def get_events(self) -> List[Event]:
        output: List[Event] = []
        for weeks_ahead in range(4):
            week_start = (
                datetime.today().date() + timedelta(days=7 * weeks_ahead)
            ).strftime("%Y-%m-%d")
            week_content = requests.get(
                "https://widgets.healcode.com/widgets/schedules/46238/load_markup?callback=jQuery18104966069031035696_1564355963232&_=1564356012761",
                params={"options[start_date]": week_start},
            )
            raw = (
                week_content.content.decode("unicode-escape")
                .encode("ISO-8859-1")
                .decode()
                .replace(
                    "\n", ""
                )  # Clean mess of encodings escape characters discovered via trial and error
            )

            html: str = re.search(r'{"class_sessions":"(.+)","filters', raw).group(1)
            soup = bs4.BeautifulSoup(html, features="lxml")

            sessions = soup.find_all("div", "bw-session")
            output += [
                self.make_event_record(session_tag)
                for session_tag in sessions
                if "bw-session--empty" not in session_tag.get("class")
            ]
        return output
