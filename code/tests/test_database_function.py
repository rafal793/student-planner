import sqlite3
import pytest
from datetime import date, timedelta

from database.database_sqlite import SqliteAppRepository
from Widgets.calendarEvents import build_week_calendar_events
from tests.create_default_values import DatabaseStarter

@pytest.fixture
def db_repo():
# fresh in-memory DB before each test
    connection = sqlite3.connect(':memory:')
    connection.row_factory = sqlite3.Row
    # need foreign keys for cascade-delete tests
    connection.execute("PRAGMA foreign_keys = ON;") 
    
    repo = SqliteAppRepository(connection)
    repo.init_db()
    
    yield repo
    
    connection.close()

# init

def test_init_db_creates_all_tables(db_repo):
    connection = db_repo.get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row['name'] for row in cursor.fetchall()]
    
    assert 'subjects' in tables
    assert 'schedule' in tables
    assert 'daily_notes' in tables
    assert 'events' in tables
    assert 'app_settings' in tables

# settings

def test_language_settings(db_repo):

    assert db_repo.get_language() == 'pl'
    
    # language change
    db_repo.set_language('en')
    assert db_repo.get_language() == 'en'

# subjects

def test_add_and_get_subjects(db_repo):
    subject_data = {
        'title': 'Matematyka Dyskretna',
        'teacher': 'dr inż. Jan Kowalski',
        'status': 'inprogress',
        'conditions': 'Egzamin końcowy 50%, projekty 50%',
        'max_absences': 3,
        'max_pluses': 10.0
    }
    
    db_repo.add_subject(subject_data)
    fetched_subjects = db_repo.get_all_subjects()
    
    assert len(fetched_subjects) == 1
    assert fetched_subjects[0]['name'] == 'Matematyka Dyskretna'
    assert fetched_subjects[0]['teacher'] == 'dr inż. Jan Kowalski'
    assert fetched_subjects[0]['current_absences'] == 0

def test_update_subject(db_repo):
    db_repo.add_subject({'title': 'Fizyka'})
    subject_id = db_repo.get_all_subjects()[0]['id']
    
    update_data = {
        'title': 'Fizyka Kwantowa',
        'teacher': 'prof. dr hab. Andrzej Nowak',
        'conditions': 'Projekt zaliczeniowy',
        'max_absences': 5,
        'max_pluses': 15.0,
        'max_colloquium_pluses': 20.0,
        'note': 'Trudny przedmiot, wymagana obecność'
    }
    
    db_repo.update_subject(subject_id, update_data)
    updated_subject = db_repo.get_all_subjects()[0]
    
    assert updated_subject['name'] == 'Fizyka Kwantowa'
    assert updated_subject['note'] == 'Trudny przedmiot, wymagana obecność'
    assert updated_subject['max_absences'] == 5
    assert updated_subject['max_activity_points'] == 15.0
    assert updated_subject['max_colloquium_points'] == 20.0

def test_remove_subject(db_repo):
    db_repo.add_subject({'title': 'Chemia Organiczna'})
    db_repo.add_subject({'title': 'Biologia Komórki'})
    
    subjects_before = db_repo.get_all_subjects()
    assert len(subjects_before) == 2
    
    subject_id_to_remove = subjects_before[0]['id']
    db_repo.remove_subject(subject_id_to_remove)
    
    subjects_after = db_repo.get_all_subjects()
    assert len(subjects_after) == 1
    assert subjects_after[0]['name'] == 'Biologia Komórki'

def test_set_status(db_repo):
    db_repo.add_subject({'title': 'Historia Polski', 'status': 'inprogress'})
    subject_id = db_repo.get_all_subjects()[0]['id']
    
    db_repo.set_status(subject_id, 'completed')
    
    updated_subject = db_repo.get_all_subjects()[0]
    assert updated_subject['status'] == 'completed'

def test_ensure_progress_defaults(db_repo):
    db_repo.add_subject({'title': 'Logika'})
    subject = db_repo.get_all_subjects()[0]
    assert subject['max_activity_points'] == 0
    assert subject['max_colloquium_points'] == 0

    db_repo.ensure_progress_defaults()
    updated = db_repo.get_all_subjects()[0]

    assert updated['max_activity_points'] == 10
    assert updated['max_colloquium_points'] == 30
    assert updated['current_activity_points'] == 3
    assert updated['current_colloquium_points'] == 17

