from datetime import datetime
import pathlib
from typing import Set

from google.oauth2 import service_account
from googleapiclient.discovery import build
import pytz

from dance_aggregator.lib import Event

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
    service.events().insert(calendarId=CALENDAR_ID, body=event_doc).execute()


def get_event_ids(time_min=datetime.today()) -> Set[int]:
    if time_min is None:
        timeMin = None
    else:
        timeMin = (
            datetime.combine(time_min.date(), datetime.min.time())
            .replace(tzinfo=pytz.timezone("US/Eastern"))
            .isoformat()
        )

    events = []
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


def remove_upcoming_events():
    event_ids = get_event_ids()
    for event_id in event_ids:
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()


def nuke_all_events():
    event_ids = get_event_ids(time_min=None)
    for event_id in event_ids:
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
