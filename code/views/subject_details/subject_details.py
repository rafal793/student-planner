from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.utils import get_color_from_hex
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.factory import Factory

STATUS_BTN_IDS = {
    'completed': 'btn_status_completed',
    'inprogress': 'btn_status_inprogress',
    'atrisk': 'btn_status_atrisk',
    'failed': 'btn_status_failed',
}

class SubjectDetailsScreen(Screen):
    selectedSubject = ObjectProperty(None, allownone=True, rebind=True)
    repo = ObjectProperty(None)
    app = ObjectProperty(None)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.selectedSubject = None

    def on_pre_enter(self):
        self._populate_form()

    def _populate_form(self):
        subject = self.selectedSubject
        if not subject:
            return

        self.ids.input_title.text = str(subject.title or "")
        self.ids.input_teacher.text = str(subject.teacher or "")
        self.ids.input_conditions.text = str(subject.conditions or "")
        self.ids.input_max_absences.text = str(subject.max_absences)
        self.ids.input_max_pluses.text = str(subject.max_pluses)
        self.ids.input_max_colloquium_pluses.text = str(subject.max_colloquium_pluses)
        self.ids.input_note.text = str(subject.note or "")

        self._sync_status_buttons()

    def _sync_status_buttons(self):
        for btn_id in STATUS_BTN_IDS.values():
            self.ids[btn_id].state = 'normal'

        if not self.selectedSubject:
            return

        active_btn = STATUS_BTN_IDS.get(self.selectedSubject.status)
        if active_btn:
            self.ids[active_btn].state = 'down'

    def get_status_text_rgba(self, status):
        colors = self.app.theme.SubjectColors
        status_colors = {
            'completed': colors.SUBJECT_BG_COLOR_COMPLETED,
            'inprogress': colors.SUBJECT_BG_COLOR_INPROGRESS,
            'atrisk': colors.SUBJECT_BG_COLOR_ATRISK,
            'failed': colors.SUBJECT_BG_COLOR_FAILED,
        }
        fallback = colors.SUBJECT_BG_COLOR_FAILED
        return get_color_from_hex(status_colors.get(status, fallback))

    def change_absences(self, diff: int) -> None:
        if self.selectedSubject:
            self.selectedSubject.absences = self.repo.add_absence(
                subject_id=self.selectedSubject.id,
                amount=diff,
            )

    def change_status(self, new_status) -> None:
        if not self.selectedSubject:
            return

        if new_status not in STATUS_BTN_IDS:
            raise ValueError("Invalid status name")

        if self.selectedSubject.status == new_status:
            return

        self.selectedSubject.status = new_status
        self.repo.set_status(subject_id=self.selectedSubject.id, new_status=new_status)
        self._sync_status_buttons()

    def save_changes(self) -> None:
        if self.selectedSubject:
            title = self.ids.input_title.text
            teacher = self.ids.input_teacher.text
            conditions = self.ids.input_conditions.text
            note = self.ids.input_note.text
            max_absences = int(self.ids.input_max_absences.text or 0)
            max_pluses = float(self.ids.input_max_pluses.text or 0)
            max_colloquium_pluses = float(self.ids.input_max_colloquium_pluses.text or 0)

            self.repo.update_subject(
                subject_id=self.selectedSubject.id,
                data={
                    'title': title,
                    'teacher': teacher,
                    'conditions': conditions,
                    'note': note,
                    'max_absences': max_absences,
                    'max_pluses': max_pluses,
                    'max_colloquium_pluses': max_colloquium_pluses,
                },
            )
            print("Zapisano!")

    def show_delete_subject_popup(self) -> None:
        if not self.selectedSubject:
            return

        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        safe_title = str(self.selectedSubject.title or '').replace('[', '').replace(']', '')
        base_msg = self.app.translate('popup_delete_subject_msg', self.app.language)
        message = Label(text=base_msg.format(safe_title), markup=True, halign='center')
        message.bind(size=message.setter('text_size'))
        content.add_widget(message)

        buttons = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        btn_cancel = Factory.StandardUiButton()
        btn_cancel.text = self.app.translate('btn_cancel', self.app.language)
        btn_confirm = Factory.RemoveSubjectButton()
        btn_confirm.text = self.app.translate('btn_delete', self.app.language)
        buttons.add_widget(btn_cancel)
        buttons.add_widget(btn_confirm)
        content.add_widget(buttons)

        popup = Popup(
            title=self.app.translate('popup_delete_subject_title', self.app.language),
            content=content,
            size_hint=(None, None),
            size=(dp(400), dp(200)),
            auto_dismiss=False,
        )
        btn_cancel.bind(on_release=popup.dismiss)
        btn_confirm.bind(on_release=lambda instance: self.delete_subject(popup))
        popup.open()

    def delete_subject(self, popup) -> None:
        if not self.selectedSubject:
            popup.dismiss()
            return

        try:
            self.repo.remove_subject(self.selectedSubject.id)
            popup.dismiss()
            self.selectedSubject = None
            self.app.change_screen('mySubjects')
        except Exception as e:
            popup.dismiss()
            error_prefix = self.app.translate('err_db_delete', self.app.language)
            self.show_delete_error_popup(f"{error_prefix}{str(e)}")

    def show_delete_error_popup(self, error_message: str) -> None:
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        label = Label(text=error_message, halign='center', valign='middle')
        label.bind(size=label.setter('text_size'))
        content.add_widget(label)

        btn_ok = Factory.StandardUiButton()
        btn_ok.text = self.app.translate('btn_close', self.app.language)
        btn_ok.size_hint = (None, None)
        btn_ok.size = (dp(160), dp(40))

        btn_row = BoxLayout(size_hint_y=None, height=dp(40))
        btn_row.add_widget(btn_ok)
        content.add_widget(btn_row)

        popup = Popup(
            title=self.app.translate('popup_error_form_title', self.app.language),
            content=content,
            size_hint=(None, None),
            size=(dp(400), dp(200)),
            auto_dismiss=True,
        )
        btn_ok.bind(on_release=popup.dismiss)
        popup.open()
