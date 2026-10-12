from abc import abstractmethod
from dataclasses import dataclass

from typing import Optional

@dataclass(frozen=True)
class LessonNote:
    id: str                # ID z bazy danych
    content: str           # Treść notatki
    last_modified: str     # Timestamp


@dataclass(frozen=True)
class CalendarBrickData:
    id: str
    title: str
    start_time: str
    duration_minutes: int
    category_id: str
    event_type: str = "zajęcia"
    note: Optional[LessonNote] = None
    subject_id: Optional[int] = None
    layout_key: str = ""
    clickable: bool = True
    overlay_label: Optional[str] = None
    overlay_event_type: Optional[str] = None

    @property
    def has_note(self) -> bool:
        return self.note is not None
