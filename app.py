import json
import Widgets.notifications

# Importy używane tylko w plikach .kv — PyInstaller musi je widzieć przy budowaniu exe.
import KivyWidgets.LogoTripleClick  # noqa: F401
import KivyWidgets.SessionPanel  # noqa: F401

from Database.database_sqllite import SqliteAppRepository
from Style.Colors import ThemeManager
from paths import resource_path, configure_kivy_resources


from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'minimum_width', '600')
Config.set('graphics', 'minimum_height', '600')

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty , ObjectProperty

from datetime import datetime
from Widgets.countdown import CountdownWidget, CountdownStyle, KivyCountdownBackend

from tests.create_default_values import DatabaseStarter

from screenHandler import *

class StudentPlannerApp(App):

    language = StringProperty("pl")
    theme = ObjectProperty(ThemeManager.with_palette('default'))
    def __init__(self, repository, **kwargs):
        super().__init__(**kwargs)
        self.repo = repository

    def build(self):
        configure_kivy_resources()

        self.screens = SCREENS # wczytanie screenow z screenHandler

        with open(resource_path('translation.json'), 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        self.translations = data
        
        Builder.load_file(resource_path('Style/universalWidgets.kv'))
        Builder.load_file(resource_path('views/Kalendarz/calendar.kv'))

        root_widget = Builder.load_file(resource_path('views/main.kv'))

        self.sesja_countdown = CountdownWidget(
            target_date=datetime(2026, 6, 22, 0, 0),
            backend=KivyCountdownBackend(),
            style=CountdownStyle(bg_color=(0, 0, 0, 0), text_color=(1, 1, 1, 1))
        )

        self.sm = root_widget.ids.sm
        self.change_screen(target_screen='calendar')
        return root_widget


    def translate(self, text:str, langtrigger ):
                return self.translations[self.language].get(text)

    def change_screen(self, target_screen , **kwargs):
        if not self.sm.has_screen(target_screen):
            
            
            
            config = self.screens.get(target_screen)
            
            if config:
                
                Builder.load_file(resource_path(config['kv']))
                screen_kwargs = {
                    'name': target_screen,
                    'repo': self.repo,
                    'app': self,
                }
                new_screen = config['class'](**screen_kwargs)
                self.sm.add_widget(new_screen)
            else:
                print(f"Error invaild scren name {target_screen}")
                return
            
        new_screen = self.sm.get_screen(target_screen)

        for klucz, wartosc in kwargs.items():
            setattr(new_screen, klucz, wartosc)

        self.sm.current = target_screen

    def change_language(self):
        if self.language == "pl":
            self.language = "en"
        else:
            self.language = "pl"

        print("Zmieniono język na:", self.language)

    def cycle_theme(self):
        palettes = ThemeManager.available_palettes()
        idx = palettes.index(self.theme.palette_name)
        self.theme.apply_palette(palettes[(idx + 1) % len(palettes)])
        self._refresh_theme_dependent_widgets()

    def _refresh_theme_dependent_widgets(self):
        if not hasattr(self, 'sm'):
            return

        from KivyWidgets.calendarWidget import CalendarWidget

        current = self.sm.current
        for screen in self.sm.screens:
            for child in screen.walk(restrict=True):
                if isinstance(child, CalendarWidget):
                    child.refresh_calendar(reload_data=False)

            if screen.name != current:
                continue
            if hasattr(screen, 'load_cards'):
                screen.load_cards()
            elif hasattr(screen, 'populate_cards'):
                screen.populate_cards()

    def events(self)->str:
        events_list = self.repo.get_upcoming_events() or []
    
        self._events = events_list
        if not events_list:
            return self.translate("no_events", self.language)
        else:
            sorted_events = sorted(events_list, key=lambda e: e.get('date_time', ''))
            return sorted_events[0].get('title', '')+ " " + sorted_events[0].get('date_time', '') + " " + self.translate(sorted_events[0].get('type', ''),self.language)


if __name__ == "__main__":

    configure_kivy_resources()

    # inicjalizacja bazy
    repo = SqliteAppRepository(db_connection=None)
    repo.init_db()

    # automatyczne zasilenie bazy / odświeżenie dat demo względem dziś
    DS = DatabaseStarter(repo)
    if not repo.get_all_subjects():
        DS.add_test_subjects()
    else:
        DS.refresh_demo_dates()

    StudentPlannerApp(repository=repo).run()
