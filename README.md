# Student Planner

Desktop app that helps students manage classes, exams, grading rules, and progress in one place.

Built as a university Software Engineering project by a **4-person team**. I was the **team lead** — responsible for architecture decisions, delivery, and the final product.

## Features

- Weekly calendar with class blocks, exams, and colloquiums (color-coded, sorted by time)
- Add subjects with schedule, grading rules, absence limits, and term dates
- Subject details: status, absences, and permanent notes
- Daily notes attached to calendar events
- Rules repository with absence progress bars
- Progress tracker for activity / colloquium points
- Session countdown and upcoming-event notifications in the top bar
- Polish / English UI switch without restart
- Offline SQLite storage + sample data on first launch

## Tech Stack

Python, Kivy, SQLite, pytest

## Project structure

```text
code/            application source (UI, database, tests)
data/            local SQLite database
documentation/   SRS, diagrams, install guide
scripts/         install and build helpers
app.py           entry point
```

## Quick start

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Or use the helpers in `scripts/`.

Full setup notes: [`documentation/installation_instructions.txt`](documentation/installation_instructions.txt)

## Tests

```bash
PYTHONPATH=code python -m pytest code/tests/ -q
```

## Demo data

On first run the app fills an empty database with sample subjects so the calendar is not empty.  
Delete those subjects in the UI and add your own to use it as a personal planner.

---

More docs (SRS, diagrams, test notes) are in [`documentation/`](documentation/).
