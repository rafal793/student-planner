from kivy.event import EventDispatcher
from kivy.properties import StringProperty, ObjectProperty
from style.palettes import PALETTES, DEFAULT_PALETTE_NAME

class UiColorsGroup(EventDispatcher):
    MAIN_BG_COLOR = StringProperty("#2c2c2e")
    SECONDARY_BG_COLOR = StringProperty("#0b3d91")
    
    TOP_BAR_BG_COLOR = StringProperty("#f8f9fa")
    TOP_BAR_TEXT_COLOR = StringProperty("#1565c0")
    NAV_BAR_BG_COLOR = StringProperty("#0b3d91")
    LOGO_SOURCE = StringProperty("images/logo_default.png")

    SCREEN_MAIN_TEXT_COLOR = "#ffffff"

    SCREEN_SECONDARY_TEXT_COLOR = "#ffffff"

class ButtonColorsGroup(EventDispatcher):
    TOP_BAR_BG_COLOR = StringProperty("#9ea6b3")
    TOP_BAR_TEXT_COLOR = StringProperty("#000000")
    NAV_BUTTON_BG_COLOR = StringProperty("#2e588c")
    NAV_BUTTON_TEXT_COLOR = StringProperty("#ffffff")
    NAV_BUTTON_PRESSED_BG_COLOR = StringProperty("#f8f9fa")
    NAV_BUTTON_PRESSED_TEXT_COLOR = StringProperty("#000000")

    SUBJECT_PLUS_BG_COLOR = StringProperty("#c0392b")
    SUBJECT_MINUS_BG_COLOR = StringProperty("#2980b9")
    SUBJECT_PLUS_TEXT_COLOR = StringProperty("#ffffff")
    SUBJECT_MINUS_TEXT_COLOR = StringProperty("#ffffff")

    TRACKER_PLUS_BG_COLOR = StringProperty("#5cb85c")
    TRACKER_PLUS_TEXT_COLOR = StringProperty("#ffffff")
    TRACKER_MINUS_BG_COLOR = StringProperty("#c94c4c")
    TRACKER_MINUS_TEXT_COLOR = StringProperty("#ffffff")

    REMOVE_BG_COLOR = StringProperty("#c0392b")
    REMOVE_TEXT_COLOR = StringProperty("#ffffff")

    STANDARD_UI_BUTTON_BG_COLOR = StringProperty("#2e588c")
    STANDARD_UI_BUTTON_TEXT_COLOR = StringProperty("#ffffff")
    STANDARD_UI_BUTTON_HOVER_BG_COLOR = StringProperty("#245073")
    STANDARD_UI_BUTTON_PRESSED_BG_COLOR = StringProperty("#1a3d5c")
    STANDARD_UI_BUTTON_PRESSED_TEXT_COLOR = StringProperty("#ffffff")

class SubjectColorsGroup(EventDispatcher):
    SUBJECT_BG_COLOR_COMPLETED = StringProperty("#62c57b")
    SUBJECT_BG_COLOR_ATRISK = StringProperty("#f28b82")
    SUBJECT_BG_COLOR_INPROGRESS = StringProperty("#d9d9d7")
    SUBJECT_BG_COLOR_FAILED = StringProperty("#272724")
    SUBJECT_TEXT_COLOR_BRIGHT = StringProperty("#ffffff")
    SUBJECT_TEXT_COLOR_DARK = StringProperty("#000000")

    

class WidgetsColorsGroup(EventDispatcher):
    FORM_TEXTINPUT_BG_COLOR = StringProperty("#322d2d") 
    FORM_TEXTINPUT_TEXT_COLOR = StringProperty("#ffffff")
    # FORM_TEXTINPUT_BG_COLOR = StringProperty("#ffffff") 
    # FORM_TEXTINPUT_TEXT_COLOR = StringProperty("#000001")
    FORM_TEXTINPUT_FOCUS_BORDER = StringProperty("#ffffff")

    SCROLLBAR_COLOR_ACTIVE = StringProperty("#888888")
    SCROLLBAR_COLOR_INACTIVE = StringProperty("#666666")

    PROGRESSBAR_LOW = StringProperty("#62c57b")
    PROGRESSBAR_MID = StringProperty("#f1c40f")
    PROGRESSBAR_HIGH = StringProperty("#e74c3c")

    PROGRESSCARD_BG_COLOR = StringProperty("#e0e0e0")
    PROGRESSCARD_TEXT_COLOR = StringProperty("#000000")
    PROGRESSCARD_SECONDARY_TEXT_COLOR = StringProperty("#333333")

class CalendarColorsGroup(EventDispatcher):
    LESSON_BG_COLOR = StringProperty("#86a6c1")
    LESSON_HOVER_BG_COLOR = StringProperty("#7092ad")
    EXAM_BG_COLOR = StringProperty("#e57373")
    EXAM_HOVER_BG_COLOR = StringProperty("#ef5350")
    COLOQUIUM_BG_COLOR = StringProperty("#ffb74d")
    COLOQUIUM_HOVER_BG_COLOR = StringProperty("#ffa726")

class DefaultColorsGroup(EventDispatcher):
    DEFAULT_WHITE = StringProperty("#ffffff")
    DEFAULT_BLACK = StringProperty("#000000")

class ThemeManager(EventDispatcher):
    UiColors = ObjectProperty(UiColorsGroup())
    ButtonColors = ObjectProperty(ButtonColorsGroup())
    SubjectColors = ObjectProperty(SubjectColorsGroup())
    CalendarColors = ObjectProperty(CalendarColorsGroup())
    DefaultColors = ObjectProperty(DefaultColorsGroup())
    WidgetColors = ObjectProperty(WidgetsColorsGroup())
    palette_name = StringProperty(DEFAULT_PALETTE_NAME)

    def __init__(self, **kwargs):
        palette = kwargs.pop('palette', DEFAULT_PALETTE_NAME)
        super().__init__(**kwargs)
        self.apply_palette(palette)

    @classmethod
    def with_palette(cls, palette_name: str = DEFAULT_PALETTE_NAME) -> 'ThemeManager':
        return cls(palette=palette_name)

    @staticmethod
    def available_palettes() -> tuple[str, ...]:
        return tuple(PALETTES.keys())

    def apply_palette(self, palette_name: str) -> None:
        if palette_name not in PALETTES:
            available = ', '.join(PALETTES.keys())
            raise ValueError(f"Unknown palette '{palette_name}'. Available: {available}")

        groups = {
            'UiColors': self.UiColors,
            'ButtonColors': self.ButtonColors,
            'SubjectColors': self.SubjectColors,
            'WidgetColors': self.WidgetColors,
            'CalendarColors': self.CalendarColors,
            'DefaultColors': self.DefaultColors,
        }

        for group_name, colors in PALETTES[palette_name].items():
            group = groups[group_name]
            for prop_name, value in colors.items():
                setattr(group, prop_name, value)

        self.palette_name = palette_name