import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch
from KivyWidgets.calendarWidget import CalendarWidget
from Widgets.Brick import CalendarBrickData
from style.Colors import ThemeManager

@pytest.fixture
def mock_calendar():
    with patch('KivyWidgets.calendarWidget.CalendarWidget.on_kv_post'):
        app = MagicMock()
        app.language = "pl"
        app.theme = ThemeManager()
        repo = MagicMock()
        repo.get_all_schedule_entries.return_value = []
        repo.get_events_in_range.return_value = []
        cal = CalendarWidget()
        cal.app = app
        cal.repo = repo
        scroll = MagicMock()
        scroll.width = 960
        scroll.bind = MagicMock()
        cal.ids = {
            'header_row': MagicMock(),
            'header_scroll': MagicMock(),
            'week_grid': MagicMock(),
            'calendar_scroll': scroll,
        }
        return cal

def _sample_event(day, title="IO", start="10:30", event_id="1"):
    return {
        "date": day,
        "data": CalendarBrickData(
            id=event_id,
            title=title,
            start_time=start,
            duration_minutes=90,
            category_id=event_id,
        ),
    }

def test_get_monday(mock_calendar):
    tuesday = date(2026, 5, 26)
    assert mock_calendar.get_monday(tuesday) == date(2026, 5, 25)

def test_navigation_next(mock_calendar):
    start = mock_calendar.current_week_start
    mock_calendar.next_week()
    assert mock_calendar.current_week_start == start + timedelta(days=7)

def test_navigation_prev(mock_calendar):
    start = mock_calendar.current_week_start
    mock_calendar.previous_week()
    assert mock_calendar.current_week_start == start - timedelta(days=7)

def test_current_week(mock_calendar):
    mock_calendar.next_week()
    mock_calendar.current_week()
    assert mock_calendar.current_week_start == date.today() - timedelta(days=date.today().weekday())

def test_events_filtering(mock_calendar):
    day = date(2026, 5, 30)
    mock_calendar.events_by_date = {
        day.isoformat(): [CalendarBrickData(
            id="1", title="IO", start_time="10:30", duration_minutes=90, category_id="1",
        )],
    }
    events = mock_calendar.get_events_for_day(day)
    assert len(events) == 1
    assert events[0].title == "IO"

def test_no_events_day(mock_calendar):
    assert mock_calendar.get_events_for_day(date(2020, 1, 1)) == []

def test_week_label_update(mock_calendar):
    with patch.object(mock_calendar, '_build_header'), patch.object(mock_calendar, '_build_week_grid'):
        mock_calendar.refresh_calendar()
        week_end = mock_calendar.current_week_start + timedelta(days=6)
        assert mock_calendar.week_label == f"{mock_calendar.current_week_start} - {week_end}"

def test_multiple_events_same_day(mock_calendar):
    day = date(2026, 5, 30)
    mock_calendar.events_by_date = {
        day.isoformat(): [
            CalendarBrickData(id="1", title="IO", start_time="10:30", duration_minutes=90, category_id="1"),
            CalendarBrickData(id="extra", title="Extra", start_time="12:00", duration_minutes=60, category_id="extra"),
        ],
    }
    events = mock_calendar.get_events_for_day(day)
    assert len(events) == 2

def test_current_week_logic(mock_calendar):
    mock_calendar.current_week_start = date(2020, 1, 1)
    mock_calendar.current_week()
    expected = date.today() - timedelta(days=date.today().weekday())
    assert mock_calendar.current_week_start == expected

def test_events_empty_date(mock_calendar):
    assert mock_calendar.get_events_for_day(date(1900, 1, 1)) == []

def test_language_binding(mock_calendar):
    mock_calendar.on_kv_post(None)
    mock_calendar.app.bind.assert_called_once()
    assert mock_calendar.ids['calendar_scroll'].bind.call_count == 2

def test_multiple_events_day(mock_calendar):
    day = date(2026, 5, 12)
    mock_calendar.events_by_date = {
        day.isoformat(): [
            CalendarBrickData(id="1", title="A", start_time="08:00", duration_minutes=90, category_id="1"),
            CalendarBrickData(id="2", title="B", start_time="10:30", duration_minutes=90, category_id="2"),
            CalendarBrickData(id="3", title="C", start_time="12:00", duration_minutes=90, category_id="3"),
        ],
    }
    assert len(mock_calendar.get_events_for_day(day)) == 3

def test_events_sorted_by_start_time(mock_calendar):
    day = date(2026, 5, 12)
    mock_calendar.events_by_date = {
        day.isoformat(): [
            CalendarBrickData(id="1", title="A", start_time="09:00", duration_minutes=60, category_id="1"),
            CalendarBrickData(id="2", title="B", start_time="08:00", duration_minutes=60, category_id="2"),
        ],
    }
    events = mock_calendar.get_events_for_day(day)
    assert [event.start_time for event in events] == ["08:00", "09:00"]

def test_reset_to_today(mock_calendar):
    mock_calendar.current_week_start = date(2000, 1, 1)
    mock_calendar.current_week()
    expected = date.today() - timedelta(days=date.today().weekday())
    assert mock_calendar.current_week_start == expected

def test_far_future_date(mock_calendar):
    future = date(2050, 1, 1)
    assert mock_calendar.get_monday(future) == date(2049, 12, 27)

@pytest.mark.parametrize("day, expected", [
    (date(2026, 5, 25), date(2026, 5, 25)),
    (date(2026, 5, 31), date(2026, 5, 25)),
])
def test_get_monday_cases(mock_calendar, day, expected):
    assert mock_calendar.get_monday(day) == expected

