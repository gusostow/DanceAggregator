import logging

from dance_aggregator import calendar
from dance_aggregator.studios import gibney


INCLUDED_STUDIOS = [gibney.Gibney]


def main():
    events = []
    for Studio in INCLUDED_STUDIOS:
        studio = Studio()
        logging.info(f"Collecting events for {studio.studio_name}")
        events += studio.get_events()

    if len(events) > 0:
        calendar.remove_upcoming_events()

    for event in events:
        calendar.insert_event(event)


if __name__ == "__main__":
    main()
