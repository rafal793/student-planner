import pytest
from unittest.mock import MagicMock
from models.subject_data import SubjectData
from views.subject_details.subject_details import SubjectDetailsScreen


@pytest.fixture
def mock_app():
    app = MagicMock()
    app.language = 'pl'
    colors = app.theme.SubjectColors
    colors.SUBJECT_BG_COLOR_COMPLETED = '#62c57b'
    colors.SUBJECT_BG_COLOR_INPROGRESS = '#d9d9d7'
    colors.SUBJECT_BG_COLOR_ATRISK = '#f28b82'
    colors.SUBJECT_BG_COLOR_FAILED = '#272724'
    return app


@pytest.fixture
def subject():
    return SubjectData.create_from_db_dict({
        'id': 1,
        'name': 'Bazy danych',
        'teacher': 'dr Kowalski',
        'status': 'inprogress',
        'grading_rules': 'Egzamin 50%, projekt 50%',
        'current_absences': 1,
        'max_absences': 3,
        'max_activity_points': 10,
        'max_colloquium_points': 20,
        'note': 'Notatka testowa',
    })


@pytest.fixture
def details_screen(mock_app, subject):
    screen = SubjectDetailsScreen()
    screen.app = mock_app
    screen.repo = MagicMock()
    screen.selectedSubject = subject

    for field in [
        'input_title', 'input_teacher', 'input_conditions',
        'input_max_absences', 'input_max_pluses',
        'input_max_colloquium_pluses', 'input_note',
    ]:
        screen.ids[field] = MagicMock()
        screen.ids[field].text = ""

    for btn_id in [
        'btn_status_completed', 'btn_status_inprogress',
        'btn_status_atrisk', 'btn_status_failed',
    ]:
        screen.ids[btn_id] = MagicMock()
        screen.ids[btn_id].state = 'normal'

    return screen


def test_populate_form_uses_subject_data(details_screen, subject):
    details_screen._populate_form()

    assert details_screen.ids['input_title'].text == subject.title
    assert details_screen.ids['input_conditions'].text == subject.conditions
    assert details_screen.ids['input_max_pluses'].text == str(subject.max_pluses)
    assert details_screen.ids['input_max_colloquium_pluses'].text == str(subject.max_colloquium_pluses)


def test_sync_status_buttons_resets_all_then_sets_active(details_screen):
    details_screen.ids['btn_status_completed'].state = 'down'
    details_screen.ids['btn_status_atrisk'].state = 'down'

    details_screen._sync_status_buttons()

    assert details_screen.ids['btn_status_completed'].state == 'normal'
    assert details_screen.ids['btn_status_atrisk'].state == 'normal'
    assert details_screen.ids['btn_status_inprogress'].state == 'down'


def test_get_status_text_rgba_uses_theme(details_screen, mock_app):
    rgba = details_screen.get_status_text_rgba('completed')

    assert tuple(rgba) == (98 / 255, 197 / 255, 123 / 255, 1.0)


def test_change_status_syncs_buttons(details_screen, subject):
    details_screen.change_status('completed')

    assert subject.status == 'completed'
    assert details_screen.ids['btn_status_completed'].state == 'down'
    assert details_screen.ids['btn_status_inprogress'].state == 'normal'


def test_delete_subject_removes_and_navigates(details_screen, subject):
    popup = MagicMock()
    details_screen.delete_subject(popup)

    details_screen.repo.remove_subject.assert_called_once_with(subject.id)
    popup.dismiss.assert_called_once()
    assert details_screen.selectedSubject is None
    details_screen.app.change_screen.assert_called_once_with('mySubjects')


def test_delete_subject_no_op_without_selection(details_screen):
    details_screen.selectedSubject = None
    popup = MagicMock()

    details_screen.delete_subject(popup)

    details_screen.repo.remove_subject.assert_not_called()
    popup.dismiss.assert_called_once()
