import logging

from dance_aggregator import calendar

from dance_aggregator.studios.dance_wave import DanceWave
from dance_aggregator.studios.gibney import Gibney
from dance_aggregator.studios.movement_research import MovementResearch


handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)8s %(name)s | %(message)s")
handler.setFormatter(formatter)
logger = logging.getLogger("dance_aggregator")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

INCLUDED_STUDIOS = (
    (Gibney(), "87nse6kec4lkia3dumm4hi92p0@group.calendar.google.com"),
    (MovementResearch(), "nk9j7d6s2bcovajull5hf7i5j4@group.calendar.google.com"),
    (DanceWave(), "2n577qjvg1bdoorj12d0hhh75o@group.calendar.google.com"),
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