def test_update_subject_progress(db_repo):
    db_repo.add_subject({'title': 'Algorytmy'})
    subject_id = db_repo.get_all_subjects()[0]['id']

    db_repo.update_subject_progress(subject_id, 7, 12)
    updated = db_repo.get_all_subjects()[0]

    assert updated['current_activity_points'] == 7
    assert updated['current_colloquium_points'] == 12

def test_add_subject_with_schedule(db_repo):
    subject_id = db_repo.add_subject_with_schedule({
        'title': 'Programowanie Obiektowe',
        'teacher': 'Inż. Anna Nowak',
        'conditions': 'Projekt i kolokwium',
        'max_absences': 2,
        'max_pluses': 3.0,
        'max_colloquium_pluses': 50.0,
        'term_start': '2026-10-05',
        'term_end': '2027-01-30',
        'schedule': [
            {'day_of_week': 2, 'start_time': '10:30', 'duration_minutes': 120},
            {'day_of_week': 4, 'start_time': '10:30', 'duration_minutes': 120},
        ],
    })

    assert subject_id == 1
    subject = db_repo.get_all_subjects()[0]
    assert subject['name'] == 'Programowanie Obiektowe'
    assert subject['max_colloquium_points'] == 50.0
    assert subject['term_start'] == '2026-10-05'

    connection = db_repo.get_db_connection()
    rows = connection.execute(
        'SELECT day_of_week, start_time, duration_minutes FROM schedule WHERE subject_id = ?',
        (subject_id,),
    ).fetchall()
    assert len(rows) == 2
    assert rows[0]['day_of_week'] == 2
    assert rows[0]['duration_minutes'] == 120

def test_get_all_schedule_entries(db_repo):
    subject_id = db_repo.add_subject_with_schedule({
        'title': 'Bazy Danych',
        'teacher': 'Dr X',
        'conditions': 'Egzamin',
        'max_absences': 2,
        'max_pluses': 5.0,
        'max_colloquium_pluses': 30.0,
        'term_start': '2026-03-01',
        'term_end': '2026-06-30',
        'schedule': [
            {'day_of_week': 1, 'start_time': '11:00', 'duration_minutes': 90},
        ],
    })

    entries = db_repo.get_all_schedule_entries()

    assert len(entries) == 1
    assert entries[0]['subject_id'] == subject_id
    assert entries[0]['subject_name'] == 'Bazy Danych'
    assert entries[0]['start_time'] == '11:00'

def test_get_events_in_range(db_repo):
    db_repo.add_subject({'title': 'Fizyka'})
    subject_id = db_repo.get_all_subjects()[0]['id']
    db_repo.add_event(subject_id, 'egzamin', 'Kolokwium', '2026-05-10 09:30')
    db_repo.add_event(subject_id, 'egzamin', 'Egzamin', '2026-06-01 14:00')

    events = db_repo.get_events_in_range('2026-05-01', '2026-05-31')

    assert len(events) == 1
    assert events[0]['title'] == 'Kolokwium'

def test_seed_schedule_spreads_across_week(db_repo):
    DatabaseStarter(db_repo).add_test_subjects()
    # Demo term dates are relative to today — use the current week, not a fixed June date.
    week_start = date.today() - timedelta(days=date.today().weekday())
    entries = db_repo.get_all_schedule_entries()
    events = build_week_calendar_events(week_start, entries)
    by_date = {}
    for item in events:
        by_date.setdefault(item['date'].isoformat(), []).append(item['data'].title)

    assert len(by_date[(week_start + timedelta(days=0)).isoformat()]) == 2
    assert len(by_date[(week_start + timedelta(days=1)).isoformat()]) == 2
    assert len(by_date[(week_start + timedelta(days=2)).isoformat()]) == 3
    assert len(by_date[(week_start + timedelta(days=3)).isoformat()]) == 2
    assert len(by_date[(week_start + timedelta(days=4)).isoformat()]) == 3

# absences

