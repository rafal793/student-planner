from abc import ABC, abstractmethod
from enum import Enum, auto
from datetime import datetime

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label




class CountdownState(Enum):
    RUNNING = auto()
    COMPLETED = auto()
    STOPPED = auto()


class CountdownStyle:

    def __init__(self, bg_color, text_color):
        self.bg_color = bg_color
        self.text_color = text_color




class CountdownBackend(ABC):

    @abstractmethod
    def create(self, style: CountdownStyle):
        pass

    @abstractmethod
    def setTime(self, text: str):
        pass




class KivyCountdownBackend(CountdownBackend):

    def __init__(self):

        self.layout = None
        self.label = None

    def create(self, style: CountdownStyle):

        self.layout = BoxLayout(
            orientation="vertical",
            padding=0,
            spacing=0
        )

        self.label = Label(
            text="",
            color=style.text_color,
            bold=True,
            font_size='14sp'
        )

        self.layout.add_widget(self.label)

        return self.layout

    def setTime(self, text: str):

        self.label.text = text


class CountdownWidget:

    def __init__(
        self,
        target_date: datetime,
        backend: CountdownBackend,
        style: CountdownStyle
    ):

        self.target_date = target_date
        self._backend = backend
        self.style = style

        self._state = CountdownState.RUNNING

        self._event = None

    def render(self):

        widget = self._backend.create(self.style)

        # natychmiast pokazuje aktualny czas
        self._update_time()
        
        self._event = Clock.schedule_interval(self._tick, 1)

        return widget

    def stop(self):

        self._state = CountdownState.STOPPED

        if self._event:
            self._event.cancel()

    def _tick(self, dt):

        if self._state != CountdownState.RUNNING:
            return

        self._update_time()

    def _update_time(self):

        now = datetime.now()

        remaining = self.target_date - now

        total_seconds = int(remaining.total_seconds())

        if total_seconds <= 0:

            self._state = CountdownState.COMPLETED

            self._backend.setTime("00d 00h 00m 00s")

            if self._event:
                self._event.cancel()

            return

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        time_text = (
            f"{days:02}d "
            f"{hours:02}h "
            f"{minutes:02}m "
            f"{seconds:02}s"
        )

        
        self._backend.setTime(time_text)
