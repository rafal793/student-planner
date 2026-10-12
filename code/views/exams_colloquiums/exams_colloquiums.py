import re
from datetime import date
from kivy.factory import Factory
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.utils import get_color_from_hex
from KivyWidgets.KivyButtonBackend import CustomToggleButtonWidget
from KivyWidgets.kivyDatePickerBackend import KivyDatePickerBackend
from Widgets.datePicker import DatePicker, DatePickerStyle

class ExamSubjectButton(CustomToggleButtonWidget):
    pass

class ExamsAndColloquiumsScreen(Screen):
    repo = ObjectProperty(None)
    app = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_subject_btn = None
        self.selected_subject_id = None

    def on_pre_enter(self, *args):
        self.load_subjects()
        self.load_events()

    def load_subjects(self, dt=None):
        grid = self.ids.subjects_grid
        grid.clear_widgets()

        for subject_record in self.repo.get_all_subjects():
            subject_id = subject_record["id"]
            subject_name = subject_record["name"]
            teacher_name = subject_record["teacher"] or ""

            btn = ExamSubjectButton()
            btn.text = f"{subject_name}\n[size=12sp]{teacher_name}[/size]"
            btn.group = "exam_subjects"
            btn.bind(
                state=lambda instance, value, s_id=subject_id: self._on_subject_state(
                    instance, value, s_id
                )
            )
            grid.add_widget(btn)

    def _on_subject_state(self, instance, value, subject_id):
        if value == "down":
            self.selected_subject_btn = instance
            self.selected_subject_id = subject_id
            self.load_events()
        elif self.selected_subject_btn is instance:
            self.selected_subject_btn = None
            self.selected_subject_id = None

    def load_events(self, dt=None):
        container = self.ids.events_container
        container.clear_widgets()

        try:
            events_list = list(self.repo.get_all_events())
            sorted_events = sorted(
                events_list, 
                key=lambda x: str(x["date_time"]), 
                reverse=True
            )

            for event_record in sorted_events:
                card = Factory.EventCard()
                card.date_text = str(event_record["date_time"])
                card.title_text = str(event_record["title"])
                card.subject_text = str(event_record["subject_name"])

                event_id = event_record["id"]
                event_title = str(event_record["title"])

                card.ids.btn_delete.bind(
                    on_release=lambda instance, e_id=event_id, e_title=event_title: self.show_delete_popup(
                        e_id, e_title
                    )
                )
                container.add_widget(card)
        except Exception as e:
            print(f"CRITICAL ERROR (load_events): {e}")

    def submit_event(self):
        if not self.selected_subject_id:
            self.show_error_popup(self.app.translate("err_select_subject", self.app.language))
            return

        event_title = self.ids.input_event_title.text.strip()
        event_date = self.ids.input_event_date.text.strip()
        event_time = self.ids.input_event_time.text.strip()
        event_type = self.ids.input_event_type.text

        if event_type == self.app.translate("type_placeholder", self.app.language):
            self.show_error_popup(self.app.translate("err_empty_event_type", self.app.language))
            return
        if not event_title:
            self.show_error_popup(self.app.translate("err_empty_event_title", self.app.language))
            return
        if not re.match(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$", event_date):
            self.show_error_popup(self.app.translate("err_invalid_date_format", self.app.language))
            return
        if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", event_time):
            self.show_error_popup(self.app.translate("err_invalid_time_format", self.app.language))
            return

        full_event_start = f"{event_date} {event_time}"

        self.repo.add_event(
            self.selected_subject_id,
            event_type,
            event_title,
            full_event_start,
        )

        self.load_events()
        self.ids.input_event_title.text = ""
        self.ids.input_event_date.text = ""
        self.ids.input_event_time.text = ""
        self.ids.input_event_type.text = self.app.translate("type_placeholder", self.app.language)

    def show_error_popup(self, error_message):
        content = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(20))
        label = Label(text=error_message, halign="center", valign="middle")
        label.bind(size=label.setter("text_size"))
        content.add_widget(label)

        btn_ok = Factory.StandardUiButton()
        btn_ok.text = self.app.translate("btn_will_fix", self.app.language)
        btn_ok.size_hint = (None, None)
        btn_ok.size = (dp(160), dp(40))

        btn_row = AnchorLayout(anchor_x="center", size_hint_y=None, height=dp(40))
        btn_row.add_widget(btn_ok)
        content.add_widget(btn_row)

        popup = Popup(
            title=self.app.translate("popup_error_input_title", self.app.language),
            content=content,
            size_hint=(None, None),
            size=(dp(400), dp(200)),
            auto_dismiss=True,
        )
        btn_ok.bind(on_release=popup.dismiss)
        popup.open()

    def show_delete_popup(self, event_id, event_title):
        try:
            content = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(20))

            safe_title = event_title.replace("[", "").replace("]", "")
            base_msg = self.app.translate("popup_delete_msg", self.app.language)
            message = Label(text=base_msg.format(safe_title), markup=True, halign="center")
            content.add_widget(message)

            buttons = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(40))
            btn_cancel = Factory.StandardUiButton()
            btn_cancel.text = self.app.translate("btn_cancel", self.app.language)
            btn_confirm = Factory.ExamDangerButton()
            btn_confirm.text = self.app.translate("btn_delete", self.app.language)

            buttons.add_widget(btn_cancel)
            buttons.add_widget(btn_confirm)
            content.add_widget(buttons)

            popup = Popup(
                title=self.app.translate("popup_delete_title", self.app.language),
                content=content,
                size_hint=(None, None),
                size=(dp(400), dp(200)),
                auto_dismiss=False,
            )

            btn_cancel.bind(on_release=popup.dismiss)
            btn_confirm.bind(on_release=lambda instance: self.delete_event(event_id, popup))
            popup.open()
        except Exception as e:
            print(f"CRITICAL ERROR (show_delete_popup): {e}")

    def delete_event(self, event_id, popup):
        try:
            self.repo.remove_event(event_id)
            popup.dismiss()
            self.load_events()
        except Exception as e:
            popup.dismiss()
            error_prefix = self.app.translate("err_db_delete", self.app.language)
            self.show_error_popup(f"{error_prefix}{str(e)}")

    def open_calendar(self):
        widget_colors = self.app.theme.WidgetColors
        ui_colors = self.app.theme.UiColors

        dp_style = DatePickerStyle(
            bg_color=get_color_from_hex(widget_colors.FORM_TEXTINPUT_BG_COLOR),
            selected_color=get_color_from_hex(ui_colors.SECONDARY_BG_COLOR),
            today_color=get_color_from_hex(widget_colors.SCROLLBAR_COLOR_ACTIVE),
            text_color=get_color_from_hex(widget_colors.FORM_TEXTINPUT_TEXT_COLOR),
        )
        backend = KivyDatePickerBackend()
        picker = DatePicker(selected_date=date.today(), backend=backend, style=dp_style)
        picker_ui = picker.render()

        popup = Popup(
            title=self.app.translate("popup_choose_exam_date", self.app.language),
            content=picker_ui,
            size_hint=(None, None),
            size=(dp(400), dp(450)),
        )

        def on_confirm(instance):
            self.ids.input_event_date.text = str(backend.selected_date)
            popup.dismiss()

        backend.confirm_button.bind(on_release=on_confirm)
        popup.open()
