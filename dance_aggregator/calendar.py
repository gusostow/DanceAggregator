from datetime import datetime
import pathlib

from google.oauth2 import service_account
from googleapiclient.discovery import build

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
    Price: {event.price}
    Url: {event.url}

    Last Crawled: {datetime.now()}
    '''
    start_datetime, end_datetime = (
        datetime.combine(event.date, event.start_time).isoformat(),
        datetime.combine(event.date, event.end_time).isoformat(),
    )
    event_doc = {
        "summary": event.title,
        "location": event.location,
        "description": description,
        "start": {"dateTime": start_datetime, "timeZone": "America/New_York"},
        "end": {"dateTime": end_datetime, "timeZone": "America/New_York"},
    }

    return event_doc


def insert_event(event: Event) -> None:
    event_doc = make_calendar_event_doc(event)
    service.events().insert(calendarId=CALENDAR_ID, body=event_doc).execute()
