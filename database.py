from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


DB_FILE = "student_planner.db"


class Database:
    """Lightweight SQLite wrapper used by the Student Planner app.

    All write operations commit immediately so that the on-disk file always
    reflects the current state of the UI. Methods return either ``sqlite3.Row``
    objects (which behave like dicts and tuples) or simple Python primitives.
    """

    def __init__(self, db_path: str = DB_FILE) -> None:
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        self._seed_defaults()

    # ------------------------------------------------------------------ schema

    def _create_tables(self) -> None:
        self.conn.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                teacher TEXT NOT NULL,
                grading_rules TEXT NOT NULL,
                max_absences INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'in_progress',
                general_note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS absences (
                subject_id INTEGER PRIMARY KEY,
                count INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER,
                title TEXT NOT NULL,
                event_date TEXT NOT NULL,
                event_type TEXT NOT NULL DEFAULT 'class',
                notified INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS recurring_classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL,
                weekday INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS subject_activity (
                subject_id INTEGER PRIMARY KEY,
                pluses INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS subject_colloquium_progress (
                subject_id INTEGER PRIMARY KEY,
                points REAL NOT NULL DEFAULT 0,
                FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS daily_subject_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL,
                note_date TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL,
                UNIQUE(subject_id, note_date),
                FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
            );
            """
        )
        self._ensure_subject_columns()
        self.conn.commit()

    def _ensure_subject_columns(self) -> None:
        columns = {row["name"] for row in self.conn.execute("PRAGMA table_info(subjects)").fetchall()}
        migrations = {
            "max_activity_points": "REAL NOT NULL DEFAULT 0",
            "max_colloquium_points": "REAL NOT NULL DEFAULT 0",
            "start_date": "TEXT NOT NULL DEFAULT ''",
            "end_date": "TEXT NOT NULL DEFAULT ''",
        }
        for column, definition in migrations.items():
            if column not in columns:
                self.conn.execute(f"ALTER TABLE subjects ADD COLUMN {column} {definition}")

    def _seed_defaults(self) -> None:
        defaults = {
            "language": "pl",
            "session_target_date": "",
        }
        for key, value in defaults.items():
            self.conn.execute(
                "INSERT OR IGNORE INTO app_settings (key, value) VALUES (?, ?)",
                (key, value),
            )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # ----------------------------------------------------------------- subjects

    def add_subject(
        self,
        name: str,
        teacher: str,
        grading_rules: str,
        max_absences: int,
        max_activity_points: float = 0,
        max_colloquium_points: float = 0,
        start_date: str = "",
        end_date: str = "",
    ) -> int:
        now = datetime.now().isoformat()
        cur = self.conn.execute(
            """
            INSERT INTO subjects (
                name, teacher, grading_rules, max_absences, max_activity_points, max_colloquium_points,
                start_date, end_date, status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'in_progress', ?)
            """,
            (
                name.strip(),
                teacher.strip(),
                grading_rules.strip(),
                int(max_absences),
                float(max_activity_points),
                float(max_colloquium_points),
                start_date.strip(),
                end_date.strip(),
                now,
            ),
        )
        subject_id = int(cur.lastrowid)
        self.conn.execute("INSERT INTO absences (subject_id, count) VALUES (?, 0)", (subject_id,))
        self.conn.execute("INSERT INTO subject_activity (subject_id, pluses) VALUES (?, 0)", (subject_id,))
        self.conn.execute(
            "INSERT INTO subject_colloquium_progress (subject_id, points) VALUES (?, 0)",
            (subject_id,),
        )
        self.conn.commit()
        return subject_id

    def update_subject(
        self,
        subject_id: int,
        name: str,
        teacher: str,
        grading_rules: str,
        max_absences: int,
        max_activity_points: float,
        max_colloquium_points: float,
        start_date: str = "",
        end_date: str = "",
    ) -> None:
        self.conn.execute(
            """
            UPDATE subjects
            SET name = ?,
                teacher = ?,
                grading_rules = ?,
                max_absences = ?,
                max_activity_points = ?,
                max_colloquium_points = ?,
                start_date = ?,
                end_date = ?
            WHERE id = ?
            """,
            (
                name.strip(),
                teacher.strip(),
                grading_rules.strip(),
                int(max_absences),
                float(max_activity_points),
                float(max_colloquium_points),
                start_date.strip(),
                end_date.strip(),
                subject_id,
            ),
        )
        self.conn.commit()

    def list_subjects(self) -> list[sqlite3.Row]:
        rows = self.conn.execute(
            """
            SELECT s.*, COALESCE(a.count, 0) AS absences_count
            FROM subjects s
            LEFT JOIN absences a ON a.subject_id = s.id
            ORDER BY s.name COLLATE NOCASE
            """
        ).fetchall()
        return list(rows)

    def get_subject(self, subject_id: int) -> sqlite3.Row | None:
        return self.conn.execute(
            """
            SELECT s.*, COALESCE(a.count, 0) AS absences_count
            FROM subjects s
            LEFT JOIN absences a ON a.subject_id = s.id
            WHERE s.id = ?
            """,
            (subject_id,),
        ).fetchone()

    def set_subject_status(self, subject_id: int, status: str) -> None:
        self.conn.execute("UPDATE subjects SET status = ? WHERE id = ?", (status, subject_id))
        self.conn.commit()

    def update_general_note(self, subject_id: int, note: str) -> None:
        self.conn.execute("UPDATE subjects SET general_note = ? WHERE id = ?", (note, subject_id))
        self.conn.commit()

    def delete_subject(self, subject_id: int) -> None:
        # Events use ON DELETE SET NULL so we drop them explicitly to avoid
        # leaving orphaned rows for a subject that no longer exists.
        self.conn.execute("DELETE FROM events WHERE subject_id = ?", (subject_id,))
        self.conn.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        self.conn.commit()

    def get_subject_rules(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT s.id, s.name, s.teacher, s.grading_rules, s.max_absences, s.status,
                   COALESCE(a.count, 0) AS absences_count
            FROM subjects s
            LEFT JOIN absences a ON a.subject_id = s.id
            ORDER BY s.name COLLATE NOCASE
            """
        ).fetchall()
        return [dict(r) for r in rows]

    # ----------------------------------------------------------------- absences

    def update_absences(self, subject_id: int, delta: int) -> None:
        self.conn.execute(
            """
            INSERT INTO absences (subject_id, count) VALUES (?, 0)
            ON CONFLICT(subject_id) DO NOTHING
            """,
            (subject_id,),
        )
        self.conn.execute(
            "UPDATE absences SET count = MAX(0, count + ?) WHERE subject_id = ?",
            (int(delta), subject_id),
        )
        self.conn.commit()

    # ------------------------------------------------------- recurring classes

    def add_recurring_class(
        self, subject_id: int, weekday: int, start_time: str, duration_minutes: int
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO recurring_classes (subject_id, weekday, start_time, duration_minutes)
            VALUES (?, ?, ?, ?)
            """,
            (subject_id, int(weekday), start_time, max(15, int(duration_minutes))),
        )
        self.conn.commit()

    def list_recurring_classes(self) -> list[sqlite3.Row]:
        rows = self.conn.execute(
            """
            SELECT rc.*, s.name AS subject_name, s.teacher AS teacher_name,
                   s.start_date AS subject_start_date, s.end_date AS subject_end_date
            FROM recurring_classes rc
            JOIN subjects s ON s.id = rc.subject_id
            ORDER BY rc.weekday, rc.start_time
            """
        ).fetchall()
        return list(rows)

    # --------------------------------------------------------------- progress

    def get_activity_pluses(self, subject_id: int) -> int:
        self.conn.execute(
            "INSERT INTO subject_activity (subject_id, pluses) VALUES (?, 0) "
            "ON CONFLICT(subject_id) DO NOTHING",
            (subject_id,),
        )
        row = self.conn.execute(
            "SELECT pluses FROM subject_activity WHERE subject_id = ?",
            (subject_id,),
        ).fetchone()
        return int(row["pluses"]) if row else 0

    def update_activity_pluses(
        self, subject_id: int, delta: int, max_pluses: float | None = None
    ) -> int:
        current = self.get_activity_pluses(subject_id)
        updated = max(0, current + int(delta))
        if max_pluses is not None:
            updated = min(updated, int(max(0.0, max_pluses)))
        self.conn.execute(
            "UPDATE subject_activity SET pluses = ? WHERE subject_id = ?",
            (updated, subject_id),
        )
        self.conn.commit()
        return updated

    def get_colloquium_points(self, subject_id: int) -> float:
        self.conn.execute(
            "INSERT INTO subject_colloquium_progress (subject_id, points) VALUES (?, 0) "
            "ON CONFLICT(subject_id) DO NOTHING",
            (subject_id,),
        )
        row = self.conn.execute(
            "SELECT points FROM subject_colloquium_progress WHERE subject_id = ?",
            (subject_id,),
        ).fetchone()
        return float(row["points"]) if row else 0.0

    def update_colloquium_points(
        self, subject_id: int, delta: float, max_colloquium_points: float | None = None
    ) -> float:
        current = self.get_colloquium_points(subject_id)
        updated = max(0.0, current + float(delta))
        if max_colloquium_points is not None:
            updated = min(updated, max(0.0, float(max_colloquium_points)))
        self.conn.execute(
            "UPDATE subject_colloquium_progress SET points = ? WHERE subject_id = ?",
            (updated, subject_id),
        )
        self.conn.commit()
        return updated

    # ----------------------------------------------------------------- events

    def add_event(
        self, subject_id: int | None, title: str, event_date: str, event_type: str
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO events (subject_id, title, event_date, event_type, notified)
            VALUES (?, ?, ?, ?, 0)
            """,
            (subject_id, title.strip(), event_date.strip(), event_type.strip()),
        )
        self.conn.commit()

    def list_upcoming_events(self) -> list[sqlite3.Row]:
        rows = self.conn.execute(
            """
            SELECT e.*, s.name AS subject_name
            FROM events e
            LEFT JOIN subjects s ON s.id = e.subject_id
            WHERE date(e.event_date) >= date('now')
            ORDER BY date(e.event_date), e.title
            """
        ).fetchall()
        return list(rows)

    def list_events_for_notifications(self) -> list[sqlite3.Row]:
        rows = self.conn.execute(
            """
            SELECT e.*, s.name AS subject_name
            FROM events e
            LEFT JOIN subjects s ON s.id = e.subject_id
            WHERE e.notified = 0
            """
        ).fetchall()
        return list(rows)

    def mark_event_notified(self, event_id: int) -> None:
        self.conn.execute("UPDATE events SET notified = 1 WHERE id = ?", (event_id,))
        self.conn.commit()

    def delete_event(self, event_id: int) -> None:
        self.conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
        self.conn.commit()

    # ------------------------------------------------------------ daily notes

    def has_daily_note(self, subject_id: int, note_date: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM daily_subject_notes "
            "WHERE subject_id = ? AND note_date = ? AND TRIM(content) != '' LIMIT 1",
            (subject_id, note_date),
        ).fetchone()
        return row is not None

    def get_daily_note(self, subject_id: int, note_date: str) -> str:
        row = self.conn.execute(
            "SELECT content FROM daily_subject_notes WHERE subject_id = ? AND note_date = ?",
            (subject_id, note_date),
        ).fetchone()
        return str(row["content"]) if row else ""

    def set_daily_note(self, subject_id: int, note_date: str, content: str) -> None:
        if not content.strip():
            self.conn.execute(
                "DELETE FROM daily_subject_notes WHERE subject_id = ? AND note_date = ?",
                (subject_id, note_date),
            )
            self.conn.commit()
            return
        now = datetime.now().isoformat()
        self.conn.execute(
            """
            INSERT INTO daily_subject_notes (subject_id, note_date, content, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(subject_id, note_date) DO UPDATE
            SET content = excluded.content,
                updated_at = excluded.updated_at
            """,
            (subject_id, note_date, content, now),
        )
        self.conn.commit()

    # --------------------------------------------------------------- settings

    def set_setting(self, key: str, value: str) -> None:
        self.conn.execute(
            """
            INSERT INTO app_settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )
        self.conn.commit()

    def get_setting(self, key: str, default: str = "") -> str:
        row = self.conn.execute(
            "SELECT value FROM app_settings WHERE key = ?", (key,)
        ).fetchone()
        if row is None:
            return default
        return str(row["value"])
