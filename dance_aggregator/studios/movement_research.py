import pytz
from datetime import datetime
from typing import List
from urllib.parse import unquote

import requests

from dance_aggregator.lib import DanceStudioScraper, Event

STUDIO = "Movement Research"


def get_raw_json(date=datetime.today()):
    first_this_month = date.replace(day=1)
    try:
        first_next_month = first_this_month.replace(month=first_this_month.month + 1)
    except ValueError:
        first_next_month = first_this_month.replace(
            year=first_this_month.year + 1, month=1
        )

    first_this_month_str = first_this_month.strftime("%Y-%m-%d")
    first_next_month_str = first_next_month.strftime("%Y-%m-%d")

    base_url = "https://movementresearch.org/calendar/month.json"
    this_month_calendar: dict = requests.get(
        base_url, params={"d": first_this_month_str}
    ).json()
    next_month_calendar: dict = requests.get(
        base_url, params={"d": first_next_month_str}
    ).json()

    return this_month_calendar, next_month_calendar


def make_day_event_records(day: dict) -> List[Event]:
    date_str = day["date"].split(" ")[0]
    eastern = pytz.timezone("US/Eastern")

    records: List[Event] = []
    for event in day["events"].get("class", []):
        start_datetime = eastern.localize(
            datetime.strptime(f"{date_str} {event['start']}", "%Y-%m-%d %I:%M%p")
        )
        end_datetime = eastern.localize(
            datetime.strptime(f"{date_str} {event['end']}", "%Y-%m-%d %I:%M%p")
        )
        record = Event(
            title=unquote(event["title"]),
            instructor=event["instructor"],
            studio=STUDIO,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            url=f"https://movementresearch.org/event/{event['url']}",
            location=unquote(event["locationName"].replace("&#039;", "'")),
        )
        records.append(record)

    return records


class MovementResearch(DanceStudioScraper):
    def __init__(self):
        super().__init__(studio_name=STUDIO)
        self.calendar_id = "nk9j7d6s2bcovajull5hf7i5j4@group.calendar.google.com"

    def get_events(self) -> List[Event]:
        this_month_calendar, next_month_calendar = get_raw_json()

        # Process days today and greater for this month calendar
        this_month_days = [
            day
            for week in this_month_calendar["weeks"]
            for day in week
            if not (day["isPrevMonth"] or day["isNextMonth"])
        ]
        next_month_days = [
            day
            for week in next_month_calendar["weeks"]
            for day in week
            if day["isNextMonth"]
        ]
        upcoming_days = [
            day for day in this_month_days if int(day["number"]) >= datetime.today().day
        ] + next_month_days

        events = [
            event for day in upcoming_days for event in make_day_event_records(day)
        ]
        return events
