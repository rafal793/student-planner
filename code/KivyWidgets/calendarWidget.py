from datetime import date, timedelta
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex
from Widgets.Brick import CalendarBrickData
from Widgets.calendarEvents import build_week_calendar_events, merge_same_time_overlays
from Widgets.calendarTimeLayout import (
    CalendarTimeConfig,
    format_event_info,
    layout_timed_events,
)
from Widgets.notePopup import NotePopup
from KivyWidgets.kivyNotePopupBackend import KivyNotePopupBackend
from KivyWidgets.KivyBrickBackend import CalendarEventBrick
from Widgets.datePicker import DatePicker, DatePickerStyle
from KivyWidgets.kivyDatePickerBackend import KivyDatePickerBackend
from style.ButtonStyle import ButtonStyle


DAY_NAMES = {
    'pl': {0: "Pon", 1: "Wt", 2: "Śr", 3: "Czw", 4: "Pt", 5: "Sob", 6: "Ndz"},
    'en': {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"},
}

HEADER_HEIGHT = dp(48)
MIN_COLUMN_WIDTH = dp(96)
COLUMN_PADDING = dp(4)


class CalendarWidget(BoxLayout):
    week_label = StringProperty("")
    repo = ObjectProperty(None)
    app = ObjectProperty(None)
    calendar_content_width = NumericProperty(900)
    calendar_grid_height = NumericProperty(500)
    column_width = NumericProperty(120)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_week_start = self.get_monday(date.today())
        self.time_config = CalendarTimeConfig()
        self.events = []
        self.events_by_date = {}

    def _note_subject_id(self, event_data: CalendarBrickData):
        if event_data.subject_id is not None:
            return event_data.subject_id
        return int(event_data.id)

    def _date_key(self, day_date) -> str:
        if isinstance(day_date, date):
            return day_date.isoformat()
        return str(day_date)

    def _load_events(self):
        if not self.repo:
            self.events = []
            self.events_by_date = {}
            return

        week_start = self.get_monday(self.current_week_start)
        self.current_week_start = week_start
        week_end = week_start + timedelta(days=6)
        schedule_entries = self.repo.get_all_schedule_entries() or []
        timed_events = self.repo.get_events_in_range(
            week_start.isoformat(),
            week_end.isoformat(),
        ) or []
        self.events = build_week_calendar_events(
            week_start,
            schedule_entries,
            timed_events,
        )
        grouped = {}
        for item in self.events:
            key = self._date_key(item['date'])
            grouped.setdefault(key, []).append(item['data'])
        self.events_by_date = grouped

    def get_monday(self, selected_date):
        return selected_date - timedelta(days=selected_date.weekday())

    def on_kv_post(self, base_widget):
        if self.app:
            self.app.bind(language=self._on_language_change)
        if 'calendar_scroll' in self.ids:
            self.ids.calendar_scroll.bind(width=self._on_scroll_resize)
            self.ids.calendar_scroll.bind(scroll_x=self._sync_header_scroll)
        Window.bind(size=self._on_window_resize)
        if 'week_grid' in self.ids:
            Clock.schedule_once(lambda _dt: self.refresh_calendar(), 0)

    def _sync_header_scroll(self, instance, value):
        if 'header_scroll' in self.ids:
            self.ids.header_scroll.scroll_x = value

    def _on_window_resize(self, *args):
        Clock.schedule_once(lambda _dt: self.refresh_calendar(reload_data=False), 0)

    def _on_scroll_resize(self, *args):
        Clock.schedule_once(lambda _dt: self.refresh_calendar(reload_data=False), 0)

    def _on_language_change(self, instance, value):
        self.refresh_calendar()

    def refresh_calendar(self, reload_data=True):
        if 'week_grid' not in self.ids or 'header_row' not in self.ids:
            return

        week_end = self.current_week_start + timedelta(days=6)
        self.week_label = f"{self.current_week_start} - {week_end}"
        if reload_data:
            self._load_events()
        self._update_dimensions()

        self.ids.header_row.clear_widgets()
        self.ids.week_grid.clear_widgets()
        self.ids.week_grid.canvas.before.clear()

        self._build_header()
        self._build_week_grid()
        self._sync_widget_sizes()

    def _hour_axis_width(self):
        return dp(self.time_config.hour_label_width)

    def _viewport_width(self):
        if 'calendar_scroll' in self.ids:
            width = self.ids.calendar_scroll.width
            if width > dp(40):
                return width
        parent = self.parent
        while parent is not None:
            if getattr(parent, 'width', 0) > dp(40):
                return max(parent.width - dp(80), dp(320))
            parent = parent.parent
        return max(Window.width - dp(120), dp(320))

    def _update_dimensions(self):
        hour_w = self._hour_axis_width()
        viewport = self._viewport_width()
        fit_column = (viewport - hour_w) / 7
        self.column_width = max(MIN_COLUMN_WIDTH, fit_column)

        self.calendar_grid_height = dp(self.time_config.grid_height)
        self.calendar_content_width = hour_w + (7 * self.column_width)

    def _column_x(self, day_index: int) -> float:
        return self._hour_axis_width() + (day_index * self.column_width)

    def _theme_white(self):
        return get_color_from_hex(self.app.theme.DefaultColors.DEFAULT_WHITE)

    def _theme_muted_white(self):
        color = self._theme_white()
        return color[0], color[1], color[2], 0.35

    def _build_header(self):
        row = self.ids.header_row
        hour_spacer = Widget(size_hint_x=None, width=self._hour_axis_width())
        row.add_widget(hour_spacer)

        text_color = self._theme_white()
        lang = self.app.language if self.app else 'pl'

        for day_index in range(7):
            day_date = self.current_week_start + timedelta(days=day_index)
            day_str = DAY_NAMES[lang][day_date.weekday()]
            label = Label(
                text=f"{day_str}\n{day_date.strftime('%m-%d')}",
                size_hint_x=None,
                width=self.column_width,
                size_hint_y=1,
                color=text_color,
                bold=True,
                font_size='14sp',
                halign='center',
                valign='middle',
            )
            label.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
            row.add_widget(label)

    def _build_week_grid(self):
        grid = self.ids.week_grid
        grid_height = self.calendar_grid_height
        line_color = get_color_from_hex(self.app.theme.WidgetColors.SCROLLBAR_COLOR_INACTIVE)
        text_color = self._theme_white()

        with grid.canvas.before:
            Color(*line_color)
            for day_index in range(8):
                x = self._column_x(day_index) if day_index < 7 else self.calendar_content_width
                Line(points=[x, 0, x, grid_height], width=1)
            for _, y_offset in self.time_config.hour_labels():
                y = dp(y_offset)
                Line(points=[0, y, self.calendar_content_width, y], width=1)

        for hour, y_offset in self.time_config.hour_labels():
            label = Label(
                text=f"{hour:02d}:00",
                size_hint=(None, None),
                size=(self._hour_axis_width() - dp(6), dp(16)),
                pos=(0, dp(y_offset)),
                color=text_color,
                font_size='11sp',
                halign='right',
                valign='middle',
            )
            label.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
            grid.add_widget(label)

        for day_index in range(7):
            day_date = self.current_week_start + timedelta(days=day_index)
            col_x = self._column_x(day_index)
            events = merge_same_time_overlays(
                self.get_events_for_day(day_date),
                self._event_type_label,
            )
            layouts = layout_timed_events(events, self.time_config)
            layout_by_key = {layout.event_id: layout for layout in layouts}

            if not events:
                empty = Label(
                    text="-",
                    size_hint=(None, None),
                    size=(self.column_width, dp(20)),
                    pos=(col_x, grid_height * 0.45),
                    color=self._theme_muted_white(),
                    halign='center',
                )
                grid.add_widget(empty)
                continue

            inner_width = self.column_width - (COLUMN_PADDING * 2)
            for event in events:
                layout_key = event.layout_key or event.id
                layout = layout_by_key[layout_key]
                brick = self.create_brick(event, day_date, layout)
                brick_w = max(inner_width * layout.width_fraction - dp(2), dp(36))
                brick_h = max(dp(layout.height), dp(40))
                brick.size = (brick_w, brick_h)
                brick.pos = (
                    col_x + COLUMN_PADDING + (inner_width * layout.x_fraction),
                    dp(layout.y),
                )
                grid.add_widget(brick)

    def _sync_widget_sizes(self):
        if 'week_grid' not in self.ids:
            return
        self.ids.week_grid.width = self.calendar_content_width
        self.ids.week_grid.height = self.calendar_grid_height
        if 'header_row' in self.ids:
            self.ids.header_row.width = self.calendar_content_width
        if 'calendar_scroll' in self.ids:
            needs_h_scroll = (
                self.calendar_content_width > self._viewport_width() + dp(4)
            )
            self.ids.calendar_scroll.do_scroll_x = needs_h_scroll
            if 'header_scroll' in self.ids:
                self.ids.header_scroll.do_scroll_x = needs_h_scroll
                self.ids.header_scroll.scroll_x = self.ids.calendar_scroll.scroll_x

    def get_events_for_day(self, day_date):
        key = self._date_key(day_date)
        items = list(self.events_by_date.get(key, []))

        def sort_key(item):
            overlay = 0 if item.event_type in ('egzamin', 'kolokwium') else 1
            return (item.start_time, overlay)

        return sorted(items, key=sort_key)

    def _event_type_label(self, event_type: str) -> str:
        if event_type == 'egzamin':
            return self.app.translate('type_exam', self.app.language)
        if event_type == 'kolokwium':
            return self.app.translate('type_colloquium', self.app.language)
        return event_type

    def create_brick(self, event_data, day_date, layout):
        colors = self.app.theme.CalendarColors
        color_type = (event_data.overlay_event_type or event_data.event_type).lower()
        if color_type == "egzamin":
            bg_c = colors.EXAM_BG_COLOR
            hover_c = colors.EXAM_HOVER_BG_COLOR
        elif color_type == "kolokwium":
            bg_c = colors.COLOQUIUM_BG_COLOR
            hover_c = colors.COLOQUIUM_HOVER_BG_COLOR
        else:
            bg_c = colors.LESSON_BG_COLOR
            hover_c = colors.LESSON_HOVER_BG_COLOR

        style = ButtonStyle(
            bg_color=bg_c,
            hover_bg_color=hover_c,
            text_color=self.app.theme.DefaultColors.DEFAULT_BLACK,
            border_radius=20,
        )

        brick = CalendarEventBrick()
        brick.style = style
        brick.data = event_data
        brick.interactive = event_data.clickable
        brick.title_text = event_data.title
        brick.overlay_label = event_data.overlay_label or ''

        if event_data.clickable:
            brick.info_text = format_event_info(event_data.start_time, event_data.duration_minutes)
            note_subject_id = self._note_subject_id(event_data)
            existing_text = self.repo.get_daily_note(note_subject_id, str(day_date))
            brick.has_note = bool(existing_text and existing_text.strip())
            brick.bind(on_release=lambda instance: self.on_event_click(event_data, day_date))
        else:
            type_label = self._event_type_label(event_data.event_type)
            time_info = format_event_info(event_data.start_time, event_data.duration_minutes)
            brick.info_text = f"{type_label} | {time_info}"
            brick.has_note = False

        return brick

    def on_event_click(self, event_data, day_date):
        date_str = str(day_date)
        note_subject_id = self._note_subject_id(event_data)
        existing_text = self.repo.get_daily_note(note_subject_id, date_str)

        backend = KivyNotePopupBackend()
        popup = NotePopup(
            subject_id=str(note_subject_id),
            subject_name=event_data.title,
            note_date=date_str,
            backend=backend,
            existing_text=existing_text,
            on_save=self.save_note_to_db,
        )
        popup.open()

    def save_note_to_db(self, subject_id, note_date, content):
        self.repo.set_daily_note(subject_id, note_date, content)
        self.refresh_calendar()

    def previous_week(self):
        self.current_week_start -= timedelta(days=7)
        self.refresh_calendar()

    def next_week(self):
        self.current_week_start += timedelta(days=7)
        self.refresh_calendar()

    def current_week(self):
        self.current_week_start = self.get_monday(date.today())
        self.refresh_calendar()

    def choose_week(self):
        dp_style = DatePickerStyle(
            bg_color=get_color_from_hex(self.app.theme.DefaultColors.DEFAULT_WHITE),
            selected_color=get_color_from_hex(self.app.theme.UiColors.SECONDARY_BG_COLOR),
            today_color=get_color_from_hex(self.app.theme.WidgetColors.SCROLLBAR_COLOR_ACTIVE),
            text_color=get_color_from_hex(self.app.theme.DefaultColors.DEFAULT_BLACK),
        )
        backend = KivyDatePickerBackend()
        picker = DatePicker(
            selected_date=date.today(),
            backend=backend,
            style=dp_style,
        )
        picker_ui = picker.render()
        popup = Popup(
            title="Wybierz datę",
            content=picker_ui,
            size_hint=(None, None),
            size=(400, 450),
        )

        def on_confirm(instance):
            chosen_date = backend.selected_date
            self.current_week_start = self.get_monday(chosen_date)
            self.refresh_calendar()
            popup.dismiss()

        backend.confirm_button.bind(on_release=on_confirm)
        popup.open()
