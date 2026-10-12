from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from KivyWidgets.calendarWidget import CalendarWidget

class StartCalendar(Screen):
    repo = ObjectProperty(None)
    app = ObjectProperty(None)

    def on_pre_enter(self):
        for child in self.walk(restrict=True):
            if isinstance(child, CalendarWidget):
                child.refresh_calendar()
                return
