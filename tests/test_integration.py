from dance_aggregator.studios import cunningham
from dance_aggregator.studios import dance_wave
from dance_aggregator.studios import gibney
from dance_aggregator.studios import mark_morris
from dance_aggregator.studios import movement_research
from dance_aggregator.studios import peridance


def test_cunningham():
    events = cunningham.Cunningham().get_events()
    assert len(events) > 0


def test_dance_wave():
    events = dance_wave.DanceWave().get_events()
    assert len(events) > 0


def test_gibney():
    events = gibney.Gibney().get_events()
    assert len(events) > 0


def test_mark_morris():
    events = mark_morris.MarkMorris().get_events()
    assert len(events) > 0


def test_movement_research():
    events = movement_research.MovementResearch().get_events()
    assert len(events) > 0


def test_peridance():
    events = peridance.Peridance().get_events()
    assert len(events) > 0
