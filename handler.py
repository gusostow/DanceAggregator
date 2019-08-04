from dance_aggregator.studios import cunningham
from dance_aggregator.studios import dance_wave
from dance_aggregator.studios import gibney
from dance_aggregator.studios import mark_morris
from dance_aggregator.studios import movement_research
from dance_aggregator.studios import peridance


def cunningham_handler(event, context):
    cunningham.Cunningham().update_calendar()


def dance_wave_handler(event, context):
    dance_wave.DanceWave().update_calendar()


def gibney_handler(event, context):
    gibney.Gibney().update_calendar()


def mark_morris_handler(event, context):
    mark_morris.MarkMorris().update_calendar()


def movement_research_handler(event, context):
    movement_research.MovementResearch().update_calendar()


def peridance_handler(event, context):
    peridance.Peridance().update_calendar()