def test_unknown_event_type(mock_calendar):
    event = CalendarBrickData(
        id="1", title="Test", start_time="10:00", duration_minutes=60,
        category_id="test", event_type="???",
    )
    layout = MagicMock(y=120, height=120, x_fraction=0.0, width_fraction=1.0)
    brick = mock_calendar.create_brick(event, date(2026, 5, 30), layout)
    assert brick.style.bg_color is not None

def test_exam_event_uses_exam_colors(mock_calendar):
    mock_calendar.app.translate.return_value = 'Egzamin'
    event = CalendarBrickData(
        id="1", title="Test", start_time="10:00", duration_minutes=60,
        category_id="test", event_type="egzamin", clickable=False,
    )
    layout = MagicMock(y=120, height=120, x_fraction=0.0, width_fraction=1.0)
    brick = mock_calendar.create_brick(event, date(2026, 5, 30), layout)
    assert brick.style.bg_color == mock_calendar.app.theme.CalendarColors.EXAM_BG_COLOR
    assert brick.interactive is False

def test_colloquium_event_uses_colloquium_colors(mock_calendar):
    mock_calendar.app.translate.return_value = 'Kolokwium'
    event = CalendarBrickData(
        id="1", title="Test", start_time="10:00", duration_minutes=60,
        category_id="test", event_type="kolokwium", clickable=False,
    )
    layout = MagicMock(y=120, height=120, x_fraction=0.0, width_fraction=1.0)
    brick = mock_calendar.create_brick(event, date(2026, 5, 30), layout)
    assert brick.style.bg_color == mock_calendar.app.theme.CalendarColors.COLOQUIUM_BG_COLOR
    assert brick.interactive is False
    assert brick.title_text == 'Test'
    assert "Kolokwium" in brick.info_text

def test_merged_lesson_uses_overlay_color(mock_calendar):
    event = CalendarBrickData(
        id="1", title="Algebra liniowa", start_time="09:00", duration_minutes=90,
        category_id="test", event_type="zajęcia",
        overlay_label="Kolokwium", overlay_event_type="kolokwium",
    )
    layout = MagicMock(y=120, height=120, x_fraction=0.0, width_fraction=1.0)
    brick = mock_calendar.create_brick(event, date(2026, 6, 2), layout)
    assert brick.style.bg_color == mock_calendar.app.theme.CalendarColors.COLOQUIUM_BG_COLOR
    assert brick.interactive is True
    assert brick.overlay_label == "Kolokwium"
    assert brick.info_text == "09:00 | 1,5 h"

def test_empty_note_string(mock_calendar):
    mock_calendar.repo.get_daily_note.return_value = "   "
    event = CalendarBrickData(
        id="1", title="Test", start_time="10:00", duration_minutes=60, category_id="test",
    )
    layout = MagicMock(y=120, height=120, x_fraction=0.0, width_fraction=1.0)
    brick = mock_calendar.create_brick(event, date(2026, 5, 30), layout)
    assert brick.has_note is False

def test_date_type_safety(mock_calendar):
    with pytest.raises(AttributeError):
        mock_calendar.get_monday(12345)

def test_load_events_from_repo(mock_calendar):
    week_start = date(2026, 10, 5)
    mock_calendar.current_week_start = week_start
    mock_calendar.repo.get_all_schedule_entries.return_value = [{
        'schedule_id': 1,
        'subject_id': 1,
        'day_of_week': 0,
        'start_time': '09:00',
        'duration_minutes': 90,
        'subject_name': 'Test',
        'term_start': '2026-10-01',
        'term_end': '2027-01-01',
    }]
    mock_calendar.repo.get_events_in_range.return_value = []

    mock_calendar._load_events()

    assert len(mock_calendar.events) == 1
    assert mock_calendar.events[0]['date'] == week_start
    assert len(mock_calendar.events_by_date['2026-10-05']) == 1
    assert len(mock_calendar.get_events_for_day(date(2026, 10, 6))) == 0

def test_get_events_for_day_filters_by_date(mock_calendar):
    mock_calendar.events_by_date = {
        '2026-06-01': [CalendarBrickData(id='1', title='Mon', start_time='08:00', duration_minutes=90, category_id='1')],
        '2026-06-03': [CalendarBrickData(id='2', title='Wed', start_time='10:00', duration_minutes=90, category_id='2')],
    }
    assert mock_calendar.get_events_for_day(date(2026, 6, 1))[0].title == 'Mon'
    assert mock_calendar.get_events_for_day(date(2026, 6, 3))[0].title == 'Wed'

def test_column_x_positions(mock_calendar):
    mock_calendar.column_width = 100
    assert mock_calendar._column_x(0) == mock_calendar._hour_axis_width()
    assert mock_calendar._column_x(1) == mock_calendar._hour_axis_width() + 100
    assert mock_calendar._column_x(3) == mock_calendar._hour_axis_width() + 300

def test_multiple_events_order(mock_calendar):
    day = date(2026, 5, 30)
    mock_calendar.events_by_date = {
        day.isoformat(): [
            CalendarBrickData(id="1", title="A", start_time="09:00", duration_minutes=60, category_id="test"),
            CalendarBrickData(id="2", title="B", start_time="08:00", duration_minutes=60, category_id="test"),
        ],
    }
    events = mock_calendar.get_events_for_day(day)
    assert [event.title for event in events] == ["B", "A"]
