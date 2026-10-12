from typing import Callable

def subjects_at_absence_limit(subjects: list[dict]) -> list[dict]:
    at_limit = []
    for subject in subjects:
        max_absences = int(subject.get('max_absences') or 0)
        if max_absences <= 0:
            continue
        current_absences = int(subject.get('current_absences') or 0)
        if current_absences >= max_absences:
            at_limit.append(subject)
    return sorted(at_limit, key=lambda item: item.get('name', ''))

def build_notification_messages(
    subjects: list[dict],
    upcoming_events: list[dict],
    translate: Callable[[str], str],
) -> list[str]:
    messages: list[str] = []

    for subject in subjects_at_absence_limit(subjects):
        messages.append(
            translate('notification_absence_limit').format(
                subject=subject.get('name', ''),
                current=int(subject.get('current_absences') or 0),
                maximum=int(subject.get('max_absences') or 0),
            )
        )

    for event in upcoming_events:
        date_time = event.get('date_time', '')
        title = event.get('title', '')
        event_type = event.get('type', '')
        if event_type:
            messages.append(
                translate('notification_upcoming_event').format(
                    date_time=date_time,
                    title=title,
                    event_type=event_type,
                )
            )
        else:
            messages.append(
                translate('notification_upcoming_event_no_type').format(
                    date_time=date_time,
                    title=title,
                )
            )

    return messages
