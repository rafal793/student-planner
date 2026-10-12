import pytest
from unittest.mock import MagicMock, patch

SAMPLE_SUBJECT_ROW = {
    'id': 1,
    'name': 'WDI',
    'teacher': 'Rafał Kawa',
    'status': 'atrisk',
    'grading_rules': 'Egzamin + projekt',
    'current_absences': 8,
    'max_absences': 10,
    'max_activity_points': 15.0,
    'max_colloquium_points': 20.0,
    'note': '',
}

@pytest.fixture
def mock_app():
    app = MagicMock()
    app.language = 'pl'
    widget_colors = app.theme.WidgetColors
    widget_colors.SCROLLBAR_COLOR_INACTIVE = '#666666'
    widget_colors.PROGRESSBAR_LOW = '#62c57b'
    widget_colors.PROGRESSBAR_MID = '#f1c40f'
    widget_colors.PROGRESSBAR_HIGH = '#e74c3c'
    app.theme.DefaultColors.DEFAULT_WHITE = '#ffffff'
    return app

@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.get_all_subjects.return_value = []
    return repo

@pytest.fixture
def rules_screen(mock_app, mock_repo):
    with patch('kivy.lang.Builder.load_file'):
        from views.rules_repository.rules_repository import RulesRepositoryScreen

        screen = RulesRepositoryScreen()
        screen.app = mock_app
        screen.repo = mock_repo
        screen.ids['rules_container'] = MagicMock()
        return screen

def test_populate_cards_calls_repo(rules_screen, mock_repo):
    mock_repo.get_all_subjects.return_value = [SAMPLE_SUBJECT_ROW]

    with patch('views.rules_repository.rules_repository.SubjectCard') as mock_card:
        rules_screen.populate_cards()

    mock_repo.get_all_subjects.assert_called_once()
    rules_screen.ids['rules_container'].clear_widgets.assert_called_once()
    mock_card.from_subject_data.assert_called_once()
    rules_screen.ids['rules_container'].add_widget.assert_called_once()

def test_populate_cards_creates_one_card_per_subject(rules_screen, mock_repo):
    mock_repo.get_all_subjects.return_value = [
        SAMPLE_SUBJECT_ROW,
        {**SAMPLE_SUBJECT_ROW, 'id': 2, 'name': 'ASD'},
    ]

    with patch('views.rules_repository.rules_repository.SubjectCard') as mock_card:
        rules_screen.populate_cards()

    assert mock_card.from_subject_data.call_count == 2
    assert rules_screen.ids['rules_container'].add_widget.call_count == 2

def test_populate_cards_empty_list(rules_screen, mock_repo):
    mock_repo.get_all_subjects.return_value = []

    with patch('views.rules_repository.rules_repository.SubjectCard') as mock_card:
        rules_screen.populate_cards()

    mock_card.from_subject_data.assert_not_called()
    rules_screen.ids['rules_container'].add_widget.assert_not_called()

def test_subject_card_from_subject_data_maps_fields(mock_app):
    from models.subject_data import SubjectData
    from views.rules_repository.rules_repository import SubjectCard

    subject = SubjectData.create_from_db_dict(SAMPLE_SUBJECT_ROW)
    with patch.object(SubjectCard, 'on_kv_post'):
        card = SubjectCard.from_subject_data(subject, mock_app)

    assert card.title == 'WDI'
    assert card.teacher == 'Rafał Kawa'
    assert card.status == 'atrisk'
    assert card.rules == 'Egzamin + projekt'
    assert card.absences == '8 / 10'
    assert card.current_absences == 8
    assert card.max_absences_count == 10
    assert card.app is mock_app

def test_subject_card_from_subject_data_empty_optional_fields(mock_app):
    from models.subject_data import SubjectData
    from views.rules_repository.rules_repository import SubjectCard

    row = {
        'id': 3,
        'name': 'Fizyka',
        'teacher': None,
        'status': 'inprogress',
        'grading_rules': '',
        'current_absences': 0,
        'max_absences': 0,
    }
    subject = SubjectData.create_from_db_dict(row)
    with patch.object(SubjectCard, 'on_kv_post'):
        card = SubjectCard.from_subject_data(subject, mock_app)

    assert card.teacher == 'Brak'
    assert card.rules == ''
    assert card.absences == '0 / 0'
    assert card.current_absences == 0
    assert card.max_absences_count == 0

def test_populate_cards_passes_mapped_subject_to_card(rules_screen, mock_repo, mock_app):
    mock_repo.get_all_subjects.return_value = [SAMPLE_SUBJECT_ROW]

    with patch('views.rules_repository.rules_repository.SubjectCard') as mock_card:
        card_instance = MagicMock()
        mock_card.from_subject_data.return_value = card_instance
        rules_screen.populate_cards()

    subject_arg = mock_card.from_subject_data.call_args[0][0]
    app_arg = mock_card.from_subject_data.call_args[0][1]

    assert subject_arg.title == 'WDI'
    assert subject_arg.teacher == 'Rafał Kawa'
    assert subject_arg.status == 'atrisk'
    assert subject_arg.conditions == 'Egzamin + projekt'
    assert subject_arg.absences == 8
    assert subject_arg.max_absences == 10
    assert app_arg is mock_app
    rules_screen.ids['rules_container'].add_widget.assert_called_once_with(card_instance)
