import logging
from typing import List

from dance_aggregator import calendar
from dance_aggregator.models import Event

logger = logging.getLogger("dance_aggregator")


class DanceStudioScraper:
    def __init__(self, studio_name: str):
        self.studio_name = studio_name

    def get_events(self) -> List[Event]:
        raise NotImplementedError

    def update_calendar(self):
        events = self.get_events()
        calendar.remove_events(self.calendar_id)
        for event in events:
            calendar.insert_event(event, self.calendar_id)
