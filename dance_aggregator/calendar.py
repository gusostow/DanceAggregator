import logging
import pathlib
from datetime import datetime
from typing import List, Set

from google.oauth2 import service_account
from googleapiclient.discovery import build
import pytz

from dance_aggregator.lib import Event

logger = logging.getLogger("dance_aggregator")

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = str(
    pathlib.Path(__file__).parent.parent
    / "secrets"
    / "danceaggregator-6a8d8b9eac27.json"
)
CALENDAR_ID = "87nse6kec4lkia3dumm4hi92p0@group.calendar.google.com"


def login():
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    return build("calendar", "v3", credentials=credentials)


service = login()


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


def insert_event(event: Event) -> None:
    event_doc = make_calendar_event_doc(event)
    logger.info(f"Inserting event: {event.title}")
    service.events().insert(calendarId=CALENDAR_ID, body=event_doc).execute()


def get_event_ids(time_min=None) -> Set[int]:
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
            .list(calendarId=CALENDAR_ID, timeMin=timeMin, pageToken=pageToken)
            .execute()
        )
        events += response["items"]
        if "nextPageToken" not in response:
            break
        else:
            pageToken = response["nextPageToken"]

    return {event["id"] for event in events}


def remove_events(time_min=datetime.today()):
    event_ids = get_event_ids(time_min=time_min)
    for event_id in event_ids:
        logger.info(f"Removing event: {event_id}")
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
