from datetime import date

import pytest

from Widgets.calendarEvents import build_week_calendar_events, merge_same_time_overlays
from Widgets.Brick import CalendarBrickData


def test_build_week_events_maps_schedule_to_weekday():
    week_start = date(2026, 10, 5)
    schedule = [{
        'schedule_id': 1,
        'subject_id': 1,
        'day_of_week': 2,
        'start_time': '10:30',
        'duration_minutes': 120,
        'subject_name': 'Programowanie Obiektowe',
        'term_start': '2026-10-05',
        'term_end': '2027-01-30',
    }]

    events = build_week_calendar_events(week_start, schedule)

    assert len(events) == 1
    assert events[0]['date'] == date(2026, 10, 7)
    brick = events[0]['data']
    assert brick.title == 'Programowanie Obiektowe'
    assert brick.start_time == '10:30'
    assert brick.duration_minutes == 120
    assert brick.layout_key == 'schedule-1'
    assert brick.subject_id == 1


def test_build_week_events_normalizes_non_monday_week_start():
    week_start = date(2026, 10, 7)
    schedule = [{
        'schedule_id': 1,
        'subject_id': 1,
        'day_of_week': 0,
        'start_time': '08:00',
        'duration_minutes': 90,
        'subject_name': 'Test',
        'term_start': '2026-10-01',
        'term_end': '2027-01-01',
    }]

    events = build_week_calendar_events(week_start, schedule)

    assert len(events) == 1
    assert events[0]['date'] == date(2026, 10, 5)


def test_build_week_events_respects_term_end():
    week_start = date(2027, 2, 1)
    schedule = [{
        'schedule_id': 1,
        'subject_id': 1,
        'day_of_week': 0,
        'start_time': '08:00',
        'duration_minutes': 90,
        'subject_name': 'PO',
        'term_start': '2026-10-05',
        'term_end': '2027-01-30',
    }]

    events = build_week_calendar_events(week_start, schedule)
    assert events == []


def test_build_week_events_includes_exams():
    week_start = date(2026, 6, 1)
    events = build_week_calendar_events(
        week_start,
        schedule_entries=[],
        timed_events=[{
            'id': 5,
            'subject_id': 2,
            'title': 'Egzamin końcowy',
            'type': 'egzamin',
            'date_time': '2026-06-03 12:00',
            'subject_name': 'Matematyka',
        }],
    )

    assert len(events) == 1
    assert events[0]['date'] == date(2026, 6, 3)
    brick = events[0]['data']
    assert brick.event_type == 'egzamin'
    assert brick.start_time == '12:00'
    assert brick.title == 'Matematyka'
    assert brick.clickable is False


def test_build_week_events_includes_kolokwium():
    week_start = date(2026, 6, 1)
    events = build_week_calendar_events(
        week_start,
        schedule_entries=[],
        timed_events=[{
            'id': 6,
            'subject_id': 3,
            'title': 'Kolokwium 1',
            'type': 'Kolokwium',
            'date_time': '2026-06-04 10:00',
            'subject_name': 'Bazy danych',
        }],
    )

    assert len(events) == 1
    assert events[0]['data'].event_type == 'kolokwium'
    assert events[0]['data'].clickable is False


def test_build_week_events_skips_project_and_other():
    week_start = date(2026, 6, 1)
    timed_events = [
        {
            'id': 7,
            'subject_id': 1,
            'title': 'Projekt',
            'type': 'Projekt',
            'date_time': '2026-06-03 12:00',
            'subject_name': 'Test',
        },
        {
            'id': 8,
            'subject_id': 1,
            'title': 'Inne',
            'type': 'Inne',
            'date_time': '2026-06-04 12:00',
            'subject_name': 'Test',
        },
    ]
    events = build_week_calendar_events(week_start, [], timed_events)
    assert events == []


def test_build_week_events_skips_exam_outside_week():
    week_start = date(2026, 6, 1)
    events = build_week_calendar_events(
        week_start,
        schedule_entries=[],
        timed_events=[{
            'id': 5,
            'subject_id': 2,
            'title': 'Egzamin',
            'type': 'egzamin',
            'date_time': '2026-06-15 12:00',
            'subject_name': 'Matematyka',
        }],
    )
    assert events == []


def test_merge_same_time_overlay_into_lesson():
    lesson = CalendarBrickData(
        id='1',
        subject_id=2,
        layout_key='schedule-1',
        title='Algebra liniowa',
        start_time='09:00',
        duration_minutes=90,
        category_id='2',
        event_type='zajęcia',
    )
    overlay = CalendarBrickData(
        id='2',
        subject_id=2,
        layout_key='event-2',
        title='Algebra liniowa',
        start_time='09:00',
        duration_minutes=90,
        category_id='2',
        event_type='kolokwium',
        clickable=False,
    )

    merged = merge_same_time_overlays([lesson, overlay], lambda t: 'Kolokwium' if t == 'kolokwium' else t)

    assert len(merged) == 1
    assert merged[0].clickable is True
    assert merged[0].overlay_label == 'Kolokwium'
    assert merged[0].overlay_event_type == 'kolokwium'


def test_merge_keeps_standalone_overlay_when_time_differs():
    lesson = CalendarBrickData(
        id='1',
        subject_id=2,
        layout_key='schedule-1',
        title='Bazy danych',
        start_time='08:00',
        duration_minutes=100,
        category_id='2',
        event_type='zajęcia',
    )
    overlay = CalendarBrickData(
        id='2',
        subject_id=2,
        layout_key='event-2',
        title='Bazy danych',
        start_time='14:00',
        duration_minutes=90,
        category_id='2',
        event_type='egzamin',
        clickable=False,
    )

    merged = merge_same_time_overlays([lesson, overlay], lambda t: 'Egzamin')

    assert len(merged) == 2
    assert merged[0].overlay_label is None
    assert merged[1].clickable is False
