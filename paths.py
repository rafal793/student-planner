import os
import sys
from pathlib import Path
from kivy.resources import resource_add_path


def resource_path(relative_path: str) -> str:
    """Zwraca bezwzględną ścieżkę do zasobu."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = Path(__file__).resolve().parent
    return str(Path(base_path) / relative_path)


def configure_kivy_resources() -> None:
    """Dodaje katalogi z assetami do ścieżek Kivy."""
    base_dir = Path(__file__).resolve().parent
    resource_add_path(str(base_dir))
    resource_add_path(str(base_dir / "Images"))
    resource_add_path(str(base_dir / "Style"))
    resource_add_path(str(base_dir / "views"))


def get_db_path() -> str:
    """Zwraca ścieżkę do pliku bazy bezpośrednio w katalogu projektu."""
    return str(Path(__file__).resolve().parent / "student_planner.db")
