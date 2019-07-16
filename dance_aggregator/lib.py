from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Event:
    title: str
    instructor: str
    studio: str
    start_datetime: datetime
    end_datetime: datetime
    url: str
    location: Optional[str] = None


class DanceStudioScraper:
    def __init__(self, studio_name: str):
        self.studio_name = studio_name

    def get_events(self) -> List[Event]:
        raise NotImplementedError
