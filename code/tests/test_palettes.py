import pytest

from style.Colors import ThemeManager
from style.palettes import PALETTE_DEFAULT, PALETTE_MIDNIGHT


def test_default_palette_matches_legacy_colors():
    theme = ThemeManager.with_palette('default')
    assert theme.UiColors.SECONDARY_BG_COLOR == PALETTE_DEFAULT['UiColors']['SECONDARY_BG_COLOR']
    assert theme.CalendarColors.LESSON_BG_COLOR == '#86a6c1'


def test_midnight_palette_applies_distinct_colors():
    theme = ThemeManager.with_palette('midnight')
    assert theme.palette_name == 'midnight'
    assert theme.UiColors.MAIN_BG_COLOR == '#1a1b26'
    assert theme.UiColors.SECONDARY_BG_COLOR == '#24283b'
    assert theme.CalendarColors.EXAM_BG_COLOR == '#f7768e'
    assert theme.DefaultColors.DEFAULT_WHITE == '#c0caf5'


def test_apply_palette_switches_theme():
    theme = ThemeManager()
    assert theme.UiColors.MAIN_BG_COLOR == '#2c2c2e'

    theme.apply_palette('midnight')
    assert theme.palette_name == 'midnight'
    assert theme.UiColors.MAIN_BG_COLOR == '#1a1b26'

    theme.apply_palette('default')
    assert theme.palette_name == 'default'
    assert theme.UiColors.MAIN_BG_COLOR == '#2c2c2e'


def test_unknown_palette_raises():
    theme = ThemeManager()
    with pytest.raises(ValueError, match='Unknown palette'):
        theme.apply_palette('neon')


def test_available_palettes():
    assert ThemeManager.available_palettes() == ('default', 'midnight', 'rose')


def test_rose_palette_standard_ui_button():
    theme = ThemeManager.with_palette('rose')
    assert theme.palette_name == 'rose'
    assert theme.ButtonColors.STANDARD_UI_BUTTON_BG_COLOR == '#d16ba5'
    assert theme.UiColors.SECONDARY_BG_COLOR == '#3d2433'


def test_default_standard_ui_button_matches_legacy_blue():
    theme = ThemeManager.with_palette('default')
    assert theme.ButtonColors.STANDARD_UI_BUTTON_BG_COLOR == '#2e588c'
    assert theme.ButtonColors.STANDARD_UI_BUTTON_TEXT_COLOR == '#ffffff'


def test_palette_cycle_order():
    palettes = ThemeManager.available_palettes()
    current = palettes[0]
    visited = {current}

    for _ in range(len(palettes) - 1):
        idx = palettes.index(current)
        current = palettes[(idx + 1) % len(palettes)]
        visited.add(current)

    assert visited == set(palettes)


def test_palette_logo_sources():
    assert ThemeManager.with_palette('default').UiColors.LOGO_SOURCE == 'images/logo_default.png'
    assert ThemeManager.with_palette('midnight').UiColors.LOGO_SOURCE == 'images/logo_theme_midnight.png'
    assert ThemeManager.with_palette('rose').UiColors.LOGO_SOURCE == 'images/logo_theme_rose.png'
