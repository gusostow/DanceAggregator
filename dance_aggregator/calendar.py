import logging
import pathlib
import time
from datetime import datetime
from functools import wraps
from typing import List, Set

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz

from dance_aggregator.models import Event

logger = logging.getLogger("dance_aggregator")

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = str(
    pathlib.Path(__file__).parent.parent
    / "secrets"
    / "danceaggregator-6a8d8b9eac27.json"
)


def login():
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    return build("calendar", "v3", credentials=credentials)


service = login()


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


def make_calendar_event_doc(event: Event) -> dict:
    description = f'''
    Studio: {event.studio}
    Instructor: {event.instructor}
    Url: {event.url}

    Last Crawled: {datetime.now()}
    '''
    event_doc = {
        "summary": event.title,
        "location": event.location,
        "description": description,
        "start": {
            "dateTime": event.start_datetime.isoformat(),
            "timeZone": "America/New_York",
        },
        "end": {
            "dateTime": event.end_datetime.isoformat(),
            "timeZone": "America/New_York",
        },
    }
    return event_doc


@ExponentialBackoff()
def insert_event(event: Event, calendar_id: str) -> None:
    event_doc = make_calendar_event_doc(event)
    logger.info(f"Inserting event: {event.title} {event.start_datetime}")
    service.events().insert(calendarId=calendar_id, body=event_doc).execute()


def get_event_ids(calendar_id: str, time_min=None) -> Set[int]:
    if time_min is None:
        timeMin = None
    else:
        timeMin = (
            datetime.combine(time_min.date(), datetime.min.time())
            .replace(tzinfo=pytz.timezone("US/Eastern"))
            .isoformat()
        )

    events: List[dict] = []
    pageToken = None
    while True:
        response = (
            service.events()
            .list(calendarId=calendar_id, timeMin=timeMin, pageToken=pageToken)
            .execute()
        )
        events += response["items"]
        if "nextPageToken" not in response:
            break
        else:
            pageToken = response["nextPageToken"]

    return {event["id"] for event in events}


@ExponentialBackoff()
def remove_event(event_id: int, calendar_id: str) -> None:
    logger.info(f"Removing event: {event_id}")
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()


def remove_events(calendar_id: str, time_min=datetime.today()):
    event_ids = get_event_ids(calendar_id, time_min=time_min)
    for event_id in event_ids:
        remove_event(event_id, calendar_id)
