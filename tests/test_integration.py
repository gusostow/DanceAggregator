from dance_aggregator.studios import cunningham
from dance_aggregator.studios import dance_wave
from dance_aggregator.studios import gibney
from dance_aggregator.studios import mark_morris
from dance_aggregator.studios import movement_research
from dance_aggregator.studios import peridance


def test_cunningham():
    cunningham.Cunningham().get_events()


def test_dance_wave():
    dance_wave.DanceWave().get_events()


def test_gibney():
    gibney.Gibney().get_events()


def test_mark_morris():
    mark_morris.MarkMorris().get_events()


def test_movement_research():
    movement_research.MovementResearch().get_events()


def test_peridance():
    peridance.Peridance().get_events()
