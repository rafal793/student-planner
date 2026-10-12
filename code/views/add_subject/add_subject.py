import os
import sys
import re
from datetime import datetime, date

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.factory import Factory
from KivyWidgets.KivyButtonBackend import CustomButtonWidget

from Widgets.datePicker import DatePicker, DatePickerStyle
from KivyWidgets.kivyDatePickerBackend import KivyDatePickerBackend

kv_path = os.path.join(parent_dir, 'kv', 'add_subject.kv')

def normalize_start_time(time_str):
    """Accept H:MM or HH:MM; return HH:MM, or None if invalid."""
    match = re.match(r'^(\d{1,2}):(\d{2})$', (time_str or '').strip())
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2))
    if hour > 23 or minute > 59:
        return None
    return f"{hour:02d}:{minute:02d}"

class AddSubjectScreen(Screen):
    repo = ObjectProperty(None)
    app = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active_date_field = None  # which date field we are editing

    def open_calendar(self, field_id):
        """Open our DatePicker (not MDDatePicker)."""
        self.active_date_field = field_id

        dp_style = DatePickerStyle(
            bg_color=(0.15, 0.15, 0.15, 1),
            selected_color=(0.2, 0.5, 0.8, 1),
            today_color=(0.8, 0.8, 0.8, 1),
            text_color=(1, 1, 1, 1)
        )
        backend = KivyDatePickerBackend()
        picker = DatePicker(
            selected_date=date.today(),
            backend=backend,
            style=dp_style
        )
        
        picker_ui = picker.render()
        
        popup = Popup(
            title=self.app.translate("popup_choose_date", self.app.language),
            content=picker_ui,
            size_hint=(None, None),
            size=(400, 450)
        )

        def on_confirm(instance):
            chosen_date = backend.selected_date
            date_str = str(chosen_date)
            
            if self.active_date_field == 'start':
                self.ids.input_start_date.text = date_str
            elif self.active_date_field == 'end':
                self.ids.input_end_date.text = date_str
            
            popup.dismiss()

        backend.confirm_button.bind(on_release=on_confirm)
        popup.open()

    def save_subject(self):
        # read form fields
        subject_name = self.ids.input_name.text.strip()
        teacher_name = self.ids.input_teacher.text.strip()
        pass_conditions = self.ids.input_conditions.text.strip()
        start_time = self.ids.input_time.text.strip()
        start_date = self.ids.input_start_date.text.strip()
        end_date = self.ids.input_end_date.text.strip()

        # validate text fields
        if not subject_name:
            self.show_error_popup(self.app.translate("err_subject_req", self.app.language))
            return
        if not teacher_name:
            self.show_error_popup(self.app.translate("err_teacher_req", self.app.language))
            return

        # validate dates
        try:
            d_start = datetime.strptime(start_date, '%Y-%m-%d')
            d_end = datetime.strptime(end_date, '%Y-%m-%d')
            if d_end < d_start:
                self.show_error_popup(self.app.translate("err_end_before_start", self.app.language))
                return
        except ValueError:
            self.show_error_popup(self.app.translate("err_invalid_dates", self.app.language))
            return

        # parse and validate numbers
        try:
            def parse_float(val):
                return float(val.strip().replace(',', '.'))

            absences_text = self.ids.input_absences.text.strip() or "0"
            try:
                absences = int(absences_text)
            except ValueError:
                self.show_error_popup(self.app.translate("err_absences_int", self.app.language))
                return

            pluses = parse_float(self.ids.input_pluses.text.strip() or "0.0")
            max_points = parse_float(self.ids.input_points.text.strip() or "0.0")
            duration_hours = parse_float(self.ids.input_duration.text.strip() or "0.0")

            if absences < 0 or pluses < 0 or max_points < 0 or duration_hours <= 0:
                self.show_error_popup(self.app.translate("err_num_positive", self.app.language))
                return

            duration_minutes = int(duration_hours * 60)
        except ValueError:
            self.show_error_popup(self.app.translate("err_num_only", self.app.language))
            return

        # validate start time
        start_time = normalize_start_time(start_time)
        if start_time is None:
            self.show_error_popup(self.app.translate("err_start_time", self.app.language))
            return

        # weekdays
        day_mapping = {self.ids.chk_mon: 0, self.ids.chk_tue: 1, self.ids.chk_wed: 2, 
                       self.ids.chk_thu: 3, self.ids.chk_fri: 4, self.ids.chk_sat: 5, self.ids.chk_sun: 6}
        selected_days = [val for chk, val in day_mapping.items() if chk.active]
        
        if not selected_days:
            self.show_error_popup(self.app.translate("err_select_day", self.app.language))
            return

        # save to database
        try:
            self.repo.add_subject_with_schedule({
                'title': subject_name,
                'teacher': teacher_name,
                'conditions': pass_conditions,
                'max_absences': absences,
                'max_pluses': pluses,
                'max_colloquium_pluses': max_points,
                'term_start': start_date,
                'term_end': end_date,
                'schedule': [
                    {
                        'day_of_week': day,
                        'start_time': start_time,
                        'duration_minutes': duration_minutes,
                    }
                    for day in selected_days
                ],
            })
            self.clear_form()
            print(f"SUKCES! Zapisano przedmiot '{subject_name}' oraz jego harmonogram do bazy danych.")
        except Exception as e:
            error_prefix = self.app.translate("err_db_save", self.app.language)
            self.show_error_popup(f"{error_prefix}{str(e)}")
    
    def clear_form(self):
        self.ids.input_name.text = ""
        self.ids.input_teacher.text = ""
        self.ids.input_conditions.text = ""
        self.ids.input_absences.text = ""
        self.ids.input_pluses.text = ""
        self.ids.input_points.text = ""
        self.ids.input_time.text = ""
        self.ids.input_duration.text = ""
        self.ids.input_start_date.text = ""
        self.ids.input_end_date.text = ""
        
        for checkbox in [self.ids.chk_mon, self.ids.chk_tue, self.ids.chk_wed, 
                         self.ids.chk_thu, self.ids.chk_fri, self.ids.chk_sat, self.ids.chk_sun]:
            checkbox.active = False

    def show_error_popup(self, error_message):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        label = Label(text=error_message, halign='center', valign='middle')
        label.bind(size=label.setter('text_size'))
        content.add_widget(label)

        btn_ok = Factory.StandardUiButton()
        btn_ok.text = self.app.translate("btn_will_fix", self.app.language)
        btn_ok.size_hint = (None, None)
        btn_ok.size = (dp(160), dp(40))

        btn_row = AnchorLayout(anchor_x='center', size_hint_y=None, height=dp(40))
        btn_row.add_widget(btn_ok)
        content.add_widget(btn_row)

        popup = Popup(
            title=self.app.translate("popup_error_form_title", self.app.language), 
            content=content, 
            size_hint=(None, None), size=(dp(400), dp(200)), 
            auto_dismiss=True
        )
        btn_ok.bind(on_release=popup.dismiss)
        popup.open()
