import logging
import time
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from typing import List, Optional

from googleapiclient.errors import HttpError

logger = logging.getLogger("dance_aggregator")


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


class ExponentialBackoff:
    def __init__(self, initial_wait_secs=1, max_wait_secs=8):
        self.initial_wait_secs = initial_wait_secs
        self.max_wait_secs = max_wait_secs

    def __call__(self, fn, *args, **kwargs):
        @wraps(fn)
        def retry_fn(*args, **kwargs):
            sleeps = [self.initial_wait_secs]
            wait = sleeps[-1]
            while wait <= self.max_wait_secs:
                wait *= 2
                sleeps.append(wait)

            for sleep in sleeps:
                try:
                    fn(*args, **kwargs)
                    break
                except HttpError as e:
                    logger.info(f"Http error: backing off for {sleep}s - {e}")
                    time.sleep(sleep)

        return retry_fn
