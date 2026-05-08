"""User-facing translations.

Keys are kept in sync with ``self.t(...)`` lookups in ``ui.py``. When adding
new UI text always add an entry for both languages so that switching the
language never silently falls back to the raw key.
"""

TEXTS = {
    "pl": {
        # Sidebar / navigation / titles
        "app_title": "Student Planner",
        "dashboard": "Start / Kalendarz",
        "add_subject": "Dodaj przedmiot",
        "schedule_exams": "Egzaminy i kolokwia",
        "rules": "Repozytorium zasad",
        "progress": "Tracker progresu",
        "my_subjects": "Moje przedmioty",
        "subject_tiles": "Przedmioty",
        "upcoming_events": "Nadchodzące wydarzenia",
        "subject_details": "Szczegóły przedmiotu",
        "general_note": "Notatka ogólna",

        # Calendar navigation
        "next_week": "Następny tydzień",
        "prev_week": "Poprzedni tydzień",
        "today_week": "Wracaj do bieżącego tygodnia",
        "pick_other_week": "Wybierz inny tydzień",

        # Forms
        "subject": "Przedmiot",
        "teacher": "Prowadzący",
        "grading_rules": "Warunki zaliczenia",
        "max_absences": "Dopuszczalne nieobecności",
        "save_subject": "Zapisz przedmiot",
        "selected_subject": "Wybrany przedmiot",
        "absence_count": "Liczba nieobecności",
        "absences_section": "Nieobecności",
        "current_status": "Aktualny status",
        "edit_subject": "Edytuj przedmiot",
        "save_changes": "Zapisz zmiany",
        "back": "Wróć",
        "increase": "+",
        "decrease": "-",

        # Add subject extras
        "class_days": "Dni zajęć (możesz zaznaczyć wiele)",
        "start_time": "Godzina startu (HH:MM)",
        "duration_hours": "Czas trwania (godziny)",
        "select_day": "Wybierz przynajmniej jeden dzień zajęć.",
        "max_activity_points": "Max liczba plusów",
        "max_colloquium_points": "Max punktów za kolokwia",
        "subject_start_date": "Początek zajęć (YYYY-MM-DD)",
        "subject_end_date": "Koniec zajęć (YYYY-MM-DD)",
        "invalid_subject_dates":
            "Niepoprawne daty. Użyj formatu YYYY-MM-DD i upewnij się, że koniec jest po początku.",

        # Progress tracker
        "pluses": "Plusy",
        "colloquium_points": "Punkty za kolokwium",
        "progress_points_text": "Zdobyto {current} z {maximum} punktów ({percent}%)",

        # Notes
        "save_note": "Zapisz notatkę",
        "daily_note_title": "Notatka",
        "daily_note_for": "Notatka do zajęć: {subject} ({date})",

        # Events
        "event_title": "Tytuł wydarzenia",
        "event_date": "Start (YYYY-MM-DD HH:MM)",
        "confirm_add_event": "Potwierdź i dodaj",
        "saved_events": "Zapisane wydarzenia",
        "no_events": "Brak zapisanych wydarzeń.",
        "delete_event": "Usuń wydarzenie",
        "confirm_delete_event": "Na pewno usunąć to wydarzenie?",

        # Status labels
        "status_in_progress": "W trakcie",
        "status_passed": "Zaliczony",
        "status_risk": "Zagrożony",

        # Subject lifecycle
        "delete_subject": "Usuń przedmiot",
        "confirm_delete_subject": "Na pewno usunąć ten przedmiot? Operacja jest nieodwracalna.",

        # Session countdown
        "session_widget_title": "Sesja",
        "session_date": "Data sesji (YYYY-MM-DD)",
        "set_date": "Ustaw datę",
        "remaining": "Pozostało",
        "days": "dni",
        "hours": "godz",
        "minutes": "min",
        "countdown_sidebar_set": "Kliknij, aby ustawić datę",
        "countdown_session_passed": "Data minęła",
        "countdown_edit_title": "Odliczanie do sesji",

        # Date / time pickers
        "pick_date_title": "Wybierz datę",
        "pick_time_title": "Wybierz godzinę",
        "pick_datetime_title": "Wybierz datę i godzinę",
        "confirm": "Potwierdź",
        "hours_label": "Godzina",
        "minutes_label": "Minuty",

        # Misc / shared
        "saved": "Zapisano",
        "error": "Błąd",
        "required_fields": "Uzupełnij wymagane pola.",
        "invalid_date": "Niepoprawny format daty. Użyj YYYY-MM-DD.",
        "no_subjects": "Brak przedmiotów. Dodaj pierwszy przedmiot w zakładce po lewej.",
        "closest_event": "Najbliższe",
        "closest_none": "Brak nadchodzących kolokwiów/egzaminów",
        "close": "Zamknij",
    },
    "en": {
        "app_title": "Student Planner",
        "dashboard": "Home / Calendar",
        "add_subject": "Add Subject",
        "schedule_exams": "Exams & Colloquia",
        "rules": "Rules Repository",
        "progress": "Progress Tracker",
        "my_subjects": "My subjects",
        "subject_tiles": "Subjects",
        "upcoming_events": "Upcoming events",
        "subject_details": "Subject details",
        "general_note": "General Note",

        "next_week": "Next week",
        "prev_week": "Previous week",
        "today_week": "Back to current week",
        "pick_other_week": "Pick another week",

        "subject": "Subject",
        "teacher": "Teacher",
        "grading_rules": "Grading rules",
        "max_absences": "Allowed absences",
        "save_subject": "Save subject",
        "selected_subject": "Selected subject",
        "absence_count": "Absence count",
        "absences_section": "Absences",
        "current_status": "Current status",
        "edit_subject": "Edit subject",
        "save_changes": "Save changes",
        "back": "Back",
        "increase": "+",
        "decrease": "-",

        "class_days": "Class days (multi-select)",
        "start_time": "Start time (HH:MM)",
        "duration_hours": "Duration (hours)",
        "select_day": "Select at least one class day.",
        "max_activity_points": "Max pluses",
        "max_colloquium_points": "Max colloquium points",
        "subject_start_date": "Classes start (YYYY-MM-DD)",
        "subject_end_date": "Classes end (YYYY-MM-DD)",
        "invalid_subject_dates":
            "Invalid dates. Use YYYY-MM-DD and make sure the end is after the start.",

        "pluses": "Pluses",
        "colloquium_points": "Colloquium points",
        "progress_points_text": "Earned {current} of {maximum} points ({percent}%)",

        "save_note": "Save note",
        "daily_note_title": "Note",
        "daily_note_for": "Class note: {subject} ({date})",

        "event_title": "Event title",
        "event_date": "Start (YYYY-MM-DD HH:MM)",
        "confirm_add_event": "Confirm and add",
        "saved_events": "Saved events",
        "no_events": "No saved events.",
        "delete_event": "Delete event",
        "confirm_delete_event": "Are you sure you want to delete this event?",

        "status_in_progress": "In progress",
        "status_passed": "Passed",
        "status_risk": "At risk",

        "delete_subject": "Delete subject",
        "confirm_delete_subject":
            "Are you sure you want to delete this subject? This action cannot be undone.",

        "session_widget_title": "Session",
        "session_date": "Session date (YYYY-MM-DD)",
        "set_date": "Set date",
        "remaining": "Remaining",
        "days": "days",
        "hours": "hrs",
        "minutes": "min",
        "countdown_sidebar_set": "Click to set the date",
        "countdown_session_passed": "Date has passed",
        "countdown_edit_title": "Session countdown",

        "pick_date_title": "Pick a date",
        "pick_time_title": "Pick a time",
        "pick_datetime_title": "Pick date and time",
        "confirm": "Confirm",
        "hours_label": "Hour",
        "minutes_label": "Minute",

        "saved": "Saved",
        "error": "Error",
        "required_fields": "Please fill required fields.",
        "invalid_date": "Invalid date format. Use YYYY-MM-DD.",
        "no_subjects": "No subjects yet. Add your first subject from the left tab.",
        "closest_event": "Closest",
        "closest_none": "No upcoming colloquiums/exams",
        "close": "Close",
    },
}
