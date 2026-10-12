import pytest
from unittest.mock import MagicMock
from views.add_subject.add_subject import AddSubjectScreen

TRANSLATIONS = {
    "err_subject_req": "Nazwa przedmiotu jest wymagana!",
    "err_teacher_req": "Nazwa prowadzącego jest wymagana!",
    "err_end_before_start": "Data końca nie może być wcześniejsza niż startu!",
    "err_invalid_dates": "Daty muszą być w formacie YYYY-MM-DD!",
    "err_absences_int": "Liczba nieobecności musi być liczbą całkowitą.",
    "err_num_positive": "Wartości liczbowe muszą być dodatnie (czas > 0)!",
    "err_num_only": "Pola liczbowe mogą zawierać tylko cyfry\n(np. 1.5 lub 1,5).",
    "err_start_time": "Godzina startu musi być w formacie HH:MM\n(np. 08:00)",
    "err_select_day": "Zaznacz co najmniej jeden dzień zajęć!",
    "err_db_save": "Wystąpił błąd podczas zapisu do bazy:\n",
}

@pytest.fixture
def mock_app():
    app = MagicMock()
    app.language = 'pl'
    app.translate.side_effect = lambda key, lang: TRANSLATIONS.get(key, key)
    return app

@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.add_subject_with_schedule.return_value = 42
    return repo

@pytest.fixture
def mock_screen(mock_app, mock_repo):
    screen = MagicMock()

    screen.ids.input_name.text = "Programowanie Obiektowe"
    screen.ids.input_teacher.text = "Inż. Anna Nowak"
    screen.ids.input_conditions.text = "Projekt i kolokwium"
    screen.ids.input_absences.text = "2"
    screen.ids.input_pluses.text = "3"
    screen.ids.input_points.text = "50"
    screen.ids.input_time.text = "10:30"
    screen.ids.input_duration.text = "2.0"
    screen.ids.input_start_date.text = "2026-10-05"
    screen.ids.input_end_date.text = "2027-01-30"

    screen.ids.chk_mon.active = False
    screen.ids.chk_tue.active = False
    screen.ids.chk_wed.active = True
    screen.ids.chk_thu.active = False
    screen.ids.chk_fri.active = False
    screen.ids.chk_sat.active = False
    screen.ids.chk_sun.active = False

    screen.app = mock_app
    screen.repo = mock_repo
    screen.show_error_popup = MagicMock()
    screen.clear_form = MagicMock()
    screen.save_subject = AddSubjectScreen.save_subject.__get__(screen, AddSubjectScreen)
    return screen


def _schedule_data(mock_screen):
    return mock_screen.repo.add_subject_with_schedule.call_args[0][0]


def test_save_valid_data(mock_screen):
    mock_screen.save_subject()
    mock_screen.show_error_popup.assert_not_called()
    mock_screen.repo.add_subject_with_schedule.assert_called_once()
    data = _schedule_data(mock_screen)
    assert data['title'] == "Programowanie Obiektowe"
    assert len(data['schedule']) == 1
    assert data['schedule'][0]['day_of_week'] == 2

def test_save_all_days_selected(mock_screen):
    for cb in ['chk_mon', 'chk_tue', 'chk_wed', 'chk_thu', 'chk_fri', 'chk_sat', 'chk_sun']:
        getattr(mock_screen.ids, cb).active = True
    mock_screen.save_subject()
    assert len(_schedule_data(mock_screen)['schedule']) == 7

def test_empty_name(mock_screen):
    mock_screen.ids.input_name.text = ""
    mock_screen.save_subject()
    mock_screen.show_error_popup.assert_called()
    mock_screen.repo.add_subject_with_schedule.assert_not_called()

@pytest.mark.parametrize("bad_time", ["24:00", "23:60", "abc", ""])
def test_invalid_time_formats(mock_screen, bad_time):
    mock_screen.ids.input_time.text = bad_time
    mock_screen.save_subject()
    mock_screen.show_error_popup.assert_called()

@pytest.mark.parametrize("field, bad_val", [("input_absences", "abc"),("input_pluses", "1.2.3"),("input_duration", "5,5,5")])
def test_invalid_numeric_formats(mock_screen, field, bad_val):
    getattr(mock_screen.ids, field).text = bad_val
    mock_screen.save_subject()
    mock_screen.show_error_popup.assert_called()

def test_no_day_selected(mock_screen):
    for cb in ['chk_mon', 'chk_tue', 'chk_wed', 'chk_thu', 'chk_fri', 'chk_sat', 'chk_sun']:
        getattr(mock_screen.ids, cb).active = False

    mock_screen.save_subject()

    mock_screen.show_error_popup.assert_called()
    mock_screen.repo.add_subject_with_schedule.assert_not_called()

def test_name_only_spaces(mock_screen):
    mock_screen.ids.input_name.text = "     "

    mock_screen.save_subject()

    mock_screen.show_error_popup.assert_called()
    mock_screen.repo.add_subject_with_schedule.assert_not_called()

def test_empty_teacher(mock_screen):
    mock_screen.ids.input_teacher.text = ""

    mock_screen.save_subject()

    mock_screen.show_error_popup.assert_called()

def test_teacher_only_spaces(mock_screen):
    mock_screen.ids.input_teacher.text = "     "

    mock_screen.save_subject()

    mock_screen.show_error_popup.assert_called()

