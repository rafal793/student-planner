import pytest
from unittest.mock import MagicMock, patch

SUBJECT_ROW = {
    'id': 1,
    'name': 'IO',
    'teacher': 'Dr Kowalski',
    'status': 'inprogress',
    'grading_rules': '',
    'current_absences': 0,
    'max_absences': 0,
    'max_activity_points': 10,
    'current_activity_points': 5,
    'max_colloquium_points': 20,
    'current_colloquium_points': 10,
}

@pytest.fixture
def mock_app():
    return MagicMock()

@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.get_all_subjects.return_value = []
    return repo

@pytest.fixture
def tracker_screen(mock_app, mock_repo):
    with patch('kivy.lang.Builder.load_file'):
        from views.progress_tracker.progress_tracker import ProgressTrackerScreen

        screen = ProgressTrackerScreen()
        screen.app = mock_app
        screen.repo = mock_repo
        screen.ids['cards_container'] = MagicMock()
        return screen

def test_load_cards_calls_repo(tracker_screen, mock_repo):
    mock_repo.get_all_subjects.return_value = [SUBJECT_ROW]

    with patch('views.progress_tracker.progress_tracker.ProgressCard') as mock_card:
        tracker_screen.load_cards()

    mock_repo.ensure_progress_defaults.assert_called_once()
    mock_repo.get_all_subjects.assert_called_once()
    tracker_screen.ids['cards_container'].clear_widgets.assert_called_once()
    mock_card.from_subject_data.assert_called_once()
    tracker_screen.ids['cards_container'].add_widget.assert_called_once()

def test_load_cards_creates_one_card_per_subject(tracker_screen, mock_repo):
    mock_repo.get_all_subjects.return_value = [
        SUBJECT_ROW,
        {**SUBJECT_ROW, 'id': 2, 'name': 'ASD'},
    ]

    with patch('views.progress_tracker.progress_tracker.ProgressCard') as mock_card:
        tracker_screen.load_cards()

    assert mock_card.from_subject_data.call_count == 2

def test_load_cards_empty_list(tracker_screen, mock_repo):
    with patch('views.progress_tracker.progress_tracker.ProgressCard') as mock_card:
        tracker_screen.load_cards()

    mock_card.from_subject_data.assert_not_called()
    tracker_screen.ids['cards_container'].add_widget.assert_not_called()
