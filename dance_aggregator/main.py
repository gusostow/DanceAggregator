import logging

from dance_aggregator import calendar

# from dance_aggregator.lib import exponential_backoff
from dance_aggregator.studios import gibney


handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)8s %(name)s | %(message)s")
handler.setFormatter(formatter)
logger = logging.getLogger("dance_aggregator")
logger.addHandler(handler)
logger.setLevel(logging.INFO)  # This toggles all the logging in your app

INCLUDED_STUDIOS = [gibney.Gibney]


def main():
    events = []
    for Studio in INCLUDED_STUDIOS:
        studio = Studio()
        logger.info(f"Collecting events for {studio.studio_name}")
        events += studio.get_events()

    if len(events) > 0:
        calendar.remove_events()

    for event in events:
        calendar.insert_event(event)


if __name__ == "__main__":
    main()
