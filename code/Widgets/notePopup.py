from abc import ABC, abstractmethod

from kivy.app import App


class NotePopupBackend(ABC):
    @abstractmethod
    def create(
        self,
        title_text: str,
        existing_text: str,
        on_save_callback,
        on_cancel_callback,
        save_label: str,
        cancel_label: str,
    ):
        pass

    @abstractmethod
    def open_popup(self):
        pass

    @abstractmethod
    def close_popup(self):
        pass


class NotePopup:
    def __init__(
        self,
        subject_id: str,
        subject_name: str,
        note_date: str,
        backend: NotePopupBackend,
        existing_text: str = "",
        on_save=None,
    ):
        self.subject_id = subject_id
        self.subject_name = subject_name
        self.note_date = note_date
        self._backend = backend
        self.existing_text = existing_text
        self.on_save = on_save

    def open(self):
        app = App.get_running_app()
        lang = getattr(app, "language", "pl")
        translations = getattr(app, "translations", {}).get(lang, {})

        title_template = translations.get(
            "popup_class_note_title",
            "Class note: {subject} ({date})",
        )
        title_text = title_template.format(
            subject=self.subject_name,
            date=self.note_date,
        )
        save_label = translations.get("btn_save_note", "Save note")
        cancel_label = translations.get("btn_close", "Close")

        self._backend.create(
            title_text=title_text,
            existing_text=self.existing_text,
            on_save_callback=self._handle_save,
            on_cancel_callback=self._handle_cancel,
            save_label=save_label,
            cancel_label=cancel_label,
        )
        self._backend.open_popup()

    def _handle_save(self, text_content: str):
        if self.on_save:
            self.on_save(self.subject_id, self.note_date, text_content)
        self._backend.close_popup()

    def _handle_cancel(self):
        self._backend.close_popup()
