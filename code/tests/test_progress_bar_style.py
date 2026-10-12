import pytest

from unittest.mock import MagicMock, patch
from models.subject_data import SubjectData
from Widgets.progressBar import ProgressBarStyle


def test_progress_bar_style_inverted_colors():
    style = ProgressBarStyle(
        bg_color=(0.2, 0.2, 0.2, 1),
        fill_color=(0, 0, 1, 1),
        text_color=(1, 1, 1, 1),
        fill_color_low=(0, 1, 0, 1),
        fill_color_mid=(1, 1, 0, 1),
        fill_color_high=(1, 0, 0, 1),
        invert_fill_colors=True,
    )

    assert style.resolve_fill_color(10, 100) == (1, 0, 0, 1)
    assert style.resolve_fill_color(50, 100) == (1, 1, 0, 1)
    assert style.resolve_fill_color(80, 100) == (0, 1, 0, 1)


def test_progress_bar_style_normal_colors():
    style = ProgressBarStyle(
        bg_color=(0.2, 0.2, 0.2, 1),
        fill_color=(0, 0, 1, 1),
        text_color=(1, 1, 1, 1),
        fill_color_low=(0, 1, 0, 1),
        fill_color_mid=(1, 1, 0, 1),
        fill_color_high=(1, 0, 0, 1),
    )

    assert style.resolve_fill_color(10, 100) == (0, 1, 0, 1)
    assert style.resolve_fill_color(80, 100) == (1, 0, 0, 1)


def test_kivy_progress_bar_backend_honors_contract():
    from KivyWidgets.kivyProgressBarBackend import KivyProgressBarBackend
    from Widgets.progressBar import ProgressBarBackend

    assert issubclass(KivyProgressBarBackend, ProgressBarBackend)
