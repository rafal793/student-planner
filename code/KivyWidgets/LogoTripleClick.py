from kivy.app import App
from kivy.clock import Clock
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image

CLICK_RESET_SECONDS = 0.6
CLICKS_TO_CYCLE = 3


class LogoTripleClick(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._click_count = 0
        self._reset_event = None
        self._theme_bound = False

    def on_parent(self, widget, parent):
        if parent is None or self._theme_bound:
            return
        app = App.get_running_app()
        if app is None:
            return
        app.theme.UiColors.bind(LOGO_SOURCE=self._on_logo_source)
        self._on_logo_source(app.theme.UiColors, app.theme.UiColors.LOGO_SOURCE)
        self._theme_bound = True

    def _on_logo_source(self, _instance, value):
        if value:
            self.source = value

    def on_release(self):
        if self._reset_event is not None:
            self._reset_event.cancel()

        self._click_count += 1
        if self._click_count >= CLICKS_TO_CYCLE:
            self._click_count = 0
            app = App.get_running_app()
            if app is not None and hasattr(app, 'cycle_theme'):
                app.cycle_theme()
            return

        self._reset_event = Clock.schedule_once(self._reset_clicks, CLICK_RESET_SECONDS)

    def _reset_clicks(self, _dt):
        self._click_count = 0
        self._reset_event = None
