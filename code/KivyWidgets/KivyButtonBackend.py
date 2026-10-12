
from kivy.uix.button import ButtonBehavior
from kivy.uix.togglebutton import ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty , BooleanProperty , StringProperty
from kivy.core.window import Window
from style.ButtonStyle import ButtonStyle
from style.ButtonState import ButtonState

class CustomButtonBase(BoxLayout):
    style = ObjectProperty(None)
    btn_state = ObjectProperty(ButtonState.NORMAL)
    hovered = BooleanProperty(False)

    text =  StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return
        
        local_x, local_y = self.to_widget(*pos)
        inside = self.collide_point(local_x, local_y)
        if self.hovered != inside:
            self.hovered = inside
            self._update_logic_state()

    def on_state(self, instance, value):
        self._update_logic_state()

    def on_disabled(self, instance, value):
        self._update_logic_state()

    def _update_logic_state(self):
        if self.disabled:
            self.btn_state = ButtonState.DISABLED
        elif self.state == 'down':
            self.btn_state = ButtonState.PRESSED
        elif getattr(self, 'hovered', False):
            self.btn_state = ButtonState.HOVER
        else:
            self.btn_state = ButtonState.NORMAL

class CustomButtonWidget(ButtonBehavior, CustomButtonBase):
    pass
class CustomToggleButtonWidget(ToggleButtonBehavior, CustomButtonBase):
    pass