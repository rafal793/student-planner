from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from Widgets.notePopup import NotePopupBackend


class KivyNotePopupBackend(NotePopupBackend):
    def __init__(self):
        self.popup = None
        self.text_input = None

    def create(
        self,
        title_text,
        existing_text,
        on_save_callback,
        on_cancel_callback,
        save_label="Save note",
        cancel_label="Close",
    ):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.text_input = TextInput(
            text=existing_text,
            multiline=True,
            background_color=(0.9, 0.9, 0.9, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            font_size=16
        )
        layout.add_widget(self.text_input)

        btn_layout = BoxLayout(size_hint_y=None, height=45, spacing=15)
        btn_cancel = Button(text=cancel_label, background_color=(0.5, 0.5, 0.5, 1), bold=True)
        btn_cancel.bind(on_release=lambda x: on_cancel_callback())

        btn_save = Button(
            text=save_label,
            background_color=(45 / 255, 88 / 255, 140 / 255, 1),
            bold=True,
        )
        btn_save.bind(on_release=lambda x: on_save_callback(self.text_input.text.strip()))

        btn_layout.add_widget(btn_cancel)
        btn_layout.add_widget(btn_save)

        layout.add_widget(btn_layout)

        self.popup = Popup(
            title=title_text,
            content=layout,
            size_hint=(None, None),
            size=(450, 350),
            title_align='center'
        )

    def open_popup(self):
        if self.popup:
            self.popup.open()

    def close_popup(self):
        if self.popup:
            self.popup.dismiss()
