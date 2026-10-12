from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from Widgets.progressBar import ProgressBar, ProgressBarStyle
from KivyWidgets.kivyProgressBarBackend import KivyProgressBarBackend
from Models.SubjectData import SubjectData


class PointControlRow(BoxLayout):
    label_text = StringProperty("")
    value_text = StringProperty("0")

    action_minus = ObjectProperty(None)
    action_plus = ObjectProperty(None)

    def on_minus(self):
        if self.action_minus:
            self.action_minus()

    def on_plus(self):
        if self.action_plus:
            self.action_plus()


class ProgressCard(BoxLayout):
    title_text = StringProperty("")
    points_text = StringProperty("")
    subject_id = NumericProperty(0)
    pluses_val = NumericProperty(0)
    exam_val = NumericProperty(0)
    max_points = NumericProperty(100)
    repo = ObjectProperty(None, allownone=True)
    app = ObjectProperty(None, allownone=True)

    @classmethod
    def from_subject_data(cls, subject: SubjectData, repo, app):
        max_activity = int(subject.max_pluses or 0)
        max_colloquium = int(subject.max_colloquium_pluses or 0)
        max_points = max_activity + max_colloquium
        if max_points <= 0:
            max_points = 100

        if subject.teacher:
            title = f"{subject.title} ({subject.teacher})"
        else:
            title = subject.title

        return cls(
            subject_id=subject.id,
            title_text=title,
            pluses_val=int(subject.current_pluses),
            exam_val=int(subject.current_colloquium_pluses),
            max_points=max_points,
            repo=repo,
            app=app,
        )

    def on_kv_post(self, base_widget):
        self._setup_progress_bar()
        if self.app:
            self.app.bind(language=self.on_language_change)
        self.update_texts()

    def _setup_progress_bar(self):
        if not self.app:
            return

        style = ProgressBarStyle.with_theme_gradient(self.app.theme, inverted=True)
        self.pb = ProgressBar(
            self.get_total(),
            int(self.max_points),
            KivyProgressBarBackend(),
            style,
        )
        self.ids.progress_container.add_widget(self.pb.render())

    def on_language_change(self, instance, lang):
        self.update_texts()

    def get_total(self):
        return self.pluses_val + self.exam_val

    def save_to_db(self):
        self.repo.update_subject_progress(
            self.subject_id,
            int(self.pluses_val),
            int(self.exam_val),
        )

    def change_pluses(self, amount):
        new_val = self.pluses_val + amount
        if new_val >= 0:
            self.pluses_val = new_val
            self.save_to_db()
            self.update_ui()

    def change_exam(self, amount):
        new_val = self.exam_val + amount
        if new_val >= 0:
            self.exam_val = new_val
            self.save_to_db()
            self.update_ui()

    def update_ui(self):
        self.pb.updateValue(self.get_total())
        self.update_texts()

    def update_texts(self):
        if not self.app:
            return

        total = self.get_total()
        capped_total = min(total, self.max_points)
        percentage = round((capped_total / self.max_points) * 100, 1) if self.max_points > 0 else 0.0

        template = self.app.translate("scored_points", self.app.language)
        if not template:
            template = "Zdobyto {total} z {max} punktów ({percent}%)"

        self.points_text = template.format(
            total=total,
            max=self.max_points,
            percent=percentage,
        )


class TrackerProgresuScreen(Screen):
    repo = ObjectProperty(None)
    app = ObjectProperty(None)

    def on_pre_enter(self, *args):
        self.load_cards()

    def load_cards(self):
        self.ids.cards_container.clear_widgets()

        try:
            self.repo.ensure_progress_defaults()

            for row in self.repo.get_all_subjects():
                subject = SubjectData.create_from_db_dict(row)
                card = ProgressCard.from_subject_data(subject, self.repo, self.app)
                self.ids.cards_container.add_widget(card)
        except Exception as e:
            print(f"Błąd przy wyświetlaniu trackera: {e}")
