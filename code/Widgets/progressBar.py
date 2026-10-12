from abc import ABC , abstractmethod
from enum import Enum, auto

class ProgressBarState(Enum):
    NORMAL = auto()
    COMPLETED = auto()
    DISABLED = auto()
    LOADING = auto()

class ProgressBarStyle:
    def __init__(
        self,
        bg_color,
        fill_color,
        text_color,
        fill_color_low=None,
        fill_color_mid=None,
        fill_color_high=None,
        invert_fill_colors=False,
    ):
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.text_color = text_color
        self.fill_color_low = fill_color_low
        self.fill_color_mid = fill_color_mid
        self.fill_color_high = fill_color_high
        self.invert_fill_colors = invert_fill_colors

    @classmethod
    def with_theme_gradient(cls, theme, *, inverted=False):
        from kivy.utils import get_color_from_hex

        widget_colors = theme.WidgetColors
        return cls(
            bg_color=get_color_from_hex(widget_colors.SCROLLBAR_COLOR_INACTIVE),
            fill_color=get_color_from_hex(widget_colors.PROGRESSBAR_LOW),
            text_color=get_color_from_hex(theme.DefaultColors.DEFAULT_WHITE),
            fill_color_low=get_color_from_hex(widget_colors.PROGRESSBAR_LOW),
            fill_color_mid=get_color_from_hex(widget_colors.PROGRESSBAR_MID),
            fill_color_high=get_color_from_hex(widget_colors.PROGRESSBAR_HIGH),
            invert_fill_colors=inverted,
        )

    def resolve_fill_color(self, value: int, max_value: int):
        if self.fill_color_low is None:
            return self.fill_color

        ratio = value / max_value if max_value > 0 else 0
        if ratio < 0.34:
            bucket = 'low'
        elif ratio < 0.67:
            bucket = 'mid'
        else:
            bucket = 'high'

        if self.invert_fill_colors:
            bucket = {'low': 'high', 'mid': 'mid', 'high': 'low'}[bucket]

        if bucket == 'low':
            return self.fill_color_low
        if bucket == 'mid':
            return self.fill_color_mid
        return self.fill_color_high

class ProgressBarBackend(ABC):
    @abstractmethod
    def create(self,value: int, max_value: int, style: ProgressBarStyle):
        # stworz progress bar
        pass
    @abstractmethod
    def setValue(self, value: int, max_value: int, fill_color=None):
        # zmieniasz value
        pass

class ProgressBar:
    def __init__ (self,value:int, max_value: int, backend: ProgressBarBackend,style: ProgressBarStyle):
        self.value=value
        self.max_value=max_value
        self._backend=backend
        self.style=style
        self._state=ProgressBarState.NORMAL
        self._validate_values()

    def render(self):
        return self._backend.create(self.value, self.max_value, self.style)
    
    def updateValue(self, new_value: int):
        self.value = new_value
        self._validate_values()
        if self.value == self.max_value:
            self._state=ProgressBarState.COMPLETED
        else:
            self._state=ProgressBarState.NORMAL
        fill_color = self.style.resolve_fill_color(self.value, self.max_value)
        self._backend.setValue(self.value, self.max_value, fill_color)

    def getPercentage(self):
        return int(self.value*100/self.max_value)
    
    def _validate_values(self):
        if self.max_value<=0:
            raise ValueError("max_value must be greater than 0")
        if self.value<0:
            self.value=0
        if self.value>self.max_value:
            self.value=self.max_value