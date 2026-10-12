from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.utils import get_color_from_hex

from Widgets.progressBar import ProgressBar, ProgressBarStyle
from KivyWidgets.kivyProgressBarBackend import KivyProgressBarBackend
from models.subject_data import SubjectData

class SubjectCard(BoxLayout):
    title = StringProperty('')
    teacher = StringProperty('')
    status = StringProperty('')
    rules = StringProperty('')
    absences = StringProperty('')
    current_absences = NumericProperty(0)
    max_absences_count = NumericProperty(1)
    app = ObjectProperty(None, allownone=True)

    @classmethod
    def from_subject_data(cls, subject: SubjectData, app):
        return cls(
            title=subject.title,
            teacher=subject.teacher or 'Brak',
            status=subject.status,
            absences=f"{subject.absences} / {subject.max_absences}",
            rules=subject.conditions or '',
            current_absences=subject.absences,
            max_absences_count=subject.max_absences,
            app=app,
        )

    def on_kv_post(self, base_widget):
        self._setup_progress_bar()

    def _progress_bar_style(self):
        return ProgressBarStyle.with_theme_gradient(self.app.theme)

    def _setup_progress_bar(self):
        if not self.app:
            return

        maximum = self.max_absences_count if self.max_absences_count > 0 else 1
        progress = ProgressBar(
            int(self.current_absences),
            maximum,
            KivyProgressBarBackend(),
            self._progress_bar_style(),
        )
        self.ids.progress_container.add_widget(progress.render())

    def get_status_bg_rgba(self):
        colors = self.app.theme.SubjectColors
        status_colors = {
            'completed': colors.SUBJECT_BG_COLOR_COMPLETED,
            'inprogress': colors.SUBJECT_BG_COLOR_INPROGRESS,
            'atrisk': colors.SUBJECT_BG_COLOR_ATRISK,
            'failed': colors.SUBJECT_BG_COLOR_FAILED,
        }
        return get_color_from_hex(status_colors.get(self.status, colors.SUBJECT_BG_COLOR_FAILED))

    def get_status_text_rgba(self):
        colors = self.app.theme.SubjectColors
        hex_color = (
            colors.SUBJECT_TEXT_COLOR_BRIGHT
            if self.status == 'failed'
            else colors.SUBJECT_TEXT_COLOR_DARK
        )
        return get_color_from_hex(hex_color)

class RulesRepositoryScreen(Screen):
    repo = ObjectProperty(None)
    app = ObjectProperty(None)

    def on_pre_enter(self):
        self.populate_cards()

    def populate_cards(self):
        self.ids.rules_container.clear_widgets()

        try:
            for row in self.repo.get_all_subjects():
                subject = SubjectData.create_from_db_dict(row)
                card = SubjectCard.from_subject_data(subject, self.app)
                self.ids.rules_container.add_widget(card)
        except Exception as e:
            print(f"Błąd przy wyświetlaniu: {e}")
