from datetime import date, timedelta
from typing import Iterable, Optional

from Widgets.Brick import CalendarBrickData

DEFAULT_EXAM_DURATION_MINUTES = 90
CALENDAR_TIMED_EVENT_TYPES = frozenset({'egzamin', 'kolokwium'})


def _date_in_term(day_date: date, term_start: Optional[str], term_end: Optional[str]) -> bool:
    if term_start:
        if day_date < date.fromisoformat(term_start):
            return False
    if term_end:
        if day_date > date.fromisoformat(term_end):
            return False
    return True


def _subject_note_id(subject_id: int) -> str:
    return str(subject_id)


def build_week_calendar_events(
    week_start: date,
    schedule_entries: Iterable[dict],
    timed_events: Optional[Iterable[dict]] = None,
) -> list[dict]:
    events: list[dict] = []
    monday = week_start - timedelta(days=week_start.weekday())

    for entry in schedule_entries:
        day_of_week = int(entry['day_of_week'])
        day_date = monday + timedelta(days=day_of_week)

        if not _date_in_term(day_date, entry.get('term_start'), entry.get('term_end')):
            continue

        subject_id = entry['subject_id']
        schedule_id = entry['schedule_id']
        events.append({
            'date': day_date,
            'data': CalendarBrickData(
                id=_subject_note_id(subject_id),
                subject_id=subject_id,
                layout_key=f"schedule-{schedule_id}",
                title=entry['subject_name'],
                start_time=entry['start_time'],
                duration_minutes=int(entry['duration_minutes']),
                category_id=_subject_note_id(subject_id),
                event_type='zajęcia',
            ),
        })

    for entry in timed_events or []:
        event_type = _map_event_type(entry.get('type', ''))
        if event_type not in CALENDAR_TIMED_EVENT_TYPES:
            continue

        event_date, start_time = _parse_event_datetime(entry['date_time'])
        if not (monday <= event_date <= monday + timedelta(days=6)):
            continue

        subject_id = entry['subject_id']
        event_id = entry['id']
        events.append({
            'date': event_date,
            'data': CalendarBrickData(
                id=_subject_note_id(subject_id),
                subject_id=subject_id,
                layout_key=f"event-{event_id}",
                title=entry.get('subject_name') or entry.get('title', ''),
                start_time=start_time,
                duration_minutes=DEFAULT_EXAM_DURATION_MINUTES,
                category_id=_subject_note_id(subject_id),
                event_type=event_type,
                clickable=False,
            ),
        })

    return events


def _parse_event_datetime(date_time: str) -> tuple[date, str]:
    date_part, time_part = date_time.split(' ', 1)
    return date.fromisoformat(date_part), time_part[:5]


def _map_event_type(raw_type: str) -> str:
    normalized = (raw_type or '').lower()
    if normalized in {'egzamin', 'exam'}:
        return 'egzamin'
    if normalized in {'kolokwium', 'colloquium'}:
        return 'kolokwium'
    return normalized or 'zajęcia'


def merge_same_time_overlays(
    events: list[CalendarBrickData],
    type_label_fn,
) -> list[CalendarBrickData]:
    from dataclasses import replace

    lessons = [event for event in events if event.clickable]
    overlays = [event for event in events if not event.clickable]
    if not overlays:
        return events

    lesson_overlays: dict[str, CalendarBrickData] = {}
    standalone_overlays: list[CalendarBrickData] = []

    for overlay in overlays:
        matched_lesson = None
        for lesson in lessons:
            if lesson.subject_id != overlay.subject_id:
                continue
            if lesson.start_time != overlay.start_time:
                continue
            matched_lesson = lesson
            break

        if matched_lesson is None:
            standalone_overlays.append(overlay)
            continue

        lesson_key = matched_lesson.layout_key or matched_lesson.id
        current = lesson_overlays.get(lesson_key)
        if current is None or overlay.event_type == 'egzamin':
            lesson_overlays[lesson_key] = overlay

    merged_lessons = []
    for lesson in lessons:
        lesson_key = lesson.layout_key or lesson.id
        overlay = lesson_overlays.get(lesson_key)
        if overlay is None:
            merged_lessons.append(lesson)
            continue

        merged_lessons.append(
            replace(
                lesson,
                overlay_label=type_label_fn(overlay.event_type),
                overlay_event_type=overlay.event_type,
            )
        )

    return merged_lessons + standalone_overlays
