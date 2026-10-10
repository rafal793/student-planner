from datetime import date, timedelta

today = date.today()
TERM_START = (today - timedelta(days=45)).strftime('%Y-%m-%d')
TERM_END = (today + timedelta(days=90)).strftime('%Y-%m-%d')

def get_future_event_date(days_offset: int, time_str: str) -> str:
    target = today + timedelta(days=days_offset)
    return f"{target.strftime('%Y-%m-%d')} {time_str}"

subjects = [
    {
        'title': 'Wstęp do informatyki',
        'teacher': 'dr inż. Marek Dąbrowski',
        'status': 'atrisk',
        'conditions': 'Obecność obowiązkowa (max 3 nieobecności). Kolokwium 40%, projekt 60%.',
        'max_absences': 3,
        'max_pluses': 10,
        'max_colloquium_pluses': 30,
        'current_pluses': 2,
        'current_colloquium_pluses': 8,
        'current_absences': 2,
        'note': 'Do nadrobienia materiał z list zadań 4–6.',
        'term_start': TERM_START,
        'term_end': TERM_END,
        'schedule': [
            {'day_of_week': 0, 'start_time': '08:00', 'duration_minutes': 90},
            {'day_of_week': 2, 'start_time': '10:30', 'duration_minutes': 120},
        ],
        'events': [
            {'type': 'Kolokwium', 'title': 'Kolokwium wejściowe', 'date_time': get_future_event_date(4, '10:30')},
        ],
    },
    {
        'title': 'Algebra liniowa',
        'teacher': 'prof. dr hab. Teresa Wójcik',
        'status': 'completed',
        'conditions': 'Egzamin pisemny. Zaliczenie przy min. 50% punktów.',
        'max_absences': 5,
        'max_pluses': 15,
        'max_colloquium_pluses': 35,
        'current_pluses': 14,
        'current_colloquium_pluses': 32,
        'current_absences': 0,
        'note': 'Zaliczone w pierwszym terminie — powtórka przed sesją.',
        'term_start': TERM_START,
        'term_end': TERM_END,
        'schedule': [
            {'day_of_week': 1, 'start_time': '09:00', 'duration_minutes': 90},
        ],
        'events': [
            {'type': 'Kolokwium', 'title': 'Kolokwium 1 - Macierze', 'date_time': get_future_event_date(1, '09:00')},
            {'type': 'Egzamin', 'title': 'Egzamin zerowy', 'date_time': get_future_event_date(18, '11:00')},
        ],
    },
    {
        'title': 'Bazy danych',
        'teacher': 'dr hab. Krzysztof Majewski',
        'status': 'inprogress',
        'conditions': 'Projekt SQL + prezentacja. Brak zaliczenia projektu = brak dopuszczenia do egzaminu.',
        'max_absences': 4,
        'max_pluses': 12,
        'max_colloquium_pluses': 28,
        'current_pluses': 7,
        'current_colloquium_pluses': 15,
        'current_absences': 1,
        'note': 'Projekt: normalizacja i schemat relacyjny bazy.',
        'term_start': TERM_START,
        'term_end': TERM_END,
        'schedule': [
            {'day_of_week': 2, 'start_time': '14:00', 'duration_minutes': 120},
            {'day_of_week': 4, 'start_time': '08:00', 'duration_minutes': 100},
        ],
        'events': [
            {'type': 'Egzamin', 'title': 'Egzamin praktyczny SQL', 'date_time': get_future_event_date(8, '08:00')},
            {'type': 'Kolokwium', 'title': 'Obrona projektu etapu 1', 'date_time': get_future_event_date(14, '14:00')},
        ],
    },
    {
        'title': 'Fizyka ogólna',
        'teacher': 'prof. dr hab. Aleksander Rutkowski',
        'status': 'failed',
        'conditions': 'Laboratorium + egzamin. Wymagane zaliczenie wszystkich ćwiczeń.',
        'max_absences': 2,
        'max_pluses': 8,
        'max_colloquium_pluses': 20,
        'current_pluses': 1,
        'current_colloquium_pluses': 3,
        'current_absences': 2,
        'note': 'Poprawka w sesji — skontaktować się w sprawie terminu.',
        'term_start': TERM_START,
        'term_end': TERM_END,
        'schedule': [
            {'day_of_week': 3, 'start_time': '11:00', 'duration_minutes': 45},
        ],
        'events': [
            {'type': 'Egzamin', 'title': 'Egzamin poprawkowy - termin 1', 'date_time': get_future_event_date(12, '11:00')},
        ],
    },
    {
        'title': 'Programowanie obiektowe',
        'teacher': 'dr inż. Joanna Adamska',
        'status': 'inprogress',
        'conditions': 'Zadania laboratoryjne co tydzień. Egzamin praktyczny przy komputerze.',
        'max_absences': 3,
        'max_pluses': 20,
        'max_colloquium_pluses': 40,
        'current_pluses': 18,
        'current_colloquium_pluses': 22,
        'current_absences': 0,
        'note': 'Wzorce projektowe: Factory, Observer, State.',
        'term_start': TERM_START,
        'term_end': TERM_END,
        'schedule': [
            {'day_of_week': 0, 'start_time': '12:00', 'duration_minutes': 90},
            {'day_of_week': 3, 'start_time': '10:30', 'duration_minutes': 150},
        ],
        'events': [
            {'type': 'Kolokwium', 'title': 'Kolokwium z wzorców projektowych', 'date_time': get_future_event_date(3, '10:30')},
            {'type': 'Egzamin', 'title': 'Projekt końcowy aplikacji', 'date_time': get_future_event_date(22, '12:00')},
        ],
    },
    {
        'title': 'Systemy operacyjne',
        'teacher': 'dr inż. Tomasz Grabowski',
        'status': 'atrisk',
        'conditions': 'Kolokwium + praca pisemna. Dopuszczalne maksymalnie 2 nieobecności.',
        'max_absences': 2,
        'max_pluses': 10,
        'max_colloquium_pluses': 25,
        'current_pluses': 4,
        'current_colloquium_pluses': 10,
        'current_absences': 2,
        'note': 'Zagrożenie nieobecnościami — dostarczyć zaświadczenie.',
        'term_start': TERM_START,
        'term_end': TERM_END,
        'schedule': [
            {'day_of_week': 1, 'start_time': '16:00', 'duration_minutes': 90},
            {'day_of_week': 4, 'start_time': '10:00', 'duration_minutes': 60},
        ],
        'events': [
            {'type': 'Kolokwium', 'title': 'Zaliczenie z procesów i wątków', 'date_time': get_future_event_date(6, '10:00')},
        ],
    },
    {
        'title': 'Język angielski B2',
        'teacher': 'mgr Katarzyna Szymańska',
        'status': 'completed',
        'conditions': 'Aktywność na zajęciach + test końcowy. Min. 60% na zaliczenie.',
        'max_absences': 6,
        'max_pluses': 10,
        'max_colloquium_pluses': 20,
        'current_pluses': 10,
        'current_colloquium_pluses': 20,
        'current_absences': 1,
        'note': 'Certyfikat B2 zaliczony.',
        'term_start': TERM_START,
        'term_end': TERM_END,
        'schedule': [
            {'day_of_week': 2, 'start_time': '08:00', 'duration_minutes': 45},
            {'day_of_week': 4, 'start_time': '12:00', 'duration_minutes': 45},
        ],
        'events': [
            {'type': 'Egzamin', 'title': 'Prezentacja zaliczeniowa', 'date_time': get_future_event_date(10, '12:00')},
        ],
    },
]