def test_add_absence_logic(db_repo):
    db_repo.add_subject({'title': 'Rysunek Techniczny'})
    subject_id = db_repo.get_all_subjects()[0]['id']
    
    # add 2 absences
    current = db_repo.add_absence(subject_id, 2)
    assert current == 2
    
    # remove 1 absence
    current = db_repo.add_absence(subject_id, -1)
    assert current == 1
    
    # should not go below 0
    current = db_repo.add_absence(subject_id, -5)
    assert current == 0

# daily notes

def test_set_and_get_daily_note(db_repo):
    db_repo.add_subject({'title': 'Programowanie w Pythonie'})
    subject_id = db_repo.get_all_subjects()[0]['id']
    test_date = '2026-06-01'
    
    # create note
    db_repo.set_daily_note(subject_id, test_date, 'Nauka dekoratorów i generatorów')
    note_content = db_repo.get_daily_note(subject_id, test_date)
    assert note_content == 'Nauka dekoratorów i generatorów'
    
    # overwrite same day/subject
    db_repo.set_daily_note(subject_id, test_date, 'Zaktualizowana treść notatki z zajęć')
    updated_content = db_repo.get_daily_note(subject_id, test_date)
    assert updated_content == 'Zaktualizowana treść notatki z zajęć'

def test_get_nonexistent_daily_note_returns_empty_string(db_repo):
    db_repo.add_subject({'title': 'Systemy Baz Danych'})
    subject_id = db_repo.get_all_subjects()[0]['id']
    
    note_content = db_repo.get_daily_note(subject_id, '2099-01-01')
    assert note_content == ""

def test_add_subject_minimum_data(db_repo):
    db_repo.add_subject({'title': 'Matematyka'})

    subject = db_repo.get_all_subjects()[0]

    assert subject['name'] == 'Matematyka'
    assert subject['teacher'] == ''
    assert subject['status'] == 'inprogress'
    assert subject['current_absences'] == 0

def test_add_multiple_subjects(db_repo):
    for i in range(10):
        db_repo.add_subject({'title': f'Przedmiot {i}'})

    subjects = db_repo.get_all_subjects()

    assert len(subjects) == 10

def test_update_nonexistent_subject(db_repo):
    db_repo.update_subject(9999,{'title': 'Nieistniejący'})

    assert db_repo.get_all_subjects() == []

def test_remove_nonexistent_subject(db_repo):
    db_repo.remove_subject(9999)

    assert db_repo.get_all_subjects() == []

def test_remove_all_subjects(db_repo):
    db_repo.add_subject({'title': 'A'})
    db_repo.add_subject({'title': 'B'})
    db_repo.add_subject({'title': 'C'})

    assert len(db_repo.get_all_subjects()) == 3

    db_repo.remove_all_subjects()

    assert db_repo.get_all_subjects() == []

def test_absences_cannot_go_below_zero(db_repo):
    db_repo.add_subject({'title': 'Matma'})
    subject_id = db_repo.get_all_subjects()[0]['id']

    current = db_repo.add_absence(subject_id, -999)

    assert current == 0

def test_add_absence_nonexistent_subject(db_repo):
    current = db_repo.add_absence(9999, 1)

    assert current == 0

def test_large_absence_increment(db_repo):
    db_repo.add_subject({'title': 'Historia'})
    subject_id = db_repo.get_all_subjects()[0]['id']

    current = db_repo.add_absence(subject_id, 1000)

    assert current == 1000

def test_multiple_status_changes(db_repo):
    db_repo.add_subject({'title': 'Matma'})
    subject_id = db_repo.get_all_subjects()[0]['id']

    db_repo.set_status(subject_id, 'atrisk')
    db_repo.set_status(subject_id, 'failed')
    db_repo.set_status(subject_id, 'completed')

    subject = db_repo.get_all_subjects()[0]

    assert subject['status'] == 'completed'

def test_set_status_nonexistent_subject(db_repo):
    db_repo.set_status(9999, 'completed')

    assert db_repo.get_all_subjects() == []

def test_set_empty_daily_note(db_repo):
    db_repo.add_subject({'title': 'Programowanie'})
    subject_id = db_repo.get_all_subjects()[0]['id']

    db_repo.set_daily_note(subject_id,'2026-06-01','')

    note = db_repo.get_daily_note(subject_id,'2026-06-01')

    assert note == ''

