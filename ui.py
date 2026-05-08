from __future__ import annotations

import calendar
import platform
import subprocess
import sys
import tkinter.messagebox as messagebox
from datetime import datetime, timedelta
from pathlib import Path

import customtkinter as ctk
from PIL import Image

from database import Database
from i18n import TEXTS


class StudentPlannerApp(ctk.CTk):
    """Main application window for Student Planner.

    The class hosts the entire UI: the persistent dashboard frame, the sidebar
    with the session-countdown widget, the top bar with the language switch and
    notification dot, plus all per-tab renderers. Every piece of state lives
    in SQLite via :class:`Database` so closing and reopening the app restores
    the previous session.
    """

    # Brand colors
    COLOR_BG = "#322C2B"
    COLOR_NAV = "#1A4173"
    COLOR_ACCENT = "#2E578C"
    COLOR_SOFT = "#B1BBC7"
    COLOR_LIGHT = "#D9D9D7"
    COLOR_TOPBAR = "#fafaf8"

    # Interaction colors derived from the palette above. Kept here so visuals
    # stay consistent across all renderers without re-typing literals.
    HOVER_ACCENT = "#3C6DAA"
    HOVER_SOFT = "#C4CBD3"
    HOVER_DIM = "#9aa6b3"
    COLOR_SELECTED = "#446EAA"
    COLOR_TODAY = "#3C6DAA"
    COLOR_INCREMENT = "#4D8A5F"
    HOVER_INCREMENT = "#61A875"
    COLOR_DECREMENT = "#8A4D50"
    HOVER_DECREMENT = "#A45E62"
    COLOR_DELETE = "#7A4045"
    HOVER_DELETE = "#944C53"
    COLOR_STATUS_PASSED = "#62C57D"
    COLOR_STATUS_RISK = "#F28B82"
    COLOR_STATUS_IN_PROGRESS = "#E3C46D"
    COLOR_DARK_TEXT = "#1A1A1A"

    # Standard corner radii so similar widgets share the same softness.
    RADIUS_PANEL = 14
    RADIUS_TILE = 18
    RADIUS_BUTTON = 10
    RADIUS_BADGE = 8

    LOGO_PATH = Path(
        "/Users/rafallip/.cursor/projects/Users-rafallip-Desktop-StudentPlanner/"
        "assets/logo4-927b959e-ba27-4014-98f5-82c32c36f082.png"
    )

    def __init__(self) -> None:
        super().__init__()
        self.db = Database()
        self.language = self.db.get_setting("language", "pl")
        if self.language not in ("pl", "en"):
            self.language = "pl"

        self._selected_subject_id: int | None = None
        self.active_page = "dashboard"
        self.countdown_job: str | None = None
        self.week_offset = 0
        self._dashboard_frame: ctk.CTkFrame | None = None
        self._calendar_grid: ctk.CTkFrame | None = None
        self._week_range_label: ctk.CTkLabel | None = None
        self._day_header_labels: list[ctk.CTkLabel] = []
        self._day_content_frames: list[ctk.CTkScrollableFrame] = []

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(self.t("app_title"))
        self.geometry("1280x760")
        self.minsize(1100, 700)
        self.configure(fg_color=self.COLOR_BG)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_top_bar()

        self._build_sidebar()
        self.content_frame = ctk.CTkFrame(self, fg_color=self.COLOR_BG, corner_radius=0)
        self.content_frame.grid(row=1, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.show_page("dashboard")
        self.refresh_subject_options()
        self.check_notifications()
        self._start_session_countdown_updates()

    def t(self, key: str) -> str:
        return TEXTS[self.language].get(key, key)

    def _build_sidebar(self) -> None:
        self.sidebar = ctk.CTkFrame(self, fg_color=self.COLOR_NAV, width=214, corner_radius=0)
        self.sidebar.grid(row=1, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)

        self.nav_config = [
            ("dashboard", "dashboard"),
            ("my_subjects", "my_subjects"),
            ("add_subject", "add_subject"),
            ("schedule_exams", "schedule_exams"),
            ("rules", "rules"),
            ("progress", "progress"),
        ]

        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        row = 2
        for idx, (key, page) in enumerate(self.nav_config):
            btn = ctk.CTkButton(
                self.sidebar,
                text=self.t(key),
                command=lambda p=page: self.show_page(p),
                fg_color=self.COLOR_ACCENT,
                hover_color=self.HOVER_ACCENT,
                text_color=self.COLOR_LIGHT,
                corner_radius=self.RADIUS_BUTTON,
                anchor="center",
                height=38,
            )
            pady_top = 22 if idx == 0 else 6
            btn.grid(row=row, column=0, padx=16, pady=(pady_top, 0), sticky="ew")
            self.nav_buttons[page] = btn
            row += 1

        self.sidebar.grid_rowconfigure(row, weight=1)
        self._build_sidebar_session_countdown(row + 1)

    def _build_sidebar_session_countdown(self, row: int) -> None:
        self._session_countdown_box = ctk.CTkFrame(
            self.sidebar,
            fg_color=self.COLOR_ACCENT,
            corner_radius=self.RADIUS_TILE,
            cursor="hand2",
        )
        self._session_countdown_box.grid(row=row, column=0, sticky="sew", padx=16, pady=(0, 18))

        self._session_countdown_title = ctk.CTkLabel(
            self._session_countdown_box,
            text=self.t("session_widget_title"),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.COLOR_LIGHT,
            anchor="w",
        )
        self._session_countdown_title.pack(fill="x", padx=10, pady=(8, 2))

        self._session_countdown_body = ctk.CTkLabel(
            self._session_countdown_box,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.COLOR_LIGHT,
            justify="left",
            anchor="w",
            wraplength=172,
        )
        self._session_countdown_body.pack(fill="x", padx=10, pady=(0, 2))

        self._session_countdown_foot = ctk.CTkLabel(
            self._session_countdown_box,
            text="",
            font=ctk.CTkFont(size=10),
            text_color=self.COLOR_SOFT,
            justify="left",
            anchor="w",
            wraplength=172,
        )
        self._session_countdown_foot.pack(fill="x", padx=10, pady=(0, 10))

        def _open(_event=None) -> None:
            self._open_session_countdown_dialog()

        for w in (
            self._session_countdown_box,
            self._session_countdown_title,
            self._session_countdown_body,
            self._session_countdown_foot,
        ):
            w.bind("<Button-1>", _open)
            try:
                w.configure(cursor="hand2")
            except Exception:
                pass

    def _session_countdown_preview_lines(self) -> tuple[str, str]:
        raw = self.db.get_setting("session_target_date", "").strip()
        if not raw or not self._valid_date(raw):
            return ("—", self.t("countdown_sidebar_set"))
        target = datetime.strptime(raw, "%Y-%m-%d")
        now = datetime.now()
        delta = target - now
        if delta.total_seconds() < 0:
            return (self.t("countdown_session_passed"), raw)
        days = delta.days
        hours = (delta.seconds // 3600) % 24
        minutes = (delta.seconds // 60) % 60
        main = (
            f"{self.t('remaining')}: "
            f"{days} {self.t('days')} {hours} {self.t('hours')} {minutes} {self.t('minutes')}"
        )
        return (main, raw)

    def _refresh_sidebar_countdown(self) -> None:
        if not getattr(self, "_session_countdown_body", None):
            return
        main, foot = self._session_countdown_preview_lines()
        self._session_countdown_title.configure(text=self.t("session_widget_title"))
        self._session_countdown_body.configure(text=main)
        self._session_countdown_foot.configure(text=foot)

    def _open_session_countdown_dialog(self) -> None:
        dlg = ctk.CTkToplevel(self)
        dlg.title(self.t("countdown_edit_title"))
        dlg.geometry("420x280")
        dlg.configure(fg_color=self.COLOR_BG)
        dlg.transient(self)
        dlg.grab_set()

        ctk.CTkLabel(
            dlg,
            text=self.t("countdown_edit_title"),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.COLOR_LIGHT,
        ).pack(anchor="w", padx=16, pady=(14, 6))

        ctk.CTkLabel(dlg, text=self.t("session_date"), text_color=self.COLOR_LIGHT).pack(
            anchor="w", padx=16, pady=(8, 2)
        )
        date_row = ctk.CTkFrame(dlg, fg_color=self.COLOR_BG)
        date_row.pack(anchor="w", padx=16, pady=(0, 8), fill="x")
        date_entry = ctk.CTkEntry(date_row, fg_color=self.COLOR_NAV, text_color=self.COLOR_LIGHT, width=300)
        date_entry.pack(side="left")
        saved = self.db.get_setting("session_target_date", "")
        if saved:
            date_entry.insert(0, saved)

        preview = ctk.CTkLabel(dlg, text="", font=ctk.CTkFont(size=14), text_color=self.COLOR_LIGHT, wraplength=380)

        def update_preview() -> None:
            raw = date_entry.get().strip()
            if not raw or not self._valid_date(raw):
                preview.configure(text=f"{self.t('remaining')}: —")
                return
            target = datetime.strptime(raw, "%Y-%m-%d")
            now = datetime.now()
            delta = target - now
            if delta.total_seconds() < 0:
                preview.configure(text=f"{self.t('remaining')}: 0 {self.t('days')}")
                return
            days = delta.days
            hours = (delta.seconds // 3600) % 24
            minutes = (delta.seconds // 60) % 60
            preview.configure(
                text=(
                    f"{self.t('remaining')}: "
                    f"{days} {self.t('days')} {hours} {self.t('hours')} {minutes} {self.t('minutes')}"
                )
            )

        def open_date_picker() -> None:
            self._open_date_picker(date_entry)
            update_preview()

        ctk.CTkButton(
            date_row,
            text="📅",
            command=open_date_picker,
            width=44,
            height=28,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.HOVER_ACCENT,
            text_color=self.COLOR_LIGHT,
            corner_radius=self.RADIUS_BUTTON,
        ).pack(side="left", padx=(8, 0))

        preview.pack(anchor="w", padx=16, pady=(4, 12))

        update_preview()
        date_entry.bind("<KeyRelease>", lambda _e: update_preview())

        btn_row = ctk.CTkFrame(dlg, fg_color=self.COLOR_BG)
        btn_row.pack(fill="x", padx=16, pady=(0, 14))

        def save_and_close() -> None:
            raw = date_entry.get().strip()
            if not self._valid_date(raw):
                messagebox.showerror(self.t("error"), self.t("invalid_date"))
                return
            self.db.set_setting("session_target_date", raw)
            self._refresh_sidebar_countdown()
            dlg.destroy()
            messagebox.showinfo(self.t("saved"), self.t("saved"))

        ctk.CTkButton(
            btn_row,
            text=self.t("close"),
            command=dlg.destroy,
            fg_color=self.COLOR_SOFT,
            text_color=self.COLOR_BG,
            hover_color=self.HOVER_SOFT,
            width=100,
        ).pack(side="left")
        ctk.CTkButton(
            btn_row,
            text=self.t("set_date"),
            command=save_and_close,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.HOVER_ACCENT,
            width=140,
        ).pack(side="right")

    def _start_session_countdown_updates(self) -> None:
        self._refresh_sidebar_countdown()
        self._schedule_next_session_countdown_tick()

    def _schedule_next_session_countdown_tick(self) -> None:
        if self.countdown_job is not None:
            try:
                self.after_cancel(self.countdown_job)
            except Exception:
                pass
        self.countdown_job = self.after(60_000, self._on_session_countdown_tick)

    def _on_session_countdown_tick(self) -> None:
        self._refresh_sidebar_countdown()
        self._schedule_next_session_countdown_tick()

    def _build_top_bar(self) -> None:
        self.top_bar = ctk.CTkFrame(self, fg_color=self.COLOR_TOPBAR, height=88, corner_radius=0)
        self.top_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.top_bar.grid_columnconfigure(0, weight=0, minsize=214)
        self.top_bar.grid_columnconfigure(1, weight=1)
        self.top_bar.grid_columnconfigure(2, weight=0)
        self.top_bar.grid_columnconfigure(3, weight=0)

        self.top_logo_image_ref = self._load_logo_image_fit(max_width=260, max_height=68)
        if self.top_logo_image_ref is not None:
            self.top_logo = ctk.CTkLabel(self.top_bar, text="", image=self.top_logo_image_ref)
        else:
            self.top_logo = ctk.CTkLabel(
                self.top_bar,
                text="SP",
                text_color=self.COLOR_NAV,
                font=ctk.CTkFont(size=22, weight="bold"),
            )
        self.top_logo.grid(row=0, column=0, padx=(8, 0), pady=10, sticky="")

        self.top_event_label = ctk.CTkLabel(
            self.top_bar,
            text="",
            text_color=self.COLOR_NAV,
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.top_event_label.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")

        self.lang_button = ctk.CTkButton(
            self.top_bar,
            text=self._language_toggle_label(),
            command=self.toggle_language,
            fg_color=self.COLOR_SOFT,
            text_color=self.COLOR_BG,
            hover_color=self.HOVER_SOFT,
            corner_radius=self.RADIUS_BUTTON,
            height=34,
            width=120,
        )
        self.lang_button.grid(row=0, column=3, padx=(8, 16), pady=10, sticky="e")

        self.notification_dot_button = ctk.CTkButton(
            self.top_bar,
            text="●",
            command=self.show_notifications_popup,
            fg_color=self.COLOR_SOFT,
            text_color=self.COLOR_BG,
            hover_color=self.HOVER_SOFT,
            corner_radius=16,
            width=34,
            height=34,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.notification_dot_button.grid(row=0, column=2, padx=(8, 0), pady=10, sticky="e")
        self._refresh_top_bar_event()

    def clear_content(self) -> None:
        for widget in self.content_frame.winfo_children():
            if widget is self._dashboard_frame:
                widget.grid_remove()
                continue
            widget.destroy()

    def _invalidate_dashboard(self) -> None:
        if self._dashboard_frame is not None:
            self._dashboard_frame.destroy()
        self._dashboard_frame = None
        self._calendar_grid = None
        self._week_range_label = None
        self._day_header_labels = []
        self._day_content_frames = []

    def show_page(self, page: str) -> None:
        self.active_page = page
        self.clear_content()
        for p, button in self.nav_buttons.items():
            button.configure(fg_color=self.COLOR_ACCENT if p != page else self.COLOR_SELECTED)
        self._refresh_top_bar_event()

        renderers = {
            "dashboard": self.render_dashboard,
            "add_subject": self.render_add_subject,
            "schedule_exams": self.render_schedule,
            "rules": self.render_rules,
            "progress": self.render_progress,
            "my_subjects": self.render_my_subjects,
            "subject_detail": self.render_subject_detail,
        }
        renderer = renderers.get(page)
        if renderer is not None:
            renderer()

    def render_dashboard(self) -> None:
        if self._dashboard_frame is not None:
            self._dashboard_frame.grid(sticky="nsew", padx=24, pady=24)
            self._update_week_view()
            return

        frame = ctk.CTkFrame(self.content_frame, fg_color=self.COLOR_BG)
        self._dashboard_frame = frame
        frame.grid(sticky="nsew", padx=24, pady=24)
        frame.grid_columnconfigure((0, 1), weight=1)
        frame.grid_rowconfigure(1, weight=1)

        header = ctk.CTkLabel(
            frame, text=self.t("dashboard"), font=ctk.CTkFont(size=28, weight="bold"), text_color=self.COLOR_LIGHT
        )
        header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

        calendar_box = ctk.CTkFrame(frame, fg_color=self.COLOR_NAV, corner_radius=self.RADIUS_PANEL)
        calendar_box.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        self._week_range_label = ctk.CTkLabel(calendar_box, text="", font=ctk.CTkFont(size=14))
        self._week_range_label.pack(anchor="w", padx=16, pady=(0, 8))

        nav_row = ctk.CTkFrame(calendar_box, fg_color=self.COLOR_NAV)
        nav_row.pack(fill="x", padx=16, pady=(0, 10))
        ctk.CTkButton(
            nav_row,
            text=self.t("prev_week"),
            command=lambda: self._change_week_offset(forward=False, back=True),
            fg_color=self.COLOR_ACCENT,
            hover_color=self.HOVER_ACCENT,
            height=30,
            width=140,
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            nav_row,
            text=self.t("next_week"),
            command=lambda: self._change_week_offset(forward=True),
            fg_color=self.COLOR_ACCENT,
            hover_color=self.HOVER_ACCENT,
            height=30,
            width=140,
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            nav_row,
            text=self.t("today_week"),
            command=lambda: self._change_week_offset(reset=True),
            fg_color=self.COLOR_SOFT,
            text_color=self.COLOR_BG,
            hover_color=self.HOVER_SOFT,
            height=30,
            width=180,
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            nav_row,
            text=self.t("pick_other_week"),
            command=self._open_week_picker,
            fg_color=self.COLOR_SOFT,
            text_color=self.COLOR_BG,
            hover_color=self.HOVER_SOFT,
            height=30,
            width=170,
        ).pack(side="left", padx=6)

        self._calendar_grid = ctk.CTkFrame(calendar_box, fg_color=self.COLOR_BG, corner_radius=self.RADIUS_PANEL)
        self._calendar_grid.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self._build_week_skeleton(self._calendar_grid)
        self._update_week_view()

        subject_box = ctk.CTkFrame(frame, fg_color=self.COLOR_NAV, corner_radius=self.RADIUS_PANEL)
        subject_box.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        subject_box.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(subject_box, text=self.t("subject_tiles"), font=ctk.CTkFont(size=18, weight="bold")).pack(
            anchor="w", padx=16, pady=(12, 4)
        )

        subjects = self.db.list_subjects()
        if not subjects:
            ctk.CTkLabel(subject_box, text=self.t("no_subjects"), wraplength=380, justify="left").pack(
                anchor="w", padx=16, pady=12
            )
        else:
            tiles = ctk.CTkScrollableFrame(subject_box, fg_color=self.COLOR_NAV)
            tiles.pack(fill="both", expand=True, padx=8, pady=(4, 8))
            for row in subjects:
                tile = ctk.CTkFrame(tiles, fg_color=self.COLOR_ACCENT, corner_radius=self.RADIUS_TILE)
                tile.pack(fill="x", padx=8, pady=6)
                ctk.CTkLabel(tile, text=row["name"], font=ctk.CTkFont(size=16, weight="bold")).pack(
                    anchor="w", padx=12, pady=(8, 2)
                )
                subtitle = f"{self.t('teacher')}: {row['teacher']} | {self.t('absence_count')}: {row['absences_count']}"
                ctk.CTkLabel(tile, text=subtitle).pack(anchor="w", padx=12, pady=(0, 8))

        events_box = ctk.CTkFrame(frame, fg_color=self.COLOR_NAV, corner_radius=self.RADIUS_PANEL)
        events_box.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        ctk.CTkLabel(events_box, text=self.t("upcoming_events"), font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=16, pady=(10, 6)
        )
        events = self.db.list_upcoming_events()[:5]
        if not events:
            ctk.CTkLabel(events_box, text="-").pack(anchor="w", padx=16, pady=(0, 10))
        else:
            for event in events:
                label = f"{event['event_date']} - {event['title']} ({event['subject_name'] or '---'})"
                ctk.CTkLabel(events_box, text=label).pack(anchor="w", padx=16, pady=2)
            ctk.CTkLabel(events_box, text=" ").pack()

    def render_add_subject(self) -> None:
        frame = self._single_panel(self.t("add_subject"))
        form = ctk.CTkScrollableFrame(frame, fg_color=self.COLOR_NAV)
        form.pack(fill="both", expand=True, padx=10, pady=10)
        self._enable_smooth_scroll(form, speed=0.3)

        name_entry = self._labeled_entry(form, self.t("subject"))
        teacher_entry = self._labeled_entry(form, self.t("teacher"))
        rules_entry = self._labeled_entry(form, self.t("grading_rules"))
        max_abs_entry = self._labeled_entry(form, self.t("max_absences"))
        max_abs_entry.insert(0, "0")
        max_activity_entry = self._labeled_entry(form, self.t("max_activity_points"))
        max_activity_entry.insert(0, "0")
        max_colloquium_entry = self._labeled_entry(form, self.t("max_colloquium_points"))
        max_colloquium_entry.insert(0, "0")
        start_time_entry = self._labeled_picker_entry(form, self.t("start_time"), kind="time")
        start_time_entry.insert(0, "08:00")
        duration_entry = self._labeled_entry(form, self.t("duration_hours"))
        duration_entry.insert(0, "1.5")
        start_date_entry = self._labeled_picker_entry(form, self.t("subject_start_date"), kind="date")
        end_date_entry = self._labeled_picker_entry(form, self.t("subject_end_date"), kind="date")

        ctk.CTkLabel(form, text=self.t("class_days")).pack(anchor="w", padx=16, pady=(8, 4))
        days_row = ctk.CTkFrame(form, fg_color=self.COLOR_NAV)
        days_row.pack(anchor="w", padx=16, pady=(0, 8))
        day_vars: list[ctk.StringVar] = []
        for idx in range(7):
            var = ctk.StringVar(value="0")
            day_vars.append(var)
            ctk.CTkCheckBox(
                days_row,
                text=self._weekday_abbr(idx),
                variable=var,
                onvalue="1",
                offvalue="0",
                checkbox_width=18,
                checkbox_height=18,
            ).grid(row=0, column=idx, padx=6, pady=4, sticky="w")

        def save_subject() -> None:
            name = name_entry.get().strip()
            teacher = teacher_entry.get().strip()
            rules = rules_entry.get().strip()
            max_abs = max_abs_entry.get().strip()
            max_activity = max_activity_entry.get().strip()
            max_colloquium = max_colloquium_entry.get().strip()
            start_time = start_time_entry.get().strip()
            duration_hours = duration_entry.get().strip()
            start_date = start_date_entry.get().strip()
            end_date = end_date_entry.get().strip()
            if not name or not teacher or not rules:
                messagebox.showerror(self.t("error"), self.t("required_fields"))
                return
            if not self._valid_time(start_time):
                messagebox.showerror(self.t("error"), "Invalid time format. Use HH:MM.")
                return
            if start_date and not self._valid_date(start_date):
                messagebox.showerror(self.t("error"), self.t("invalid_subject_dates"))
                return
            if end_date and not self._valid_date(end_date):
                messagebox.showerror(self.t("error"), self.t("invalid_subject_dates"))
                return
            if start_date and end_date:
                if datetime.strptime(end_date, "%Y-%m-%d") < datetime.strptime(start_date, "%Y-%m-%d"):
                    messagebox.showerror(self.t("error"), self.t("invalid_subject_dates"))
                    return
            selected_days = [idx for idx, var in enumerate(day_vars) if var.get() == "1"]
            if not selected_days:
                messagebox.showerror(self.t("error"), self.t("select_day"))
                return
            try:
                max_abs_i = max(0, int(max_abs or "0"))
                max_activity_f = max(0.0, float(max_activity or "0"))
                max_colloquium_f = max(0.0, float(max_colloquium or "0"))
                duration_minutes = max(30, int(float(duration_hours or "1") * 60))
            except ValueError:
                max_abs_i = 0
                max_activity_f = 0.0
                max_colloquium_f = 0.0
                duration_minutes = 60
            subject_id = self.db.add_subject(
                name, teacher, rules, max_abs_i, max_activity_f, max_colloquium_f,
                start_date, end_date,
            )
            for weekday in selected_days:
                self.db.add_recurring_class(subject_id, weekday, start_time, duration_minutes)
            messagebox.showinfo(self.t("saved"), self.t("saved"))
            self._invalidate_dashboard()
            self.show_page("dashboard")
            self.refresh_subject_options()

        ctk.CTkButton(
            form,
            text=self.t("save_subject"),
            command=save_subject,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.HOVER_ACCENT,
            height=36,
        ).pack(anchor="w", padx=16, pady=(4, 16))

    def render_schedule(self) -> None:
        frame = self._single_panel(self.t("schedule_exams"))

        body = ctk.CTkFrame(frame, fg_color=self.COLOR_BG)
        body.pack(fill="both", expand=True, padx=10, pady=10)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        panel = ctk.CTkFrame(body, fg_color=self.COLOR_NAV, corner_radius=self.RADIUS_PANEL)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(panel, text=self.t("subject_tiles"), font=ctk.CTkFont(size=16, weight="bold")).pack(
            anchor="w", padx=16, pady=(12, 4)
        )

        subjects = self.db.list_subjects()
        selected_subject_id = ctk.IntVar(value=int(subjects[0]["id"]) if subjects else -1)
        selected_subject_label = ctk.CTkLabel(panel, text="", font=ctk.CTkFont(size=13, weight="bold"))
        tile_refs: list[tuple[int, ctk.CTkFrame]] = []

        def update_selected_subject_ui() -> None:
            if selected_subject_id.get() < 0:
                selected_subject_label.configure(text=f"{self.t('selected_subject')}: -")
            else:
                name = next((s["name"] for s in subjects if int(s["id"]) == selected_subject_id.get()), "-")
                selected_subject_label.configure(text=f"{self.t('selected_subject')}: {name}")
            for sid, tile in tile_refs:
                tile.configure(fg_color=self.COLOR_SELECTED if sid == selected_subject_id.get() else self.COLOR_ACCENT)

        if subjects:
            tiles = ctk.CTkFrame(panel, fg_color=self.COLOR_NAV)
            tiles.pack(fill="x", padx=10, pady=(0, 8))
            max_cols = 4
            for idx, row in enumerate(subjects):
                sid = int(row["id"])
                tile = ctk.CTkFrame(tiles, fg_color=self.COLOR_ACCENT, corner_radius=self.RADIUS_TILE)
                grid_row = idx // max_cols
                grid_col = idx % max_cols
                tile.grid(row=grid_row, column=grid_col, padx=6, pady=6, sticky="ew")
                tiles.grid_columnconfigure(grid_col, weight=1)
                tile_refs.append((sid, tile))
                name_lbl = ctk.CTkLabel(tile, text=row["name"], font=ctk.CTkFont(size=14, weight="bold"))
                name_lbl.pack(
                    padx=14, pady=(8, 2)
                )
                teacher_lbl = ctk.CTkLabel(tile, text=row["teacher"])
                teacher_lbl.pack(padx=14, pady=(0, 8))
                tile.bind("<Button-1>", lambda _e, subject_id=sid: (selected_subject_id.set(subject_id), update_selected_subject_ui()))
                name_lbl.bind("<Button-1>", lambda _e, subject_id=sid: (selected_subject_id.set(subject_id), update_selected_subject_ui()))
                teacher_lbl.bind("<Button-1>", lambda _e, subject_id=sid: (selected_subject_id.set(subject_id), update_selected_subject_ui()))
            update_selected_subject_ui()
        else:
            ctk.CTkLabel(panel, text=self.t("no_subjects")).pack(anchor="w", padx=16, pady=(0, 8))

        selected_subject_label.pack(anchor="w", padx=16, pady=(0, 8))

        title_e = self._labeled_entry(panel, self.t("event_title"))
        date_e = self._labeled_picker_entry(panel, self.t("event_date"), kind="datetime")

        events_panel = ctk.CTkFrame(body, fg_color=self.COLOR_NAV, corner_radius=self.RADIUS_PANEL)
        events_panel.grid(row=0, column=1, sticky="nsew")
        events_panel.grid_columnconfigure(0, weight=1)
        events_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            events_panel,
            text=self.t("saved_events"),
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.COLOR_LIGHT,
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))

        events_list = ctk.CTkScrollableFrame(events_panel, fg_color=self.COLOR_NAV)
        events_list.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 12))
        events_list.grid_columnconfigure(0, weight=1)
        self._enable_smooth_scroll(events_list, speed=0.3)

        def render_events() -> None:
            for child in events_list.winfo_children():
                child.destroy()
            events = self.db.list_upcoming_events()
            if not events:
                ctk.CTkLabel(
                    events_list,
                    text=self.t("no_events"),
                    text_color=self.COLOR_SOFT,
                    font=ctk.CTkFont(size=13),
                    anchor="w",
                ).grid(row=0, column=0, sticky="ew", padx=10, pady=10)
                return
            for idx, ev in enumerate(events):
                event_id = int(ev["id"])
                tile = ctk.CTkFrame(events_list, fg_color=self.COLOR_ACCENT, corner_radius=self.RADIUS_TILE)
                tile.grid(row=idx, column=0, sticky="ew", padx=6, pady=4)
                tile.grid_columnconfigure(0, weight=1)

                date_raw = str(ev["event_date"])
                ctk.CTkLabel(
                    tile,
                    text=date_raw,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=self.COLOR_SOFT,
                    anchor="w",
                ).grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 2))
                ctk.CTkLabel(
                    tile,
                    text=str(ev["title"]),
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=self.COLOR_LIGHT,
                    anchor="w",
                ).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 2))
                subj_name = ev["subject_name"] if "subject_name" in ev.keys() else None
                if subj_name:
                    ctk.CTkLabel(
                        tile,
                        text=str(subj_name),
                        font=ctk.CTkFont(size=11),
                        text_color=self.COLOR_LIGHT,
                        anchor="w",
                    ).grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 8))
                else:
                    tile.grid_rowconfigure(2, minsize=8)

                def _delete(_e=None, eid=event_id) -> None:
                    confirmed = messagebox.askyesno(
                        self.t("delete_event"), self.t("confirm_delete_event")
                    )
                    if not confirmed:
                        return
                    self.db.delete_event(eid)
                    render_events()
                    self._refresh_top_bar_event()
                    self._invalidate_dashboard()

                del_btn = ctk.CTkButton(
                    tile,
                    text="✕",
                    width=28,
                    height=28,
                    fg_color=self.COLOR_DELETE,
                    hover_color=self.HOVER_DELETE,
                    text_color=self.COLOR_LIGHT,
                    corner_radius=14,
                    command=_delete,
                )
                del_btn.grid(row=0, column=1, rowspan=3, padx=(8, 10), pady=8, sticky="ne")

        def add_event() -> None:
            title = title_e.get().strip()
            date_str = date_e.get().strip()
            event_type = "exam"
            if not title or not date_str:
                messagebox.showerror(self.t("error"), self.t("required_fields"))
                return
            if not self._valid_datetime(date_str):
                messagebox.showerror(self.t("error"), "Invalid format. Use YYYY-MM-DD HH:MM.")
                return
            subject_id = selected_subject_id.get()
            if subject_id < 0:
                messagebox.showerror(self.t("error"), self.t("no_subjects"))
                return
            self.db.add_event(subject_id, title, date_str, event_type)
            self._refresh_top_bar_event()
            self._invalidate_dashboard()
            title_e.delete(0, "end")
            render_events()
            messagebox.showinfo(self.t("saved"), self.t("saved"))

        ctk.CTkButton(
            panel,
            text=self.t("confirm_add_event"),
            command=add_event,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.HOVER_ACCENT,
            height=36,
            width=180,
        ).pack(anchor="w", padx=16, pady=(8, 10))

        render_events()

    def render_rules(self) -> None:
        frame = self._single_panel(self.t("rules"))
        rules = self.db.get_subject_rules()

        if not rules:
            ctk.CTkLabel(
                frame,
                text=self.t("no_subjects"),
                text_color=self.COLOR_SOFT,
                font=ctk.CTkFont(size=14),
            ).pack(anchor="w", padx=16, pady=20)
            return

        if len(rules) <= 4:
            container = ctk.CTkFrame(frame, fg_color=self.COLOR_BG)
            container.pack(fill="both", expand=True, padx=10, pady=10, anchor="n")
        else:
            container = ctk.CTkScrollableFrame(frame, fg_color=self.COLOR_BG)
            container.pack(fill="both", expand=True, padx=10, pady=10)
            self._enable_smooth_scroll(container, speed=0.3)

        max_cols = 2
        for col in range(max_cols):
            container.grid_columnconfigure(col, weight=1, uniform="rules")

        for idx, r in enumerate(rules):
            grid_row = idx // max_cols
            grid_col = idx % max_cols

            card = ctk.CTkFrame(container, fg_color=self.COLOR_NAV, corner_radius=self.RADIUS_TILE)
            card.grid(row=grid_row, column=grid_col, padx=8, pady=8, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)

            header = ctk.CTkFrame(card, fg_color=self.COLOR_NAV)
            header.grid(row=0, column=0, sticky="ew", padx=14, pady=(14, 4))
            header.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                header,
                text=str(r["name"]),
                font=ctk.CTkFont(size=17, weight="bold"),
                text_color=self.COLOR_LIGHT,
                anchor="w",
                justify="left",
            ).grid(row=0, column=0, sticky="w")

            status = str(r["status"])
            status_badge = ctk.CTkLabel(
                header,
                text=self._status_label(status),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.COLOR_DARK_TEXT,
                fg_color=self._status_color(status),
                corner_radius=self.RADIUS_BADGE,
                padx=10,
                pady=2,
            )
            status_badge.grid(row=0, column=1, sticky="e", padx=(8, 0))

            ctk.CTkLabel(
                card,
                text=str(r["teacher"]) or "—",
                font=ctk.CTkFont(size=12),
                text_color=self.COLOR_SOFT,
                anchor="w",
            ).grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 10))

            absences_count = int(r["absences_count"])
            max_abs = int(r["max_absences"] or 0)
            ratio = (absences_count / max_abs) if max_abs > 0 else 0.0
            ratio = max(0.0, min(1.0, ratio))
            if max_abs == 0:
                progress_color = self.COLOR_ACCENT
            elif ratio >= 1.0:
                progress_color = self.COLOR_STATUS_RISK
            elif ratio >= 0.66:
                progress_color = self.COLOR_STATUS_IN_PROGRESS
            else:
                progress_color = self.COLOR_STATUS_PASSED

            absences_card = ctk.CTkFrame(card, fg_color=self.COLOR_ACCENT, corner_radius=self.RADIUS_BUTTON)
            absences_card.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 10))
            absences_card.grid_columnconfigure(0, weight=1)

            abs_top = ctk.CTkFrame(absences_card, fg_color=self.COLOR_ACCENT)
            abs_top.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
            abs_top.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                abs_top,
                text=self.t("absences_section"),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.COLOR_LIGHT,
                anchor="w",
            ).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(
                abs_top,
                text=f"{absences_count} / {max_abs}" if max_abs > 0 else f"{absences_count}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.COLOR_LIGHT,
                anchor="e",
            ).grid(row=0, column=1, sticky="e")

            progress = ctk.CTkProgressBar(
                absences_card,
                progress_color=progress_color,
                fg_color=self.COLOR_BG,
                height=8,
                corner_radius=4,
            )
            progress.set(ratio)
            progress.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))

            rules_text = str(r["grading_rules"]).strip() or "—"
            rules_card = ctk.CTkFrame(card, fg_color=self.COLOR_BG, corner_radius=self.RADIUS_BUTTON)
            rules_card.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 14))
            rules_card.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                rules_card,
                text=self.t("grading_rules"),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.COLOR_SOFT,
                anchor="w",
            ).grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 2))
            ctk.CTkLabel(
                rules_card,
                text=rules_text,
                font=ctk.CTkFont(size=13),
                text_color=self.COLOR_LIGHT,
                anchor="w",
                justify="left",
                wraplength=380,
            ).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))

    def render_progress(self) -> None:
        frame = self._single_panel(self.t("progress"))
        panel = ctk.CTkFrame(frame, fg_color=self.COLOR_NAV)
        panel.pack(fill="both", expand=True, padx=10, pady=10)

        subjects = self.db.list_subjects()
        if not subjects:
            ctk.CTkLabel(panel, text=self.t("no_subjects")).pack(anchor="w", padx=16, pady=16)
            return

        cards = ctk.CTkScrollableFrame(panel, fg_color=self.COLOR_NAV)
        cards.pack(fill="both", expand=True, padx=12, pady=12)
        self._enable_smooth_scroll(cards, speed=0.3)

        for subject in subjects:
            sid = int(subject["id"])

            card = ctk.CTkFrame(cards, fg_color=self.COLOR_LIGHT, corner_radius=self.RADIUS_TILE)
            card.pack(fill="x", padx=8, pady=8)

            ctk.CTkLabel(
                card,
                text=f"{subject['name']} ({subject['teacher']})",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=self.COLOR_BG,
            ).pack(anchor="w", padx=14, pady=(10, 4))

            header_points_label = ctk.CTkLabel(
                card,
                text="",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.COLOR_BG,
            )
            header_points_label.pack(anchor="w", padx=14, pady=(0, 6))

            progress_bar = ctk.CTkProgressBar(
                card,
                progress_color=self.COLOR_NAV,
                fg_color="#BFC3C5",
                height=14,
                corner_radius=self.RADIUS_BUTTON,
            )
            progress_bar.pack(fill="x", padx=14, pady=(0, 12))

            activity_row = ctk.CTkFrame(card, fg_color=self.COLOR_LIGHT)
            activity_row.pack(anchor="w", padx=14, pady=(0, 8))
            ctk.CTkLabel(
                activity_row,
                text=self.t("pluses"),
                text_color=self.COLOR_BG,
                font=ctk.CTkFont(size=13, weight="bold"),
            ).pack(side="left", padx=(0, 8))

            activity_value_label = ctk.CTkLabel(
                activity_row,
                text="0",
                text_color=self.COLOR_BG,
                font=ctk.CTkFont(size=16, weight="bold"),
                width=40,
            )
            activity_value_label.pack(side="left", padx=(0, 8))

            colloq_row = ctk.CTkFrame(card, fg_color=self.COLOR_LIGHT)
            colloq_row.pack(anchor="w", padx=14, pady=(0, 10))
            ctk.CTkLabel(
                colloq_row,
                text=self.t("colloquium_points"),
                text_color=self.COLOR_BG,
                font=ctk.CTkFont(size=13, weight="bold"),
            ).pack(side="left", padx=(0, 8))
            colloq_value_label = ctk.CTkLabel(
                colloq_row,
                text="0",
                text_color=self.COLOR_BG,
                font=ctk.CTkFont(size=16, weight="bold"),
                width=56,
            )
            colloq_value_label.pack(side="left", padx=(0, 8))

            def refresh_card(
                subject_id: int = sid,
                activity_label: ctk.CTkLabel = activity_value_label,
                colloq_label: ctk.CTkLabel = colloq_value_label,
                pbar: ctk.CTkProgressBar = progress_bar,
                points_label: ctk.CTkLabel = header_points_label,
            ) -> None:
                subj_row = self.db.get_subject(subject_id)
                max_activity_points = float(subj_row["max_activity_points"] or 0) if subj_row else 0.0
                max_colloquium_points = float(subj_row["max_colloquium_points"] or 0) if subj_row else 0.0
                pluses = self.db.get_activity_pluses(subject_id)
                colloq_points = self.db.get_colloquium_points(subject_id)
                total_current = pluses + colloq_points
                total_max = max(0.0, max_activity_points + max_colloquium_points)
                percent = int(round((total_current / total_max) * 100)) if total_max > 0 else 0

                activity_label.configure(text=str(pluses))
                colloq_label.configure(text=str(round(colloq_points, 2)).rstrip("0").rstrip("."))
                pbar.set(min(1.0, (total_current / total_max)) if total_max > 0 else 0)
                points_label.configure(
                    text=self.t("progress_points_text").format(
                        current=round(total_current, 2),
                        maximum=round(total_max, 2),
                        percent=percent,
                    )
                )

            ctk.CTkButton(
                activity_row,
                text=self.t("decrease"),
                width=42,
                fg_color=self.COLOR_DECREMENT,
                hover_color=self.HOVER_DECREMENT,
                command=lambda subject_id=sid, refresh_fn=refresh_card: (
                    self.db.update_activity_pluses(
                        subject_id,
                        -1,
                        float(self.db.get_subject(subject_id)["max_activity_points"] or 0),
                    ),
                    refresh_fn(),
                ),
            ).pack(side="left", padx=4)
            ctk.CTkButton(
                activity_row,
                text=self.t("increase"),
                width=42,
                fg_color=self.COLOR_INCREMENT,
                hover_color=self.HOVER_INCREMENT,
                command=lambda subject_id=sid, refresh_fn=refresh_card: (
                    self.db.update_activity_pluses(
                        subject_id,
                        1,
                        float(self.db.get_subject(subject_id)["max_activity_points"] or 0),
                    ),
                    refresh_fn(),
                ),
            ).pack(side="left", padx=4)
            ctk.CTkButton(
                colloq_row,
                text=self.t("decrease"),
                width=42,
                fg_color=self.COLOR_DECREMENT,
                hover_color=self.HOVER_DECREMENT,
                command=lambda subject_id=sid, refresh_fn=refresh_card: (
                    self.db.update_colloquium_points(
                        subject_id,
                        -1,
                        float(self.db.get_subject(subject_id)["max_colloquium_points"] or 0),
                    ),
                    refresh_fn(),
                ),
            ).pack(side="left", padx=4)
            ctk.CTkButton(
                colloq_row,
                text=self.t("increase"),
                width=42,
                fg_color=self.COLOR_INCREMENT,
                hover_color=self.HOVER_INCREMENT,
                command=lambda subject_id=sid, refresh_fn=refresh_card: (
                    self.db.update_colloquium_points(
                        subject_id,
                        1,
                        float(self.db.get_subject(subject_id)["max_colloquium_points"] or 0),
                    ),
                    refresh_fn(),
                ),
            ).pack(side="left", padx=4)

            refresh_card()

    def render_my_subjects(self) -> None:
        frame = self._single_panel(self.t("my_subjects"))
        subjects = self.db.list_subjects()
        if not subjects:
            ctk.CTkLabel(frame, text=self.t("no_subjects")).pack(anchor="w", padx=16, pady=16)
            return

        if len(subjects) <= 6:
            tiles = ctk.CTkFrame(frame, fg_color=self.COLOR_NAV)
            tiles.pack(fill="both", expand=True, padx=16, pady=10, anchor="n")
        else:
            tiles = ctk.CTkScrollableFrame(frame, fg_color=self.COLOR_NAV)
            tiles.pack(fill="both", expand=True, padx=16, pady=10)
            self._enable_smooth_scroll(tiles, speed=0.3)

        max_cols = 3
        for col in range(max_cols):
            tiles.grid_columnconfigure(col, weight=1)

        for idx, row in enumerate(subjects):
            sid = int(row["id"])
            status = str(row["status"])
            tile_color = self._status_color(status)
            text_color = self.COLOR_DARK_TEXT if status in {"passed", "risk"} else self.COLOR_BG

            tile = ctk.CTkFrame(tiles, fg_color=tile_color, corner_radius=self.RADIUS_TILE)
            grid_row = idx // max_cols
            grid_col = idx % max_cols
            tile.grid(row=grid_row, column=grid_col, padx=8, pady=8, sticky="ew")

            name_lbl = ctk.CTkLabel(
                tile,
                text=row["name"],
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=text_color,
                anchor="w",
            )
            name_lbl.pack(fill="x", padx=12, pady=(10, 2))
            teacher_lbl = ctk.CTkLabel(
                tile,
                text=row["teacher"],
                font=ctk.CTkFont(size=12),
                text_color=text_color,
                anchor="w",
            )
            teacher_lbl.pack(fill="x", padx=12, pady=(0, 4))
            status_lbl = ctk.CTkLabel(
                tile,
                text=self._status_label(status),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=text_color,
                anchor="w",
            )
            status_lbl.pack(fill="x", padx=12, pady=(0, 10))

            def _open(_event=None, subject_id=sid):
                self._selected_subject_id = subject_id
                self.show_page("subject_detail")

            for widget in (tile, name_lbl, teacher_lbl, status_lbl):
                widget.bind("<Button-1>", _open)
                try:
                    widget.configure(cursor="hand2")
                except Exception:
                    pass

    def render_subject_detail(self) -> None:
        sid = self._selected_subject_id
        subject = self.db.get_subject(sid) if sid is not None else None
        if subject is None:
            self.show_page("my_subjects")
            return

        frame = self._single_panel(f"{self.t('subject_details')}: {subject['name']}")

        top_row = ctk.CTkFrame(frame, fg_color=self.COLOR_BG)
        top_row.pack(fill="x", padx=10, pady=(0, 6))
        ctk.CTkButton(
            top_row,
            text="← " + self.t("back"),
            command=lambda: self.show_page("my_subjects"),
            fg_color=self.COLOR_SOFT,
            text_color=self.COLOR_BG,
            hover_color=self.HOVER_SOFT,
            width=100,
            height=32,
        ).pack(side="left")

        body = ctk.CTkFrame(frame, fg_color=self.COLOR_BG)
        body.pack(fill="both", expand=True, padx=10, pady=10)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(body, fg_color=self.COLOR_BG)
        scroll.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self._enable_smooth_scroll(scroll, speed=0.3)

        note_card = ctk.CTkFrame(body, fg_color=self.COLOR_NAV, corner_radius=self.RADIUS_PANEL)
        note_card.grid(row=0, column=1, sticky="nsew")
        note_card.grid_rowconfigure(1, weight=1)
        note_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            note_card,
            text=self.t("general_note"),
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))

        note_textbox = ctk.CTkTextbox(
            note_card,
            fg_color=self.COLOR_LIGHT,
            text_color=self.COLOR_BG,
            corner_radius=self.RADIUS_BUTTON,
        )
        note_textbox.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 8))
        existing_general = ""
        try:
            existing_general = str(subject["general_note"] or "")
        except (KeyError, IndexError):
            existing_general = ""
        if existing_general:
            note_textbox.insert("1.0", existing_general)

        def save_general_note() -> None:
            content = note_textbox.get("1.0", "end").rstrip("\n")
            self.db.update_general_note(sid, content)
            messagebox.showinfo(self.t("saved"), self.t("saved"))

        ctk.CTkButton(
            note_card,
            text=self.t("save_note"),
            command=save_general_note,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.HOVER_ACCENT,
            height=36,
        ).grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 14))

        # ---- Status section ----
        status_card = ctk.CTkFrame(scroll, fg_color=self.COLOR_NAV, corner_radius=self.RADIUS_PANEL)
        status_card.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            status_card,
            text=self.t("current_status"),
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=14, pady=(10, 4))
        status_value_lbl = ctk.CTkLabel(
            status_card,
            text=self._status_label(str(subject["status"])),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self._status_color(str(subject["status"])),
        )
        status_value_lbl.pack(anchor="w", padx=14, pady=(0, 8))

        status_btn_row = ctk.CTkFrame(status_card, fg_color=self.COLOR_NAV)
        status_btn_row.pack(fill="x", padx=14, pady=(0, 12))
        status_btn_row.grid_columnconfigure((0, 1, 2), weight=1)
        status_buttons: dict[str, ctk.CTkButton] = {}

        def apply_status(new_status: str) -> None:
            self.db.set_subject_status(sid, new_status)
            status_value_lbl.configure(
                text=self._status_label(new_status),
                text_color=self._status_color(new_status),
            )
            for st_key, btn in status_buttons.items():
                btn.configure(border_width=2 if st_key == new_status else 0)

        for col, (key, label_key, color) in enumerate(
            [
                ("passed", "status_passed", self.COLOR_STATUS_PASSED),
                ("in_progress", "status_in_progress", self.COLOR_STATUS_IN_PROGRESS),
                ("risk", "status_risk", self.COLOR_STATUS_RISK),
            ]
        ):
            btn = ctk.CTkButton(
                status_btn_row,
                text=self.t(label_key),
                command=lambda s=key: apply_status(s),
                fg_color=color,
                text_color=self.COLOR_DARK_TEXT,
                hover_color=self.HOVER_DIM,
                border_color=self.COLOR_LIGHT,
                border_width=2 if str(subject["status"]) == key else 0,
                height=34,
            )
            btn.grid(row=0, column=col, padx=4, sticky="ew")
            status_buttons[key] = btn

        # ---- Absences section ----
        absences_card = ctk.CTkFrame(scroll, fg_color=self.COLOR_NAV, corner_radius=self.RADIUS_PANEL)
        absences_card.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            absences_card,
            text=self.t("absences_section"),
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=14, pady=(10, 4))

        max_abs = int(subject["max_absences"] or 0)
        abs_count_var = ctk.StringVar(
            value=f"{int(subject['absences_count'])} / {max_abs}" if max_abs else f"{int(subject['absences_count'])}"
        )
        abs_value_lbl = ctk.CTkLabel(
            absences_card,
            textvariable=abs_count_var,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.COLOR_LIGHT,
        )
        abs_value_lbl.pack(anchor="w", padx=14, pady=(0, 8))

        abs_btn_row = ctk.CTkFrame(absences_card, fg_color=self.COLOR_NAV)
        abs_btn_row.pack(anchor="w", padx=14, pady=(0, 12))

        def refresh_abs() -> None:
            row = self.db.get_subject(sid)
            if row is None:
                return
            current = int(row["absences_count"])
            mx = int(row["max_absences"] or 0)
            abs_count_var.set(f"{current} / {mx}" if mx else str(current))

        def change_abs(delta: int) -> None:
            self.db.update_absences(sid, delta)
            refresh_abs()

        ctk.CTkButton(
            abs_btn_row, text="-", width=44, height=36,
            fg_color=self.COLOR_DELETE, hover_color=self.HOVER_DELETE,
            command=lambda: change_abs(-1),
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            abs_btn_row, text="+", width=44, height=36,
            fg_color=self.COLOR_ACCENT, hover_color=self.HOVER_ACCENT,
            command=lambda: change_abs(1),
        ).pack(side="left")

        # ---- Edit form ----
        edit_card = ctk.CTkFrame(scroll, fg_color=self.COLOR_NAV, corner_radius=self.RADIUS_PANEL)
        edit_card.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            edit_card,
            text=self.t("edit_subject"),
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(anchor="w", padx=14, pady=(12, 6))

        edit_form = ctk.CTkFrame(edit_card, fg_color=self.COLOR_NAV)
        edit_form.pack(fill="x", padx=4, pady=(0, 8))

        name_entry = self._labeled_entry(edit_form, self.t("subject"))
        name_entry.insert(0, str(subject["name"]))
        teacher_entry = self._labeled_entry(edit_form, self.t("teacher"))
        teacher_entry.insert(0, str(subject["teacher"]))
        rules_entry = self._labeled_entry(edit_form, self.t("grading_rules"))
        rules_entry.insert(0, str(subject["grading_rules"]))
        max_abs_entry = self._labeled_entry(edit_form, self.t("max_absences"))
        max_abs_entry.insert(0, str(int(subject["max_absences"] or 0)))
        max_activity_entry = self._labeled_entry(edit_form, self.t("max_activity_points"))
        max_activity_entry.insert(0, str(float(subject["max_activity_points"] or 0)))
        max_colloquium_entry = self._labeled_entry(edit_form, self.t("max_colloquium_points"))
        max_colloquium_entry.insert(0, str(float(subject["max_colloquium_points"] or 0)))
        start_date_entry = self._labeled_picker_entry(edit_form, self.t("subject_start_date"), kind="date")
        try:
            start_date_entry.insert(0, str(subject["start_date"] or ""))
        except (KeyError, IndexError):
            pass
        end_date_entry = self._labeled_picker_entry(edit_form, self.t("subject_end_date"), kind="date")
        try:
            end_date_entry.insert(0, str(subject["end_date"] or ""))
        except (KeyError, IndexError):
            pass

        def save_changes() -> None:
            name = name_entry.get().strip()
            teacher = teacher_entry.get().strip()
            rules = rules_entry.get().strip()
            if not name or not teacher or not rules:
                messagebox.showerror(self.t("error"), self.t("required_fields"))
                return
            start_date = start_date_entry.get().strip()
            end_date = end_date_entry.get().strip()
            if start_date and not self._valid_date(start_date):
                messagebox.showerror(self.t("error"), self.t("invalid_subject_dates"))
                return
            if end_date and not self._valid_date(end_date):
                messagebox.showerror(self.t("error"), self.t("invalid_subject_dates"))
                return
            if start_date and end_date:
                if datetime.strptime(end_date, "%Y-%m-%d") < datetime.strptime(start_date, "%Y-%m-%d"):
                    messagebox.showerror(self.t("error"), self.t("invalid_subject_dates"))
                    return
            try:
                max_abs_i = max(0, int(max_abs_entry.get().strip() or "0"))
                max_activity_f = max(0.0, float(max_activity_entry.get().strip() or "0"))
                max_colloquium_f = max(0.0, float(max_colloquium_entry.get().strip() or "0"))
            except ValueError:
                messagebox.showerror(self.t("error"), self.t("required_fields"))
                return
            self.db.update_subject(
                sid,
                name,
                teacher,
                rules,
                max_abs_i,
                max_activity_f,
                max_colloquium_f,
                start_date,
                end_date,
            )
            messagebox.showinfo(self.t("saved"), self.t("saved"))
            self._invalidate_dashboard()
            self.show_page("subject_detail")

        action_row = ctk.CTkFrame(edit_card, fg_color=self.COLOR_NAV)
        action_row.pack(fill="x", padx=14, pady=(4, 14))

        ctk.CTkButton(
            action_row,
            text=self.t("save_changes"),
            command=save_changes,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.HOVER_ACCENT,
            height=36,
            width=180,
        ).pack(side="left")

        def delete_self() -> None:
            confirmed = messagebox.askyesno(self.t("delete_subject"), self.t("confirm_delete_subject"))
            if not confirmed:
                return
            self.db.delete_subject(sid)
            self._selected_subject_id = None
            messagebox.showinfo(self.t("saved"), self.t("saved"))
            self._invalidate_dashboard()
            self.show_page("my_subjects")

        ctk.CTkButton(
            action_row,
            text=self.t("delete_subject"),
            command=delete_self,
            fg_color=self.COLOR_DELETE,
            hover_color=self.HOVER_DELETE,
            text_color=self.COLOR_LIGHT,
            height=36,
            width=180,
        ).pack(side="right")

    def _single_panel(self, title: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.content_frame, fg_color=self.COLOR_BG)
        frame.grid(sticky="nsew", padx=22, pady=22)
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=28, weight="bold"), text_color=self.COLOR_LIGHT).pack(
            anchor="w", padx=10, pady=(0, 8)
        )
        return frame

    def _load_logo_image_fit(self, max_width: int, max_height: int) -> ctk.CTkImage | None:
        """Load the logo asset and scale it to fit the given bounding box.

        Returns ``None`` when the asset cannot be found or read so callers can
        fall back to a textual placeholder gracefully.
        """
        if not self.LOGO_PATH.exists():
            return None
        try:
            image = Image.open(self.LOGO_PATH)
        except Exception:
            return None
        width, height = image.size
        if width <= 0 or height <= 0:
            return None
        scale = min(max_width / width, max_height / height, 1.0)
        target = (max(1, int(width * scale)), max(1, int(height * scale)))
        return ctk.CTkImage(light_image=image, dark_image=image, size=target)

    def _refresh_top_bar_event(self) -> None:
        closest = self._closest_priority_event()
        if closest is None:
            self.top_event_label.configure(text=f"{self.t('closest_event')}: {self.t('closest_none')}")
            self.notification_dot_button.configure(text="●")
            return

        date_str = closest["event_date"]
        event_type = str(closest["event_type"]).strip()
        title = closest["title"]
        subject = closest["subject_name"] or "---"
        info = f"{self.t('closest_event')}: {date_str} | {event_type} | {title} ({subject})"
        self.top_event_label.configure(text=info)
        upcoming_count = len(self._priority_events_sorted())
        self.notification_dot_button.configure(text=f"●{upcoming_count}" if upcoming_count > 0 else "●")

    def _closest_priority_event(self):
        candidates = self._priority_events_sorted()
        if not candidates:
            return None
        return candidates[0]

    def _priority_events_sorted(self) -> list:
        priority_types = {"exam", "colloquium", "kolokwium"}
        now = datetime.now()
        candidates = []
        for event in self.db.list_upcoming_events():
            event_dt = self._parse_event_datetime(str(event["event_date"]))
            if event_dt is None:
                continue
            if event_dt < now:
                continue
            if str(event["event_type"]).strip().lower() not in priority_types:
                continue
            candidates.append(event)
        return sorted(
            candidates,
            key=lambda e: (
                self._parse_event_datetime(str(e["event_date"])) or datetime.max,
                str(e["title"]).lower(),
            ),
        )

    def show_notifications_popup(self) -> None:
        items = self._priority_events_sorted()[:8]
        if not items:
            messagebox.showinfo("Student Planner", self.t("closest_none"))
            return

        lines = []
        for event in items:
            subject = event["subject_name"] or "---"
            lines.append(f"{event['event_date']} | {event['event_type']} | {event['title']} ({subject})")
        messagebox.showinfo("Student Planner", "\n".join(lines))

    def _language_toggle_label(self) -> str:
        return "ANG" if self.language == "pl" else "POL"

    def _labeled_entry(self, parent: ctk.CTkFrame, label: str) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label).pack(anchor="w", padx=16, pady=(8, 2))
        entry = ctk.CTkEntry(parent, fg_color=self.COLOR_BG, text_color=self.COLOR_LIGHT, width=420)
        entry.pack(anchor="w", padx=16, pady=(0, 4))
        return entry

    def _labeled_picker_entry(
        self,
        parent: ctk.CTkFrame,
        label: str,
        kind: str = "date",
    ) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label).pack(anchor="w", padx=16, pady=(8, 2))
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(anchor="w", padx=16, pady=(0, 4), fill="x")
        entry = ctk.CTkEntry(row, fg_color=self.COLOR_BG, text_color=self.COLOR_LIGHT, width=360)
        entry.pack(side="left")
        icon = {"date": "📅", "time": "🕒", "datetime": "📅"}.get(kind, "📅")

        def open_picker() -> None:
            if kind == "time":
                self._open_time_picker(entry)
            elif kind == "datetime":
                self._open_datetime_picker(entry)
            else:
                self._open_date_picker(entry)

        ctk.CTkButton(
            row,
            text=icon,
            command=open_picker,
            width=44,
            height=28,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.HOVER_ACCENT,
            text_color=self.COLOR_LIGHT,
            corner_radius=self.RADIUS_BUTTON,
        ).pack(side="left", padx=(8, 0))
        return entry

    def _build_month_calendar(
        self,
        parent: ctk.CTkFrame,
        initial: datetime,
        on_pick,
    ) -> None:
        state = {"year": initial.year, "month": initial.month}
        header_label = ctk.CTkLabel(
            parent,
            text="",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.COLOR_LIGHT,
        )
        header_label.pack(pady=(0, 6))

        nav = ctk.CTkFrame(parent, fg_color="transparent")
        nav.pack(fill="x", padx=4)
        grid_box = ctk.CTkFrame(parent, fg_color="transparent")
        grid_box.pack(fill="both", expand=True, padx=4, pady=8)

        def shift_month(delta: int) -> None:
            new_month = state["month"] + delta
            new_year = state["year"]
            while new_month < 1:
                new_month += 12
                new_year -= 1
            while new_month > 12:
                new_month -= 12
                new_year += 1
            state["month"] = new_month
            state["year"] = new_year
            redraw()

        def redraw() -> None:
            for child in grid_box.winfo_children():
                child.destroy()
            for child in nav.winfo_children():
                child.destroy()

            ctk.CTkButton(
                nav,
                text="<",
                width=36,
                height=28,
                command=lambda: shift_month(-1),
                fg_color=self.COLOR_ACCENT,
                hover_color=self.HOVER_ACCENT,
                corner_radius=self.RADIUS_BUTTON,
            ).pack(side="left")
            ctk.CTkButton(
                nav,
                text=">",
                width=36,
                height=28,
                command=lambda: shift_month(1),
                fg_color=self.COLOR_ACCENT,
                hover_color=self.HOVER_ACCENT,
                corner_radius=self.RADIUS_BUTTON,
            ).pack(side="right")
            header_label.configure(text=f"{state['year']}-{state['month']:02d}")

            for col in range(7):
                grid_box.grid_columnconfigure(col, weight=1)
                ctk.CTkLabel(
                    grid_box,
                    text=self._weekday_abbr(col),
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=self.COLOR_SOFT,
                ).grid(row=0, column=col, padx=2, pady=(0, 4), sticky="n")

            month_matrix = calendar.monthcalendar(state["year"], state["month"])
            today = datetime.now().date()
            for r_idx, week in enumerate(month_matrix, start=1):
                for c_idx, day in enumerate(week):
                    if day == 0:
                        continue
                    is_today = (
                        state["year"] == today.year
                        and state["month"] == today.month
                        and day == today.day
                    )
                    btn = ctk.CTkButton(
                        grid_box,
                        text=str(day),
                        width=36,
                        height=30,
                        fg_color=self.COLOR_TODAY if is_today else self.COLOR_ACCENT,
                        hover_color=self.HOVER_ACCENT,
                        corner_radius=self.RADIUS_BUTTON,
                        command=lambda y=state["year"], m=state["month"], d=day: on_pick(y, m, d),
                    )
                    btn.grid(row=r_idx, column=c_idx, padx=2, pady=2, sticky="ew")

        redraw()

    def _build_time_spinners(
        self,
        parent: ctk.CTkFrame,
        initial_hour: int,
        initial_minute: int,
    ) -> tuple[ctk.IntVar, ctk.IntVar]:
        hour_var = ctk.IntVar(value=initial_hour)
        minute_var = ctk.IntVar(value=initial_minute)

        wrapper = ctk.CTkFrame(parent, fg_color="transparent")
        wrapper.pack(pady=(8, 6))

        def make_column(col_label: str, var: ctk.IntVar, lo: int, hi: int) -> None:
            box = ctk.CTkFrame(wrapper, fg_color=self.COLOR_NAV, corner_radius=self.RADIUS_BUTTON)
            box.pack(side="left", padx=8, pady=4)

            ctk.CTkLabel(
                box,
                text=col_label,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.COLOR_SOFT,
            ).pack(padx=14, pady=(8, 2))

            value_label = ctk.CTkLabel(
                box,
                text=f"{var.get():02d}",
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color=self.COLOR_LIGHT,
                width=70,
            )
            value_label.pack(padx=14, pady=2)

            def step(delta: int) -> None:
                new_val = var.get() + delta
                if new_val < lo:
                    new_val = hi
                elif new_val > hi:
                    new_val = lo
                var.set(new_val)
                value_label.configure(text=f"{new_val:02d}")

            btns = ctk.CTkFrame(box, fg_color="transparent")
            btns.pack(pady=(2, 10), padx=14)
            ctk.CTkButton(
                btns,
                text="−",
                width=32,
                height=28,
                fg_color=self.COLOR_ACCENT,
                hover_color=self.HOVER_ACCENT,
                corner_radius=self.RADIUS_BUTTON,
                command=lambda: step(-1),
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                btns,
                text="+",
                width=32,
                height=28,
                fg_color=self.COLOR_ACCENT,
                hover_color=self.HOVER_ACCENT,
                corner_radius=self.RADIUS_BUTTON,
                command=lambda: step(1),
            ).pack(side="left", padx=2)

        make_column(self.t("hours_label"), hour_var, 0, 23)
        ctk.CTkLabel(
            wrapper,
            text=":",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.COLOR_LIGHT,
        ).pack(side="left", padx=2)
        make_column(self.t("minutes_label"), minute_var, 0, 59)
        return hour_var, minute_var

    def _open_date_picker(self, target_entry: ctk.CTkEntry) -> None:
        current = target_entry.get().strip()
        if current and self._valid_date(current):
            initial = datetime.strptime(current, "%Y-%m-%d")
        else:
            initial = datetime.now()

        dlg = ctk.CTkToplevel(self)
        dlg.title(self.t("pick_date_title"))
        dlg.geometry("360x360")
        dlg.configure(fg_color=self.COLOR_BG)
        dlg.transient(self)
        dlg.grab_set()

        ctk.CTkLabel(
            dlg,
            text=self.t("pick_date_title"),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.COLOR_LIGHT,
        ).pack(pady=(12, 0))

        body = ctk.CTkFrame(dlg, fg_color=self.COLOR_BG)
        body.pack(fill="both", expand=True, padx=12, pady=8)

        def on_pick(year: int, month: int, day: int) -> None:
            iso = f"{year:04d}-{month:02d}-{day:02d}"
            target_entry.delete(0, "end")
            target_entry.insert(0, iso)
            dlg.destroy()

        self._build_month_calendar(body, initial, on_pick)

    def _open_time_picker(self, target_entry: ctk.CTkEntry) -> None:
        current = target_entry.get().strip()
        if current and self._valid_time(current):
            initial_hour, initial_minute = (int(p) for p in current.split(":"))
        else:
            now = datetime.now()
            initial_hour, initial_minute = now.hour, now.minute

        dlg = ctk.CTkToplevel(self)
        dlg.title(self.t("pick_time_title"))
        dlg.geometry("320x260")
        dlg.configure(fg_color=self.COLOR_BG)
        dlg.transient(self)
        dlg.grab_set()

        ctk.CTkLabel(
            dlg,
            text=self.t("pick_time_title"),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.COLOR_LIGHT,
        ).pack(pady=(14, 4))

        hour_var, minute_var = self._build_time_spinners(dlg, initial_hour, initial_minute)

        btn_row = ctk.CTkFrame(dlg, fg_color=self.COLOR_BG)
        btn_row.pack(fill="x", padx=14, pady=(8, 14))

        def confirm() -> None:
            target_entry.delete(0, "end")
            target_entry.insert(0, f"{int(hour_var.get()):02d}:{int(minute_var.get()):02d}")
            dlg.destroy()

        ctk.CTkButton(
            btn_row,
            text=self.t("close"),
            command=dlg.destroy,
            fg_color=self.COLOR_SOFT,
            text_color=self.COLOR_BG,
            hover_color=self.HOVER_SOFT,
            corner_radius=self.RADIUS_BUTTON,
            width=120,
        ).pack(side="left")
        ctk.CTkButton(
            btn_row,
            text=self.t("confirm"),
            command=confirm,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.HOVER_ACCENT,
            corner_radius=self.RADIUS_BUTTON,
            width=120,
        ).pack(side="right")

    def _open_datetime_picker(self, target_entry: ctk.CTkEntry) -> None:
        current = target_entry.get().strip()
        initial_dt: datetime
        if current and self._valid_datetime(current):
            initial_dt = datetime.strptime(current, "%Y-%m-%d %H:%M")
        else:
            now = datetime.now()
            initial_dt = now.replace(second=0, microsecond=0)

        chosen = {"date": initial_dt.date()}
        hour_var: ctk.IntVar
        minute_var: ctk.IntVar

        dlg = ctk.CTkToplevel(self)
        dlg.title(self.t("pick_datetime_title"))
        dlg.geometry("680x440")
        dlg.configure(fg_color=self.COLOR_BG)
        dlg.transient(self)
        dlg.grab_set()

        ctk.CTkLabel(
            dlg,
            text=self.t("pick_datetime_title"),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.COLOR_LIGHT,
        ).pack(pady=(12, 4))

        body = ctk.CTkFrame(dlg, fg_color=self.COLOR_BG)
        body.pack(fill="both", expand=True, padx=12, pady=4)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        cal_frame = ctk.CTkFrame(body, fg_color=self.COLOR_NAV, corner_radius=self.RADIUS_PANEL)
        cal_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        cal_inner = ctk.CTkFrame(cal_frame, fg_color="transparent")
        cal_inner.pack(fill="both", expand=True, padx=10, pady=10)

        time_frame = ctk.CTkFrame(body, fg_color=self.COLOR_NAV, corner_radius=self.RADIUS_PANEL)
        time_frame.grid(row=0, column=1, sticky="nsew")
        time_inner = ctk.CTkFrame(time_frame, fg_color="transparent")
        time_inner.pack(fill="both", expand=True, padx=10, pady=10)

        chosen_label = ctk.CTkLabel(
            dlg,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.COLOR_LIGHT,
        )
        chosen_label.pack(pady=(2, 4))

        def update_chosen_label() -> None:
            chosen_label.configure(
                text=f"{chosen['date'].isoformat()} {int(hour_var.get()):02d}:{int(minute_var.get()):02d}"
            )

        def on_date_pick(year: int, month: int, day: int) -> None:
            chosen["date"] = datetime(year, month, day).date()
            update_chosen_label()

        self._build_month_calendar(cal_inner, initial_dt, on_date_pick)
        hour_var, minute_var = self._build_time_spinners(time_inner, initial_dt.hour, initial_dt.minute)
        for var in (hour_var, minute_var):
            var.trace_add("write", lambda *_: update_chosen_label())
        update_chosen_label()

        btn_row = ctk.CTkFrame(dlg, fg_color=self.COLOR_BG)
        btn_row.pack(fill="x", padx=14, pady=(0, 14))

        def confirm() -> None:
            d = chosen["date"]
            iso = (
                f"{d.year:04d}-{d.month:02d}-{d.day:02d} "
                f"{int(hour_var.get()):02d}:{int(minute_var.get()):02d}"
            )
            target_entry.delete(0, "end")
            target_entry.insert(0, iso)
            dlg.destroy()

        ctk.CTkButton(
            btn_row,
            text=self.t("close"),
            command=dlg.destroy,
            fg_color=self.COLOR_SOFT,
            text_color=self.COLOR_BG,
            hover_color=self.HOVER_SOFT,
            corner_radius=self.RADIUS_BUTTON,
            width=120,
        ).pack(side="left")
        ctk.CTkButton(
            btn_row,
            text=self.t("confirm"),
            command=confirm,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.HOVER_ACCENT,
            corner_radius=self.RADIUS_BUTTON,
            width=120,
        ).pack(side="right")

    def _valid_date(self, date_str: str) -> bool:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def _enable_smooth_scroll(self, scrollable: ctk.CTkScrollableFrame, speed: float = 0.35) -> None:
        canvas = getattr(scrollable, "_parent_canvas", None)
        if canvas is None:
            return

        def on_mousewheel(event) -> str:
            delta = 0
            if hasattr(event, "delta") and event.delta:
                # On macOS event.delta is usually small; scale down for smoother scroll.
                raw = float(event.delta) * speed
                if raw > 0:
                    delta = -max(1, int(abs(raw) / 2))
                else:
                    delta = max(1, int(abs(raw) / 2))
            elif getattr(event, "num", None) == 4:
                delta = -1
            elif getattr(event, "num", None) == 5:
                delta = 1

            if delta != 0:
                first, last = canvas.yview()
                # Block overscroll into blank space at top/bottom.
                if first <= 0.0 and delta < 0:
                    return "break"
                if last >= 1.0 and delta > 0:
                    return "break"
                canvas.yview_scroll(delta, "units")
            return "break"

        def bind_recursive(widget) -> None:
            widget.bind("<MouseWheel>", on_mousewheel, add="+")
            widget.bind("<Button-4>", on_mousewheel, add="+")
            widget.bind("<Button-5>", on_mousewheel, add="+")
            for child in widget.winfo_children():
                bind_recursive(child)

        bind_recursive(scrollable)

    def _valid_time(self, time_str: str) -> bool:
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False

    def _valid_datetime(self, dt_str: str) -> bool:
        try:
            datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
            return True
        except ValueError:
            return False

    def _parse_event_datetime(self, raw: str) -> datetime | None:
        raw = raw.strip()
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw, fmt)
            except ValueError:
                continue
        return None

    def _status_label(self, status: str) -> str:
        if status == "passed":
            return self.t("status_passed")
        if status == "risk":
            return self.t("status_risk")
        return self.t("status_in_progress")

    def _status_color(self, status: str) -> str:
        if status == "passed":
            return self.COLOR_STATUS_PASSED
        if status == "risk":
            return self.COLOR_STATUS_RISK
        return self.COLOR_LIGHT

    REFRESHABLE_PAGES = frozenset(
        {
            "dashboard",
            "schedule_exams",
            "rules",
            "progress",
            "my_subjects",
            "subject_detail",
        }
    )

    def refresh_subject_options(self) -> None:
        """Re-render the active page so newly added subjects show up everywhere."""
        if self.active_page in self.REFRESHABLE_PAGES:
            self.show_page(self.active_page)

    def _current_week_start(self) -> datetime:
        now = datetime.now()
        return now - timedelta(days=now.weekday())

    def _change_week_offset(self, forward: bool = False, back: bool = False, reset: bool = False) -> None:
        if reset:
            self.week_offset = 0
        elif forward:
            self.week_offset += 1
        elif back:
            self.week_offset -= 1
        if self.active_page == "dashboard":
            self._update_week_view()

    def _update_week_view(self) -> None:
        if not hasattr(self, "_calendar_grid") or not hasattr(self, "_week_range_label"):
            return
        week_start = self._current_week_start() + timedelta(days=7 * self.week_offset)
        week_end = week_start + timedelta(days=6)
        self._week_range_label.configure(
            text=f"{week_start.strftime('%Y-%m-%d')} - {week_end.strftime('%Y-%m-%d')}"
        )
        self._render_week_tiles(self._calendar_grid, week_start)

    def _build_week_skeleton(self, parent: ctk.CTkFrame) -> None:
        parent.grid_columnconfigure(tuple(range(7)), weight=1)
        parent.grid_rowconfigure(1, weight=1)

        self._day_header_labels: list[ctk.CTkLabel] = []
        self._day_content_frames: list[ctk.CTkScrollableFrame] = []

        for col in range(7):
            header = ctk.CTkLabel(
                parent,
                text="",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.COLOR_LIGHT,
            )
            header.grid(row=0, column=col, padx=4, pady=(6, 4), sticky="n")
            self._day_header_labels.append(header)

            day_frame = ctk.CTkScrollableFrame(parent, fg_color=self.COLOR_BG)
            day_frame.grid(row=1, column=col, padx=4, pady=(0, 6), sticky="nsew")
            self._day_content_frames.append(day_frame)

    def _open_week_picker(self) -> None:
        picker = ctk.CTkToplevel(self)
        picker.title(self.t("pick_other_week"))
        picker.geometry("360x360")
        picker.configure(fg_color=self.COLOR_BG)
        picker.transient(self)
        picker.grab_set()

        ctk.CTkLabel(
            picker,
            text=self.t("pick_other_week"),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.COLOR_LIGHT,
        ).pack(pady=(12, 0))

        body = ctk.CTkFrame(picker, fg_color=self.COLOR_BG)
        body.pack(fill="both", expand=True, padx=12, pady=8)

        def on_pick(year: int, month: int, day: int) -> None:
            picked = datetime(year, month, day)
            picked_week_start = picked - timedelta(days=picked.weekday())
            current_week_start = self._current_week_start()
            diff_days = (picked_week_start.date() - current_week_start.date()).days
            self.week_offset = diff_days // 7
            picker.destroy()
            self._update_week_view()

        self._build_month_calendar(body, datetime.now(), on_pick)

    def _open_daily_note_dialog(self, subject_id: int, subject_name: str, day_iso: str) -> None:
        existing = self.db.get_daily_note(subject_id, day_iso)

        dialog = ctk.CTkToplevel(self)
        dialog.title(self.t("daily_note_title"))
        dialog.geometry("520x420")
        dialog.configure(fg_color=self.COLOR_BG)
        dialog.transient(self)
        dialog.grab_set()

        header = ctk.CTkLabel(
            dialog,
            text=self.t("daily_note_for").format(subject=subject_name, date=day_iso),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.COLOR_LIGHT,
            wraplength=480,
            justify="left",
        )
        header.pack(anchor="w", padx=16, pady=(14, 8))

        textbox = ctk.CTkTextbox(
            dialog,
            fg_color=self.COLOR_LIGHT,
            text_color=self.COLOR_BG,
            corner_radius=self.RADIUS_BUTTON,
        )
        textbox.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        if existing:
            textbox.insert("1.0", existing)

        button_row = ctk.CTkFrame(dialog, fg_color=self.COLOR_BG)
        button_row.pack(fill="x", padx=16, pady=(0, 14))

        def _save() -> None:
            content = textbox.get("1.0", "end").rstrip("\n")
            self.db.set_daily_note(subject_id, day_iso, content)
            dialog.destroy()
            try:
                self._update_week_view()
            except Exception:
                pass

        ctk.CTkButton(
            button_row,
            text=self.t("close"),
            command=dialog.destroy,
            fg_color=self.COLOR_SOFT,
            text_color=self.COLOR_BG,
            hover_color=self.HOVER_DIM,
        ).pack(side="left")
        ctk.CTkButton(
            button_row,
            text=self.t("save_note"),
            command=_save,
            fg_color=self.COLOR_ACCENT,
            hover_color=self.HOVER_ACCENT,
        ).pack(side="right")

        textbox.focus_set()

    def _subject_active_on(self, row: object, day: datetime) -> bool:
        try:
            start_raw = str(row["subject_start_date"] or "").strip()
            end_raw = str(row["subject_end_date"] or "").strip()
        except (KeyError, IndexError, TypeError):
            return True
        day_only = day.date()
        if start_raw:
            try:
                if datetime.strptime(start_raw, "%Y-%m-%d").date() > day_only:
                    return False
            except ValueError:
                pass
        if end_raw:
            try:
                if datetime.strptime(end_raw, "%Y-%m-%d").date() < day_only:
                    return False
            except ValueError:
                pass
        return True

    def _render_week_tiles(self, parent: ctk.CTkFrame, week_start: datetime) -> None:
        week_days = [week_start + timedelta(days=i) for i in range(7)]
        recurring = self.db.list_recurring_classes()
        one_time_events = self.db.list_upcoming_events()

        if not getattr(self, "_day_content_frames", None):
            self._build_week_skeleton(parent)

        for col, day in enumerate(week_days):
            day_header = f"{self._weekday_abbr(day.weekday())}\n{day.strftime('%m-%d')}"
            self._day_header_labels[col].configure(text=day_header)
            day_frame = self._day_content_frames[col]
            for child in day_frame.winfo_children():
                child.destroy()

            day_items = [
                r for r in recurring
                if int(r["weekday"]) == day.weekday()
                and self._subject_active_on(r, day)
            ]
            day_items.sort(key=lambda r: r["start_time"])
            day_key = day.strftime("%Y-%m-%d")
            day_events = []
            for event in one_time_events:
                event_date_raw = str(event["event_date"])
                event_day = event_date_raw[:10]
                if event_day == day_key:
                    day_events.append(event)
            day_events.sort(key=lambda e: str(e["event_date"]))
            if not day_items and not day_events:
                ctk.CTkLabel(day_frame, text="-", text_color=self.COLOR_SOFT).pack(pady=8)
                continue

            for item in day_items:
                duration_min = int(item["duration_minutes"])
                tile_height = max(40, int(duration_min * 0.9))
                tile = ctk.CTkFrame(day_frame, fg_color=self.COLOR_ACCENT, height=tile_height, corner_radius=self.RADIUS_TILE)
                tile.pack(fill="x", padx=4, pady=5)
                tile.pack_propagate(False)

                duration_h = round(duration_min / 60, 2)
                title_label = ctk.CTkLabel(
                    tile,
                    text=f"{item['subject_name']}",
                    font=ctk.CTkFont(size=13, weight="bold"),
                )
                title_label.pack(anchor="w", padx=8, pady=(6, 2))
                time_label = ctk.CTkLabel(
                    tile,
                    text=f"{item['start_time']} | {duration_h}h",
                    font=ctk.CTkFont(size=11),
                )
                time_label.pack(anchor="w", padx=8, pady=(0, 6))

                subject_id = int(item["subject_id"])
                subject_name = str(item["subject_name"])
                day_iso = day.strftime("%Y-%m-%d")

                def _open(_event=None, sid=subject_id, sname=subject_name, diso=day_iso):
                    self._open_daily_note_dialog(sid, sname, diso)

                bound_widgets = [tile, title_label, time_label]

                if self.db.has_daily_note(subject_id, day_iso):
                    note_icon = ctk.CTkLabel(
                        tile,
                        text="\U0001F4D3",
                        font=ctk.CTkFont(size=14),
                        fg_color="transparent",
                        text_color=self.COLOR_LIGHT,
                    )
                    note_icon.place(relx=1.0, y=4, x=-6, anchor="ne")
                    bound_widgets.append(note_icon)

                for widget in bound_widgets:
                    widget.bind("<Button-1>", _open)
                    try:
                        widget.configure(cursor="hand2")
                    except Exception:
                        pass

            for event in day_events:
                event_type = str(event["event_type"]).strip().lower()
                if event_type not in {"exam", "colloquium", "kolokwium"}:
                    continue
                subject_name_raw = ""
                try:
                    subject_name_raw = str(event["subject_name"] or "").strip()
                except (KeyError, IndexError, TypeError):
                    subject_name_raw = ""
                tile_height = 86 if subject_name_raw else 64
                event_tile = ctk.CTkFrame(day_frame, fg_color=self.COLOR_DECREMENT, height=tile_height, corner_radius=self.RADIUS_TILE)
                event_tile.pack(fill="x", padx=4, pady=5)
                event_tile.pack_propagate(False)
                event_time = str(event["event_date"])[11:16] if len(str(event["event_date"])) >= 16 else "--:--"
                main_font = ctk.CTkFont(size=12, weight="bold")
                if subject_name_raw:
                    ctk.CTkLabel(
                        event_tile,
                        text=subject_name_raw,
                        font=main_font,
                        text_color=self.COLOR_LIGHT,
                        anchor="w",
                    ).pack(anchor="w", padx=8, pady=(6, 1))
                ctk.CTkLabel(
                    event_tile,
                    text=str(event["title"]),
                    font=main_font,
                    text_color=self.COLOR_LIGHT,
                    anchor="w",
                ).pack(anchor="w", padx=8, pady=(0, 1))
                ctk.CTkLabel(
                    event_tile,
                    text=event_time,
                    font=ctk.CTkFont(size=10),
                    text_color=self.COLOR_LIGHT,
                    anchor="w",
                ).pack(anchor="w", padx=8, pady=(0, 6))

    def _weekday_abbr(self, idx: int) -> str:
        if self.language == "pl":
            names = ["Pon", "Wt", "Sr", "Czw", "Pt", "Sob", "Ndz"]
        else:
            names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return names[idx % 7]

    def toggle_language(self) -> None:
        self.language = "en" if self.language == "pl" else "pl"
        self.db.set_setting("language", self.language)
        self.title(self.t("app_title"))
        self.lang_button.configure(text=self._language_toggle_label())
        self._refresh_top_bar_event()

        for key, page in self.nav_config:
            self.nav_buttons[page].configure(text=self.t(key))
        self._refresh_sidebar_countdown()
        self._invalidate_dashboard()
        self.show_page("dashboard")

    def check_notifications(self) -> None:
        now = datetime.now()
        for event in self.db.list_events_for_notifications():
            event_dt = self._parse_event_datetime(str(event["event_date"]))
            if event_dt is None:
                continue
            delta_hours = (event_dt - now).total_seconds() / 3600
            if 0 <= delta_hours <= 24 and event["event_type"].lower() == "exam":
                title = "Student Planner"
                subject = event["subject_name"] or "-"
                msg = f"Exam soon: {event['title']} ({subject}) on {event['event_date']}"
                self._send_system_notification(title, msg)
                self.db.mark_event_notified(int(event["id"]))

        self.after(120000, self.check_notifications)

    def _send_system_notification(self, title: str, message: str) -> None:
        # Avoid importing plyer in the main process on macOS builds where it crashes.
        plyer_script = (
            "from plyer import notification; "
            "notification.notify("
            f"title={title!r}, message={message!r}, app_name='Student Planner', timeout=10)"
        )
        try:
            result = subprocess.run(
                [sys.executable, "-c", plyer_script],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return
        except Exception:
            pass

        if platform.system() == "Darwin":
            safe_title = title.replace('"', "'")
            safe_message = message.replace('"', "'")
            apple_script = f'display notification "{safe_message}" with title "{safe_title}"'
            try:
                subprocess.run(["osascript", "-e", apple_script], check=False, timeout=5)
            except Exception:
                pass

    def on_close(self) -> None:
        if self.countdown_job is not None:
            try:
                self.after_cancel(self.countdown_job)
            except Exception:
                pass
            self.countdown_job = None
        self.db.close()
        self.destroy()
