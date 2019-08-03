import logging

from dance_aggregator.studios.cunningham import Cunningham
from dance_aggregator.studios.dance_wave import DanceWave
from dance_aggregator.studios.gibney import Gibney
from dance_aggregator.studios.mark_morris import MarkMorris
from dance_aggregator.studios.movement_research import MovementResearch
from dance_aggregator.studios.peridance import Peridance


logger = logging.getLogger("dance_aggregator")

INCLUDED_STUDIOS = (
    Cunningham(),
    DanceWave(),
    Gibney(),
    MarkMorris(),
    MovementResearch(),
    Peridance(),
)


def main():
    for studio in INCLUDED_STUDIOS:
        logger.info(f"Collecting events from {studio.studio_name}")
        studio.update_calendar()


if __name__ == "__main__":
    main()
