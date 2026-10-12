from Widgets.progressBar import ProgressBarBackend, ProgressBarState, ProgressBarStyle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle

class ThickProgressBar(Widget):
    def __init__(self, max_value, value, bg_color, fill_color, **kwargs):
        super().__init__(**kwargs)
        self.max_value = max_value
        self.value = value
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.size_hint_y = None
        self.height = dp(14) 
        
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(rgba=self.bg_color) 
            RoundedRectangle(pos=self.pos, size=self.size, radius=[self.height / 2])
            
            Color(rgba=self.fill_color)
            fill_width = self.width * (self.value / self.max_value) if self.max_value > 0 else 0
            RoundedRectangle(pos=self.pos, size=(fill_width, self.height), radius=[self.height / 2])

    def update_values(self, value, max_value, fill_color=None):
        self.value = value
        self.max_value = max_value
        if fill_color:
            self.fill_color = fill_color
        self.update_canvas()

class KivyProgressBarBackend(ProgressBarBackend):
    def __init__(self):
        self.layout = None
        self.progress_bar = None

    def create(self, value: int, max_value: int, style: ProgressBarStyle):
        self.layout = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(15))
        fill_color = style.resolve_fill_color(value, max_value)

        self.progress_bar = ThickProgressBar(
            max_value=max_value,
            value=value,
            bg_color=style.bg_color,
            fill_color=fill_color,
        )
        self.layout.add_widget(self.progress_bar)

        return self.layout
    
    def setValue(self, value: int, max_value: int, fill_color=None):
        if self.progress_bar is None:
            return
        self.progress_bar.update_values(value, max_value, fill_color)