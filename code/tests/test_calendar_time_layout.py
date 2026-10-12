import pytest
from dataclasses import dataclass

from Widgets.calendarTimeLayout import (
    CalendarTimeConfig,
    format_duration_label,
    format_event_info,
    layout_timed_events,
    parse_time,
)


@dataclass
class _EventStub:
    id: str
    start_time: str
    duration_minutes: int


def test_parse_time():
    assert parse_time("08:30") == 8 * 60 + 30


def test_format_duration_label_hours():
    assert format_duration_label(90) == "1,5 h"
    assert format_duration_label(120) == "2 h"


def test_format_event_info():
    assert format_event_info("10:30", 90) == "10:30 | 1,5 h"


def test_layout_single_event_position():
    events = [_EventStub(id="1", start_time="10:00", duration_minutes=90)]
    config = CalendarTimeConfig(start_hour=7, end_hour=21, pixels_per_minute=2.0)
    layouts = layout_timed_events(events, config)

    assert len(layouts) == 1
    assert layouts[0].height == 90 * 2.0
    assert layouts[0].y == config.event_y(10 * 60, layouts[0].height)
    assert layouts[0].width_fraction == 1.0
    assert layouts[0].x_fraction == 0.0


def test_layout_short_event_uses_min_height():
    events = [_EventStub(id="1", start_time="08:00", duration_minutes=10)]
    config = CalendarTimeConfig(min_event_height=28.0, pixels_per_minute=2.0)
    layouts = layout_timed_events(events, config)

    assert layouts[0].height == 28.0


def test_layout_overlapping_events_split_width():
    events = [
        _EventStub(id="1", start_time="08:00", duration_minutes=90),
        _EventStub(id="2", start_time="08:00", duration_minutes=90),
    ]
    layouts = layout_timed_events(events)

    by_id = {layout.event_id: layout for layout in layouts}
    assert by_id["1"].width_fraction == 0.5
    assert by_id["2"].width_fraction == 0.5
    assert by_id["1"].x_fraction == 0.0
    assert by_id["2"].x_fraction == 0.5


def test_calendar_time_config_grid_height():
    config = CalendarTimeConfig(start_hour=7, end_hour=21, pixels_per_minute=2.0)
    assert config.grid_height == 14 * 60 * 2.0


def test_layout_empty_events():
    assert layout_timed_events([]) == []


def test_hour_y_places_morning_at_top():
    config = CalendarTimeConfig(start_hour=7, end_hour=21, pixels_per_minute=2.0)
    assert config.hour_y(7) > config.hour_y(12)
    assert config.hour_y(12) > config.hour_y(21)
