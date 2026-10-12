from KivyWidgets.KivyButtonBackend import CustomButtonWidget , CustomButtonBase
from kivy.uix.button import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty , StringProperty , BooleanProperty

class DashboardBrick2( CustomButtonWidget, BoxLayout ):
    subject_obj = ObjectProperty(None)
     
class DashboardBrick(ButtonBehavior,CustomButtonBase ):
    subject_obj = ObjectProperty(None)

class BrickWidget(ButtonBehavior,CustomButtonBase):
    info_text = StringProperty()
    title_text = StringProperty()
    has_note = BooleanProperty(False)
class BlueBrick(BrickWidget):
    pass

class CalendarEventBrick(ButtonBehavior, CustomButtonBase):
    info_text = StringProperty()
    title_text = StringProperty()
    overlay_label = StringProperty()
    has_note = BooleanProperty(False)
    interactive = BooleanProperty(True)

    def on_mouse_pos(self, window, pos):
        if not self.interactive:
            return
        super().on_mouse_pos(window, pos)