def test_min_valid_time(mock_screen):
    mock_screen.ids.input_time.text = "00:00"

    mock_screen.save_subject()

    mock_screen.show_error_popup.assert_not_called()

def test_time_single_digit_hour_normalized(mock_screen):
    mock_screen.ids.input_time.text = "8:30"
    mock_screen.save_subject()
    mock_screen.show_error_popup.assert_not_called()
    assert _schedule_data(mock_screen)['schedule'][0]['start_time'] == "08:30"


def test_time_nine_oclock(mock_screen):
    mock_screen.ids.input_time.text = "9:00"
    mock_screen.save_subject()
    mock_screen.show_error_popup.assert_not_called()
    assert _schedule_data(mock_screen)['schedule'][0]['start_time'] == "09:00"


@pytest.mark.parametrize("bad_time", ["9:0", "09:0"])
def test_time_without_leading_zeros(mock_screen, bad_time):
    mock_screen.ids.input_time.text = bad_time

    mock_screen.save_subject()

    mock_screen.show_error_popup.assert_called()

def test_zero_duration(mock_screen):
    mock_screen.ids.input_duration.text = "0"

    mock_screen.save_subject()

    mock_screen.show_error_popup.assert_called()

@pytest.mark.parametrize("bad_date", ["05-10-2026","2026/10/05","abc",""])
def test_invalid_start_date(mock_screen, bad_date):
    mock_screen.ids.input_start_date.text = bad_date

    mock_screen.save_subject()

    mock_screen.show_error_popup.assert_called()

@pytest.mark.parametrize("bad_date", ["30-01-2027","2027/01/30","abc",""])
def test_invalid_end_date(mock_screen, bad_date):
    mock_screen.ids.input_end_date.text = bad_date

    mock_screen.save_subject()

    mock_screen.show_error_popup.assert_called()

def test_end_date_before_start_date(mock_screen):
    mock_screen.ids.input_start_date.text = "2027-01-30"
    mock_screen.ids.input_end_date.text = "2026-10-05"

    mock_screen.save_subject()

    mock_screen.show_error_popup.assert_called()
    mock_screen.repo.add_subject_with_schedule.assert_not_called()

def test_numbers_with_spaces(mock_screen):
    mock_screen.ids.input_points.text = " 50 "

    mock_screen.save_subject()

    mock_screen.show_error_popup.assert_not_called()

def test_polish_characters(mock_screen):
    mock_screen.ids.input_name.text = "Zaawansowane Algorytmy ĄĆĘŁŃÓŚŹŻ"
    mock_screen.ids.input_teacher.text = "dr hab. Żółć"

    mock_screen.save_subject()

    mock_screen.show_error_popup.assert_not_called()

def test_emoji_in_name(mock_screen):
    mock_screen.ids.input_name.text = "Programowanie 🚀"

    mock_screen.save_subject()

    mock_screen.show_error_popup.assert_not_called()

def test_large_duration(mock_screen):
    mock_screen.ids.input_duration.text = "24"

    mock_screen.save_subject()

    mock_screen.show_error_popup.assert_not_called()

@pytest.mark.parametrize("field, val", [("input_absences", "-1"), ("input_pluses", "-0.01"), ("input_points", "-50"),("input_duration", "-1")])
def test_negative_values(mock_screen, field, val):
    getattr(mock_screen.ids, field).text = val
    mock_screen.save_subject()
    mock_screen.show_error_popup.assert_called()
    mock_screen.repo.add_subject_with_schedule.assert_not_called()

def test_zero_values(mock_screen):
    mock_screen.ids.input_absences.text = "0"
    mock_screen.ids.input_pluses.text = "0"
    mock_screen.ids.input_points.text = "0"
    mock_screen.save_subject()
    mock_screen.show_error_popup.assert_not_called()
    mock_screen.repo.add_subject_with_schedule.assert_called()

def test_fractional_absences_not_allowed(mock_screen):
    mock_screen.ids.input_absences.text = "1.5"
    mock_screen.save_subject()
    mock_screen.show_error_popup.assert_called()
    mock_screen.repo.add_subject_with_schedule.assert_not_called()

def test_extreme_large_values(mock_screen):
    mock_screen.ids.input_points.text = "2147483647"
    mock_screen.save_subject()
    mock_screen.show_error_popup.assert_not_called()

def test_extreme_small_positive_values(mock_screen):
    mock_screen.ids.input_points.text = "0.0000001"
    mock_screen.save_subject()
    mock_screen.show_error_popup.assert_not_called()

def test_comma_to_dot_conversion(mock_screen):
    mock_screen.ids.input_duration.text = "1,75"
    mock_screen.save_subject()
    duration_min = _schedule_data(mock_screen)['schedule'][0]['duration_minutes']
    assert duration_min == 105

def test_very_long_inputs(mock_screen):
    long_str = "A" * 500
    mock_screen.ids.input_name.text = long_str
    mock_screen.ids.input_teacher.text = long_str
    mock_screen.save_subject()
    mock_screen.show_error_popup.assert_not_called()
    mock_screen.repo.add_subject_with_schedule.assert_called()

def test_db_crash_shows_error(mock_screen):
    mock_screen.repo.add_subject_with_schedule.side_effect = Exception("DB Connection Lost")
    mock_screen.save_subject()
    mock_screen.show_error_popup.assert_called()
