import sys
from pathlib import Path
from kivy.resources import resource_add_path

PROJECT_ROOT = Path(__file__).resolve().parent
CODE_DIR = PROJECT_ROOT / "code"

# Packages live under code/ (database, Widgets, KivyWidgets, views, style, ...)
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))


def resource_path(relative_path: str) -> str:
    """Zwraca bezwzględną ścieżkę do zasobu (root projektu lub code/)."""
    try:
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        base_path = PROJECT_ROOT

    relative = Path(relative_path)
    direct = base_path / relative
    if direct.exists():
        return str(direct)

    under_code = base_path / "code" / relative
    if under_code.exists():
        return str(under_code)

    # Domyślnie: jeśli ścieżka już zaczyna się od code/, zostaw; inaczej preferuj code/
    if relative.parts and relative.parts[0] == "code":
        return str(direct)
    return str(under_code)


def configure_kivy_resources() -> None:
    """Dodaje katalogi z assetami do ścieżek Kivy."""
    resource_add_path(str(PROJECT_ROOT))
    resource_add_path(str(CODE_DIR))
    resource_add_path(str(CODE_DIR / "images"))
    resource_add_path(str(CODE_DIR / "style"))
    resource_add_path(str(CODE_DIR / "views"))


def get_db_path() -> str:
    """Zwraca ścieżkę do pliku bazy w katalogu data/."""
    data_dir = PROJECT_ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return str(data_dir / "student_planner.db")
