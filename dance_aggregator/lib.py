from dataclasses import asdict, dataclass
from datetime import date, time, timedelta
from typing import List, Optional


@dataclass
class Event:
    title: str
    studio: str
    date: date
    start_time: time
    end_time: time
    price: str
    url: str
    location: Optional[str] = None


class DanceStudioScraper:
    def __init__(self, studio_name: str):
        self.studio_name = studio_name

    def scrape_date(self, target_date: date) -> List[Event]:
        raise NotImplementedError

    def get_events(
        self, start_date: Optional[date] = None, n_days: int = 14
    ) -> List[Event]:
        if start_date is None:
            start_date = date.today()
        target_dates = [
            start_date + timedelta(days=offset) for offset in range(n_days + 1)
        ]
        events: List[Event] = []
        for target_date in target_dates:
            events += self.scrape_date(target_date)
        self.events = events
        return events

    def as_records(self) -> List[dict]:
        return [asdict(event) for event in self.events]
