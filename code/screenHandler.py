"""Screen registry — import and register app screens here."""

KV_FILE_PATH = "views"

from views.my_subjects.my_subjects import MySubjectsScreen
from views.subject_details.subject_details import SubjectDetailsScreen
from views.calendar.start_calendar import StartCalendar
from views.exams_colloquiums.exams_colloquiums import ExamsAndColloquiumsScreen
from views.add_subject.add_subject import AddSubjectScreen
from views.progress_tracker.progress_tracker import ProgressTrackerScreen, ProgressCard, PointControlRow
from views.rules_repository.rules_repository import RulesRepositoryScreen

SCREENS = {
    'mySubjects': {
        'class': MySubjectsScreen,
        'kv': f'{KV_FILE_PATH}/my_subjects/my_subjects.kv',
    },
    'subjectDetails': {
        'class': SubjectDetailsScreen,
        'kv': f'{KV_FILE_PATH}/subject_details/subject_details.kv',
    },
    'calendar': {
        'class': StartCalendar,
        'kv': f'{KV_FILE_PATH}/calendar/home.kv',
    },
    'add_subject': {
        'class': AddSubjectScreen,
        'kv': f'{KV_FILE_PATH}/add_subject/add_subject.kv',
    },
    'exams_tests': {
        'class': ExamsAndColloquiumsScreen,
        'kv': f'{KV_FILE_PATH}/exams_colloquiums/exams_colloquiums.kv',
    },
    'rules_repository': {
        'class': RulesRepositoryScreen,
        'kv': f'{KV_FILE_PATH}/rules_repository/rules_repository.kv',
    },
    'progress_tracker': {
        'class': ProgressTrackerScreen,
        'kv': f'{KV_FILE_PATH}/progress_tracker/progress_tracker.kv',
    },
}
