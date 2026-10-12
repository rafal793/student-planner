import sqlite3

from database.database_interface import IAppRepository
from paths import get_db_path


DB_NAME = get_db_path()


from functools import wraps

def db_transaction(func):

    @wraps(func)
    def wrapper(self, *args, **kwargs):
  
        conn = self.get_db_connection()

        try:
        
            result = func(self, *args, **kwargs)
            conn.commit()

            return result
        except sqlite3.Error as e:
           
            conn.rollback()
            print(f"Błąd SQL w metodzie {func.__name__}: {e}")


    return wrapper


class SqliteAppRepository(IAppRepository):
    def __init__(self , db_connection) -> None:
        self.conn = db_connection

    def init_db(self) -> None:
       
        cursor = self.get_db_connection().cursor()

        # TABELA 1: PRZEDMIOTY (glowna konfiguracja + sledzenie postepow)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                teacher TEXT,
                status TEXT DEFAULT 'inprogress' CHECK(status IN ('inprogress', 'completed', 'atrisk', 'failed')),
                grading_rules TEXT,              
                max_absences INTEGER DEFAULT 0,
                current_absences INTEGER DEFAULT 0,  -- sledzenie biezacych nieobecnosci
                max_activity_points REAL DEFAULT 0,
                current_activity_points REAL DEFAULT 0, -- aktualnie zdobyte punkty z aktywnosci
                max_colloquium_points REAL DEFAULT 0,
                current_colloquium_points REAL DEFAULT 0, -- aktualnie zdobyte punkty z kolokwiow
                term_start TEXT,                 
                term_end TEXT,
                note TEXT                    
            )
        ''')

        # TABELA 2: HARMONOGRAM
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                day_of_week INTEGER, -- w INTEGER (0=Pon, 6=Niedz)
                start_time TEXT,                 
                duration_minutes INTEGER, -- czas trwania zajec
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
            )
        ''')

        # TABELA 3: NOTATKI
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                note_date TEXT NOT NULL,         
                content TEXT,
                UNIQUE(subject_id, note_date), -- brak mozliwosci stworzenia dwoch roznych notatek dla tego samego przedmiotu w tym samym dniu
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
            )
        ''')

        # TABELA 4: WYDARZENIA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                type TEXT,
                title TEXT,
                date_time TEXT,                  
                FOREIGN KEY (subject_id) REFERENCES subjects (id) ON DELETE CASCADE
            )
        ''')

        # TABELA 5: USTAWIENIA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        cursor.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES ('language', 'pl')")

        self.get_db_connection().commit()
        
        print("Baza danych gotowa do pracy!")
   

    def get_db_connection(self):
        if self.conn is None:
            self.conn = sqlite3.connect(DB_NAME)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON;")
        return self.conn
    
    """
    Settings
    """

    @db_transaction
    def set_language(self,lang) -> None:
        self.get_db_connection().execute(
            "INSERT OR REPLACE INTO app_settings (key, value) VALUES ('language', ?)", 
            (lang,)
        )

    @db_transaction
    def get_language(self) -> str:
        row = self.get_db_connection().execute("SELECT value FROM app_settings WHERE key = 'language'").fetchone()
        return row['value'] if row else 'pl'

    """
    Subjects
    """

    @db_transaction
    def get_all_subjects(self) -> list[dict]:
        rows = self.get_db_connection().execute("SELECT * FROM subjects").fetchall()
        return [dict(row) for row in rows]


    @db_transaction
    def add_absence(self, subject_id: int, amount: int = 1) -> int:
        row = self.get_db_connection().execute(
            '''
            UPDATE subjects 
            SET current_absences = MAX(0, current_absences + ?)
            WHERE id = ?
            RETURNING current_absences
            ''', 
            (amount, subject_id)
        ).fetchone()
  
        return row['current_absences'] if row else 0

    @db_transaction
    def set_status(self, subject_id:int , new_status:str):
        self.get_db_connection().execute(
            '''
            UPDATE subjects 
            SET status = ?
            WHERE id = ?
            ''', 
            (new_status, subject_id)
        )
    

    @db_transaction
    def add_subject(self, data:dict) -> None:
        name = data.get('title')
        teacher = data.get('teacher', '')
        status = data.get('status', 'inprogress')
        grading_rules = data.get('conditions', '')
        max_absences = data.get('max_absences', 0)
        max_activity_points = data.get('max_pluses', 0.0)

        self.get_db_connection().execute(
            '''
            INSERT INTO subjects (
                name, teacher, status, grading_rules, max_absences, max_activity_points
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (name, teacher, status, grading_rules, max_absences, max_activity_points)
        )

    @db_transaction
    def add_subject_with_schedule(self, data: dict) -> int:
        name = data.get('title')
        teacher = data.get('teacher', '')
        grading_rules = data.get('conditions', '')
        max_absences = data.get('max_absences', 0)
        max_activity_points = data.get('max_pluses', 0.0)
        max_colloquium_points = data.get('max_colloquium_pluses', 0.0)
        term_start = data.get('term_start', '')
        term_end = data.get('term_end', '')
        schedule_entries = data.get('schedule', [])

        cursor = self.get_db_connection().execute(
            '''
            INSERT INTO subjects (
                name, teacher, grading_rules, max_absences,
                max_activity_points, max_colloquium_points, term_start, term_end
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                name, teacher, grading_rules, max_absences,
                max_activity_points, max_colloquium_points, term_start, term_end,
            ),
        )
        subject_id = cursor.lastrowid

        for entry in schedule_entries:
            self.get_db_connection().execute(
                '''
                INSERT INTO schedule (subject_id, day_of_week, start_time, duration_minutes)
                VALUES (?, ?, ?, ?)
                ''',
                (
                    subject_id,
                    entry['day_of_week'],
                    entry['start_time'],
                    entry['duration_minutes'],
                ),
            )

        return subject_id

    @db_transaction
    def get_all_schedule_entries(self) -> list[dict]:
        rows = self.get_db_connection().execute(
            '''
            SELECT schedule.id AS schedule_id, schedule.subject_id, schedule.day_of_week,
                   schedule.start_time, schedule.duration_minutes,
                   subjects.name AS subject_name, subjects.term_start, subjects.term_end
            FROM schedule
            JOIN subjects ON schedule.subject_id = subjects.id
            ORDER BY schedule.day_of_week, schedule.start_time
            '''
        ).fetchall()
        return [dict(row) for row in rows]

    @db_transaction
    def update_subject(self, subject_id: int, data: dict) -> None:
        name = data.get('title')
        teacher = data.get('teacher', '')
        grading_rules = data.get('conditions', '')
        max_absences = data.get('max_absences', 0)
        max_activity_points = data.get('max_pluses', 0.0)
        max_colloquium_points = data.get('max_colloquium_pluses', 0.0)
        note = data.get('note')
        self.get_db_connection().execute(
            '''
            UPDATE subjects 
            SET name = ?, teacher = ?, grading_rules = ?,
                max_absences = ?, max_activity_points = ?,
                max_colloquium_points = ?, note = ?
            WHERE id = ?
            ''',
            (
                name, teacher, grading_rules,
                max_absences, max_activity_points,
                max_colloquium_points, note, subject_id,
            )
        )

    @db_transaction
    def remove_subject(self, subject_id:int) -> None:
        self.get_db_connection().execute(
            "DELETE FROM subjects WHERE id = ?", 
            (subject_id,)
        )

    @db_transaction
    def ensure_progress_defaults(self) -> None:
        rows = self.get_db_connection().execute(
            '''
            SELECT id, max_activity_points, max_colloquium_points
            FROM subjects
            '''
        ).fetchall()

        for row in rows:
            max_activity = row['max_activity_points']
            max_colloquium = row['max_colloquium_points']
            if (not max_activity) and (not max_colloquium):
                self.get_db_connection().execute(
                    '''
                    UPDATE subjects
                    SET max_activity_points = 10,
                        max_colloquium_points = 30,
                        current_activity_points = 3,
                        current_colloquium_points = 17
                    WHERE id = ?
                    ''',
                    (row['id'],),
                )

    @db_transaction
    def update_subject_progress(
        self, subject_id: int, current_activity: int, current_colloquium: int
    ) -> None:
        self.get_db_connection().execute(
            '''
            UPDATE subjects
            SET current_activity_points = ?, current_colloquium_points = ?
            WHERE id = ?
            ''',
            (current_activity, current_colloquium, subject_id),
        )

    @db_transaction
    def remove_all_subjects(self) -> None:
        self.get_db_connection().execute(
            "DELETE FROM subjects"
            )
        
        
        

    """
    Notes
    """

    @db_transaction
    def get_daily_note(self, subject_id:int , date:str) -> str:

        row = self.get_db_connection().execute(
            '''
            SELECT content FROM daily_notes 
            WHERE subject_id = ? AND note_date = ?
            ''', 
            (subject_id, date)
        ).fetchone()
          
        return row['content'] if row else ""
    
    @db_transaction
    def set_daily_note(self, subject_id:int , date:str, content:str) -> None:
        self.get_db_connection().execute(
            '''
            INSERT INTO daily_notes (subject_id, note_date, content)
            VALUES (?, ?, ?)
            ON CONFLICT(subject_id, note_date) DO UPDATE SET content = excluded.content
            ''',
            (subject_id, date, content)
        )

    """
    Events
    """

    @db_transaction
    def get_all_events(self) -> list[dict]:
        rows = self.get_db_connection().execute(
            '''
            SELECT events.id, events.title, events.date_time, events.type,
                   events.subject_id, subjects.name AS subject_name
            FROM events
            JOIN subjects ON events.subject_id = subjects.id
            ORDER BY events.date_time ASC
            '''
        ).fetchall()
        return [dict(row) for row in rows]

    @db_transaction
    def get_events_in_range(self, start_date: str, end_date: str) -> list[dict]:
        rows = self.get_db_connection().execute(
            '''
            SELECT events.id, events.title, events.date_time, events.type,
                   events.subject_id, subjects.name AS subject_name
            FROM events
            JOIN subjects ON events.subject_id = subjects.id
            WHERE date(events.date_time) BETWEEN ? AND ?
            ORDER BY events.date_time ASC
            ''',
            (start_date, end_date),
        ).fetchall()
        return [dict(row) for row in rows]

    @db_transaction
    def add_event(self, subject_id: int, event_type: str, title: str, date_time: str) -> None:
        self.get_db_connection().execute(
            "INSERT INTO events (subject_id, type, title, date_time) VALUES (?, ?, ?, ?)",
            (subject_id, event_type, title, date_time),
        )

    @db_transaction
    def remove_event(self, event_id: int) -> None:
        self.get_db_connection().execute(
            "DELETE FROM events WHERE id = ?",
            (event_id,),
        )

    @db_transaction
    def get_upcoming_events(self) -> list[dict]:
        rows = self.get_db_connection().execute('''
            SELECT type, title, date_time 
            FROM events 
            WHERE date_time >= date('now')
            ORDER BY date_time ASC
        ''').fetchall()
        return [dict(row) for row in rows]