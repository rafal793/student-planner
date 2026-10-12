from Widgets.notificationMessages import (
    build_notification_messages,
    subjects_at_absence_limit,
)


def _translate(key: str) -> str:
    translations = {
        'notification_absence_limit': '{subject}: limit ({current}/{maximum})',
        'notification_upcoming_event': '{date_time} | {title} ({event_type})',
        'notification_upcoming_event_no_type': '{date_time} | {title}',
    }
    return translations[key]


def test_subjects_at_absence_limit_filters_and_sorts():
    subjects = [
        {'name': 'Z', 'current_absences': 3, 'max_absences': 3},
        {'name': 'A', 'current_absences': 2, 'max_absences': 2},
        {'name': 'B', 'current_absences': 1, 'max_absences': 5},
        {'name': 'C', 'current_absences': 4, 'max_absences': 0},
    ]

    result = subjects_at_absence_limit(subjects)

    assert [item['name'] for item in result] == ['A', 'Z']


def test_build_notification_messages_includes_absence_and_events():
    subjects = [
        {'name': 'Fizyka', 'current_absences': 2, 'max_absences': 2},
    ]
    events = [
        {'date_time': '2026-06-10 10:00', 'title': 'Kolokwium', 'type': 'Kolokwium'},
    ]

    messages = build_notification_messages(subjects, events, _translate)

    assert len(messages) == 2
    assert messages[0] == 'Fizyka: limit (2/2)'
    assert messages[1] == '2026-06-10 10:00 | Kolokwium (Kolokwium)'


def test_build_notification_messages_empty():
    assert build_notification_messages([], [], _translate) == []
