from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Event:
    title: str
    instructor: str
    studio: str
    start_datetime: datetime
    end_datetime: datetime
    url: str
    location: Optional[str] = None
