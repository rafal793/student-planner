from datetime import datetime
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup
from kivy.app import App
from Widgets.countdown import CountdownWidget, CountdownStyle, KivyCountdownBackend
from Widgets.datePicker import DatePicker, DatePickerStyle
from KivyWidgets.kivyDatePickerBackend import KivyDatePickerBackend

class SessionPanel(ButtonBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.countdown = None
        self.rendered_countdown = None
        Clock.schedule_once(self.add_timer, 0.1)

    def add_timer(self, dt):
        self.countdown = CountdownWidget(
            target_date=datetime(2026, 6, 22, 0, 0),
            backend=KivyCountdownBackend(),
            style=CountdownStyle(
                bg_color=(0, 0, 0, 0), 
                text_color=(1, 1, 1, 1)
            )
        )
        self.rendered_countdown = self.countdown.render()
        self.add_widget(self.rendered_countdown)
    
    def on_release(self):
        self.open_date_picker()

    def open_date_picker(self):
        app = App.get_running_app()
        lang = app.language
        backend = KivyDatePickerBackend()
        dp_style = DatePickerStyle(
            bg_color=(1, 1, 1, 1),
            selected_color=(45/255, 88/255, 140/255, 1),
            today_color=(0.8, 0.8, 0.8, 1),
            text_color=(1, 1, 1, 1)
        )
        
        picker = DatePicker(
            selected_date=datetime.now().date(),
            backend=backend,
            style=dp_style
        )
        picker_ui = picker.render()
        
        popup = Popup(
            title=app.translations[lang].get("calendar_title", "Wybierz datę sesji"),
            content=picker_ui,
            size_hint=(None, None),
            size=(400, 450)
        )

        def on_confirm(instance):
            chosen_date = backend.selected_date

            if self.rendered_countdown:
                self.remove_widget(self.rendered_countdown)
            
            self.countdown = CountdownWidget(
                target_date=datetime.combine(chosen_date, datetime.min.time()),
                backend=KivyCountdownBackend(),
                style=CountdownStyle(
                    bg_color=(0, 0, 0, 0), 
                    text_color=(1, 1, 1, 1)
                )
            )
            
            self.rendered_countdown = self.countdown.render()
            self.add_widget(self.rendered_countdown)
            
            popup.dismiss()

        backend.confirm_button.bind(on_release=on_confirm)
        popup.open()