def test_very_long_daily_note(db_repo):
    db_repo.add_subject({'title': 'Programowanie'})
    subject_id = db_repo.get_all_subjects()[0]['id']

    long_note = "A" * 10000

    db_repo.set_daily_note(subject_id,'2026-06-01',long_note)

    note = db_repo.get_daily_note(subject_id,'2026-06-01')

    assert note == long_note

def test_multiple_daily_notes_for_same_subject(db_repo):
    db_repo.add_subject({'title': 'Programowanie'})
    subject_id = db_repo.get_all_subjects()[0]['id']

    db_repo.set_daily_note(subject_id,'2026-06-01','Notatka 1')

    db_repo.set_daily_note(subject_id,'2026-06-02','Notatka 2')

    assert db_repo.get_daily_note(subject_id,'2026-06-01') == 'Notatka 1'

    assert db_repo.get_daily_note(subject_id,'2026-06-02') == 'Notatka 2'

def test_polish_characters(db_repo):
    db_repo.add_subject({'title': 'Programowanie Obiektowe','teacher': 'Łukasz Żółć'})

    subject = db_repo.get_all_subjects()[0]

    assert subject['teacher'] == 'Łukasz Żółć'

def test_unicode_subject_name(db_repo):
    db_repo.add_subject({'title': '📚 Matematyka 🚀'})

    subject = db_repo.get_all_subjects()[0]

    assert subject['name'] == '📚 Matematyka 🚀'

def test_default_language_exists(db_repo):
    assert db_repo.get_language() == 'pl'

def test_language_multiple_changes(db_repo):
    db_repo.set_language('en')
    db_repo.set_language('de')
    db_repo.set_language('pl')

    assert db_repo.get_language() == 'pl'

def test_cascade_delete_daily_notes(db_repo):
    db_repo.add_subject({'title': 'Programowanie'})

    subject_id = db_repo.get_all_subjects()[0]['id']

    db_repo.set_daily_note(subject_id,'2026-06-01','Testowa notatka')

    db_repo.remove_subject(subject_id)

    connection = db_repo.get_db_connection()

    count = connection.execute("SELECT COUNT(*) AS cnt FROM daily_notes").fetchone()['cnt']
    assert count == 0

def test_subject_ids_are_unique(db_repo):
    db_repo.add_subject({'title': 'A'})
    db_repo.add_subject({'title': 'B'})

    subjects = db_repo.get_all_subjects()

    ids = [s['id'] for s in subjects]
    assert len(ids) == len(set(ids))

def test_empty_teacher_is_allowed(db_repo):
    db_repo.add_subject({'title': 'Matematyka','teacher': ''})

    subject = db_repo.get_all_subjects()[0]
    assert subject['teacher'] == ''

def test_empty_conditions_are_allowed(db_repo):
    db_repo.add_subject({'title': 'Matematyka', 'conditions': ''})

    subject = db_repo.get_all_subjects()[0]
    assert subject['grading_rules'] == ''

def test_add_and_get_all_events(db_repo):
    subject_id = db_repo.get_all_subjects()[0]['id'] if db_repo.get_all_subjects() else None
    if subject_id is None:
        db_repo.add_subject({'title': 'IO', 'teacher': 'Kawa'})
        subject_id = db_repo.get_all_subjects()[0]['id']

    db_repo.add_event(subject_id, "Egzamin", "Kolokwium 1", "2026-06-10 10:00")
    events = db_repo.get_all_events()

    assert len(events) == 1
    assert events[0]['title'] == "Kolokwium 1"
    assert events[0]['subject_name'] == "IO"
    assert events[0]['type'] == "Egzamin"

def test_remove_event(db_repo):
    db_repo.add_subject({'title': 'SK', 'teacher': 'Nowak'})
    subject_id = db_repo.get_all_subjects()[0]['id']
    db_repo.add_event(subject_id, "Kolokwium", "Test", "2026-06-15 12:00")

    event_id = db_repo.get_all_events()[0]['id']
    db_repo.remove_event(event_id)

    assert db_repo.get_all_events() == []