from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.app import App
from kivy.metrics import dp
from Widgets.notificationMessages import build_notification_messages

class NotificationPopup(Popup):
    def on_open(self):
        self.ids.notifications_container.clear_widgets()

        app = App.get_running_app()
        translate = lambda key: app.translations[app.language].get(key, key)
        messages = build_notification_messages(
            app.repo.get_all_subjects() or [],
            app.repo.get_upcoming_events() or [],
            translate,
        )

        if not messages:
            empty_label = Label(
                text=translate('no_notifications'),
                size_hint_y=None,
                height=dp(40),
            )
            self.ids.notifications_container.add_widget(empty_label)
            return

        for message in messages:
            item_label = Label(
                text=message,
                size_hint_y=None,
                height=dp(40),
                halign='left',
                valign='middle',
            )
            item_label.bind(size=item_label.setter('text_size'))
            self.ids.notifications_container.add_widget(item_label)
