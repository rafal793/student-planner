from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass
class _EventPlacement:
    event: object
    start: int
    end: int
    column: int
    max_columns: int = 1


@dataclass(frozen=True)
class CalendarTimeConfig:
    start_hour: int = 7
    end_hour: int = 21
    pixels_per_minute: float = 2.0
    min_event_height: float = 28.0
    hour_label_width: float = 45.0
    column_padding: float = 4.0

    @property
    def start_minutes(self) -> int:
        return self.start_hour * 60

    @property
    def end_minutes(self) -> int:
        return self.end_hour * 60

    @property
    def grid_height(self) -> float:
        return (self.end_minutes - self.start_minutes) * self.pixels_per_minute

    def hour_y(self, hour: int) -> float:
        minutes = hour * 60
        offset_from_top = (minutes - self.start_minutes) * self.pixels_per_minute
        return self.grid_height - offset_from_top

    def event_y(self, start_minutes: int, height: float) -> float:
        offset_from_top = (start_minutes - self.start_minutes) * self.pixels_per_minute
        return self.grid_height - offset_from_top - height

    def hour_labels(self) -> list[tuple[int, float]]:
        return [(hour, self.hour_y(hour)) for hour in range(self.start_hour, self.end_hour + 1)]


@dataclass(frozen=True)
class TimedEventLayout:
    event_id: str
    y: float
    height: float
    x_fraction: float
    width_fraction: float


def parse_time(time_str: str) -> int:
    hours, minutes = time_str.split(":")
    return int(hours) * 60 + int(minutes)


def format_duration_label(duration_minutes: int) -> str:
    if duration_minutes % 60 == 0:
        return f"{duration_minutes // 60} h"
    hours = duration_minutes / 60
    if hours == int(hours):
        return f"{int(hours)} h"
    return f"{hours:.1f} h".replace(".", ",")


def format_event_info(start_time: str, duration_minutes: int) -> str:
    return f"{start_time} | {format_duration_label(duration_minutes)}"


def event_end_minutes(start_time: str, duration_minutes: int) -> int:
    return parse_time(start_time) + duration_minutes


def _event_layout_key(event) -> str:
    layout_key = getattr(event, 'layout_key', '')
    return layout_key or event.id


def layout_timed_events(
    events: Iterable,
    config: Optional[CalendarTimeConfig] = None,
) -> list[TimedEventLayout]:
    config = config or CalendarTimeConfig()
    sorted_events = sorted(events, key=lambda event: parse_time(event.start_time))
    if not sorted_events:
        return []

    placements: list[_EventPlacement] = []

    for event in sorted_events:
        start = parse_time(event.start_time)
        end = event_end_minutes(event.start_time, event.duration_minutes)

        overlapping = [
            placement for placement in placements
            if placement.start < end and placement.end > start
        ]
        used_columns = {placement.column for placement in overlapping}
        column = 0
        while column in used_columns:
            column += 1

        placement = _EventPlacement(event=event, start=start, end=end, column=column)
        overlap_group = overlapping + [placement]
        total_columns = max(item.column for item in overlap_group) + 1
        for item in overlap_group:
            item.max_columns = max(item.max_columns, total_columns)
        placements.append(placement)

    layouts: list[TimedEventLayout] = []
    for placement in placements:
        height = max(
            placement.event.duration_minutes * config.pixels_per_minute,
            config.min_event_height,
        )
        y = config.event_y(placement.start, height)
        width_fraction = 1.0 / placement.max_columns
        x_fraction = placement.column * width_fraction
        layouts.append(
            TimedEventLayout(
                event_id=_event_layout_key(placement.event),
                y=y,
                height=height,
                x_fraction=x_fraction,
                width_fraction=width_fraction,
            )
        )

    return layouts
