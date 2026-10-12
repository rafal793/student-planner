from abc import ABC, abstractmethod
from typing import Dict
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle

#PLACEHOLDER
def openCalendar():

    return "2026-05-19"

class FormStyle:

    def __init__(
        self,
        bg_color,
        text_color,
        button_color,
        field_background_color,
        field_text_color
    ):

        self.bg_color = bg_color
        self.text_color = text_color
        self.button_color = button_color

        self.field_background_color = field_background_color
        self.field_text_color = field_text_color

class FormField:

    def __init__(
        self,
        name,
        width=300,
        use_calendar=False
    ):

        self.name = name
        self.width = width

        
        self.use_calendar = use_calendar

class FormBackend(ABC):

    @abstractmethod
    def create(
        self,
        fields,
        style,
        submit_callback
    ):
        pass

    @abstractmethod
    def getValues(self):
        pass

class KivyFormBackend(FormBackend):

    def __init__(self):

        self.layout = None
        self.inputs = {}

    def create(
        self,
        fields,
        style,
        submit_callback
    ):

        self.layout = BoxLayout(
            orientation="vertical",
            spacing=10,
            padding=20
        )

        

        with self.layout.canvas.before:

            Color(*style.bg_color)

            self.bg_rect = Rectangle(
                pos=self.layout.pos,
                size=self.layout.size
            )

        self.layout.bind(
            pos=self._update_bg,
            size=self._update_bg
        )

        

        for field in fields:

            

            label = Label(

            text=field.name,

            size_hint=(1, None),

            height=30,

            color=style.text_color,

            halign="left",
            valign="middle"
            )

            label.bind(
                size=lambda instance, value:
                setattr(instance, "text_size", value)
            )

            self.layout.add_widget(label)

            

            row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=40,
                spacing=5
            )

            

            text_input = TextInput(

                multiline=False,

                size_hint=(None, None),

                width=field.width,
                height=40,

                background_color=style.field_background_color,

                foreground_color=style.field_text_color
            )

            self.inputs[field.name] = text_input

            row.add_widget(text_input)

            

            if field.use_calendar:

                calendar_button = Button(

                    text="K",

                    size_hint=(None, None),

                    width=40,
                    height=40
                )

                calendar_button.bind(
                    on_press=lambda instance,
                    inp=text_input:
                    self._select_date(inp)
                )

                row.add_widget(calendar_button)

            self.layout.add_widget(row)

        

        submit_button = Button(

            text="Zatwierdź",

            size_hint_y=None,

            height=50,

            background_color=style.button_color
        )

        submit_button.bind(
            on_press=lambda instance:
            self._submit(submit_callback)
        )

        self.layout.add_widget(submit_button)

        return self.layout

    

    def _select_date(self, text_input):

        selected_date = openCalendar()

        text_input.text = selected_date

    
    

    def _submit(self, submit_callback):

        values = self.getValues()

        
        submit_callback(values)

        
        self.clearFields()

    

    def clearFields(self):

        for text_input in self.inputs.values():

            text_input.text = ""

    

    def getValues(self):

        values = {}

        for field, text_input in self.inputs.items():

            values[field] = text_input.text

        return values

    

    def _update_bg(self, instance, value):

        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

class FormWidget:

    def __init__(
        self,
        fields,
        backend,
        style
    ):

        self.fields = fields
        self._backend = backend
        self.style = style

    def render(self):

        return self._backend.create(
            self.fields,
            self.style,
            self._on_submit
        )

    def _on_submit(self, values):

        print("Wysłane dane:\n")

        for key, value in values.items():

            print(f"{key}: {value}")
