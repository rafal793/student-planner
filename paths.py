import sys
from pathlib import Path
from kivy.resources import resource_add_path

PROJECT_ROOT = Path(__file__).resolve().parent
CODE_DIR = PROJECT_ROOT / "code"

if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

def resource_path(relative_path: str) -> str:
    """Absolute path to a project resource."""
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

    if relative.parts and relative.parts[0] == "code":
        return str(direct)
    return str(under_code)

def configure_kivy_resources() -> None:
    """Register asset folders for Kivy."""
    resource_add_path(str(PROJECT_ROOT))
    resource_add_path(str(CODE_DIR))
    resource_add_path(str(CODE_DIR / "images"))
    resource_add_path(str(CODE_DIR / "style"))
    resource_add_path(str(CODE_DIR / "views"))

def get_db_path() -> str:
    """Path to the SQLite file in data/."""
    data_dir = PROJECT_ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return str(data_dir / "student_planner.db")
