import logging

from dance_aggregator import calendar

# from dance_aggregator.lib import exponential_backoff
from dance_aggregator.studios import gibney, movement_research


handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)8s %(name)s | %(message)s")
handler.setFormatter(formatter)
logger = logging.getLogger("dance_aggregator")
logger.addHandler(handler)
logger.setLevel(logging.INFO)  # This toggles all the logging in your app

INCLUDED_STUDIOS = (
    (gibney.Gibney(), "87nse6kec4lkia3dumm4hi92p0@group.calendar.google.com"),
    (
        movement_research.MovementResearch(),
        "nk9j7d6s2bcovajull5hf7i5j4@group.calendar.google.com",
    ),
)


def main():
    for studio, calendar_id in INCLUDED_STUDIOS:
        logger.info(f"Collecting events from {studio.studio_name}")
        events = studio.get_events()

        if len(events) > 0:
            calendar.remove_events(calendar_id)

        for event in events:
            calendar.insert_event(event, calendar_id)


if __name__ == "__main__":
    main()