class DatabaseStarter:
    def __init__(self, repo):
        self.repo = repo

    def remove_all_subjects(self):
        self.repo.remove_all_subjects()

    def add_test_subjects(self):
        for data in subjects:
            subject_id = self.repo.add_subject_with_schedule({
                'title': data['title'],
                'teacher': data.get('teacher', ''),
                'conditions': data.get('conditions', ''),
                'max_absences': data.get('max_absences', 0),
                'max_pluses': data.get('max_pluses', 0),
                'max_colloquium_pluses': data.get('max_colloquium_pluses', 0),
                'term_start': data.get('term_start', TERM_START),
                'term_end': data.get('term_end', TERM_END),
                'schedule': data.get('schedule', []),
            })

            status = data.get('status', 'inprogress')
            if status != 'inprogress':
                self.repo.set_status(subject_id, status)

            self.repo.update_subject(subject_id, {
                'title': data['title'],
                'teacher': data.get('teacher', ''),
                'conditions': data.get('conditions', ''),
                'max_absences': data.get('max_absences', 0),
                'max_pluses': data.get('max_pluses', 0),
                'max_colloquium_pluses': data.get('max_colloquium_pluses', 0),
                'note': data.get('note', ''),
            })

            self.repo.update_subject_progress(
                subject_id,
                data.get('current_pluses', 0),
                data.get('current_colloquium_pluses', 0),
            )

            absences = data.get('current_absences', 0)
            if absences:
                self.repo.add_absence(subject_id, absences)

            for event in data.get('events', []):
                self.repo.add_event(
                    subject_id,
                    event['type'],
                    event['title'],
                    event['date_time'],
                )

    def refresh_demo_dates(self):
        """Przesuwa daty przedmiotów demo względem dziś, żeby kalendarz zawsze pokazywał kafelki."""
        by_name = {row['name']: row for row in self.repo.get_all_subjects()}
        conn = self.repo.get_db_connection()

        for data in subjects:
            subject = by_name.get(data['title'])
            if not subject:
                continue

            subject_id = subject['id']
            conn.execute(
                "UPDATE subjects SET term_start = ?, term_end = ? WHERE id = ?",
                (TERM_START, TERM_END, subject_id),
            )
            conn.execute("DELETE FROM events WHERE subject_id = ?", (subject_id,))
            for event in data.get('events', []):
                conn.execute(
                    "INSERT INTO events (subject_id, type, title, date_time) VALUES (?, ?, ?, ?)",
                    (subject_id, event['type'], event['title'], event['date_time']),
                )

        conn.commit()


if __name__ == '__main__':
    import sqlite3
    from paths import get_db_path
    from Database.database_sqllite import SqliteAppRepository

    db_path = get_db_path()
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    repo = SqliteAppRepository(connection)

    starter = DatabaseStarter(repo)
    print("Clearing old subjects...")
    starter.remove_all_subjects()
    print("Populating database with test curriculum...")
    starter.add_test_subjects()
    print("Database seeding completed successfully.")