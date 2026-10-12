import pytest
from unittest.mock import MagicMock, patch

from models.subject_data import SubjectData
from views.progress_tracker.progress_tracker import ProgressCard

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
def mock_card():
    app = MagicMock()
    app.translate.return_value = "Zdobyto {total} z {max} punktów ({percent}%)"
    app.language = "pl"

    repo = MagicMock()
    subject = SubjectData.create_from_db_dict(SUBJECT_ROW)

    with patch.object(ProgressCard, 'on_kv_post'):
        card = ProgressCard.from_subject_data(subject, repo, app)
        card.pb = MagicMock()
        card.update_texts()
        yield card

def test_initial_values(mock_card):
    assert mock_card.get_total() == 15
    assert mock_card.max_points == 30

def test_plus_minus_logic(mock_card):
    mock_card.change_pluses(1)
    assert mock_card.pluses_val == 6
    assert mock_card.get_total() == 16

def test_cannot_have_negative_points(mock_card):
    mock_card.change_pluses(-100)
    assert mock_card.pluses_val >= 0

def test_save_to_db(mock_card):
    mock_card.change_pluses(1)
    mock_card.repo.update_subject_progress.assert_called_with(1, 6, 10)

def test_points_text_formatting(mock_card):
    expected_text = "Zdobyto 15 z 30 punktów (50.0%)"
    assert mock_card.points_text == expected_text

def test_progress_card_from_subject_data():
    app = MagicMock()
    repo = MagicMock()
    subject = SubjectData.create_from_db_dict(SUBJECT_ROW)

    with patch.object(ProgressCard, 'on_kv_post'):
        card = ProgressCard.from_subject_data(subject, repo, app)

    assert card.subject_id == 1
    assert card.title_text == "IO (Dr Kowalski)"
    assert card.pluses_val == 5
    assert card.exam_val == 10
    assert card.max_points == 30
