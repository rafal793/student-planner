import calendar
from datetime import date
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.properties import ColorProperty
from kivy.utils import get_color_from_hex
from kivy.app import App

from Widgets.datePicker import DatePickerBackend, DatePickerStyle

# ==========================================
# DEFINICJE KLAS PRZYCISKÓW (PYTHON + KIVY)
# ==========================================

class RoundedDateButton(Button):
    bg_color = ColorProperty(get_color_from_hex("#2e588c"))

class RoundedNavBtn(Button):
    bg_color = ColorProperty(get_color_from_hex("#2e588c"))

Builder.load_string("""
<RoundedDateButton>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    
    canvas.before:
        Color:
            rgba: self.bg_color if self.state == 'normal' else [self.bg_color[0]*0.7, self.bg_color[1]*0.7, self.bg_color[2]*0.7, 1]
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [8]

<RoundedNavBtn>:
    background_normal: ""
    background_down: ""
    background_color: 0, 0, 0, 0
    
    canvas.before:
        Color:
            rgba: self.bg_color if self.state == 'normal' else [self.bg_color[0]*0.7, self.bg_color[1]*0.7, self.bg_color[2]*0.7, 1]
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [5]
""")

# ==========================================
# GŁÓWNA KLASA BACKENDU
# ==========================================
class KivyDatePickerBackend(DatePickerBackend):
    def __init__(self):
        self.root = None
        self.month_label = None
        self.calendar_layout = None
        self.confirm_button = None

        self.selected_date = None
        self.confirmed_date = None
        self.current_year = None
        self.current_month = None
        self.style = None

    def create(self, selected_date: date, style: DatePickerStyle):
        self.selected_date = selected_date
        self.style = style 
        
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
        
        self.root = BoxLayout(
            orientation="vertical",
            spacing=15,
            padding=20
        )
        
        header = BoxLayout(
            size_hint_y=None,
            height=40,
            spacing=5
        )
        
        prev_year_button = RoundedNavBtn(text="<<", size_hint_x=0.15)
        prev_month_button = RoundedNavBtn(text="<", size_hint_x=0.15)
        next_month_button = RoundedNavBtn(text=">", size_hint_x=0.15)
        next_year_button = RoundedNavBtn(text=">>", size_hint_x=0.15)
        
        self.month_label = Label(size_hint_x=0.4, bold=True)
        
        prev_year_button.bind(on_press=self.previousYear)
        prev_month_button.bind(on_press=self.previousMonth)
        next_month_button.bind(on_press=self.nextMonth)
        next_year_button.bind(on_press=self.nextYear)

        header.add_widget(prev_year_button)
        header.add_widget(prev_month_button)
        header.add_widget(self.month_label)
        header.add_widget(next_month_button)
        header.add_widget(next_year_button)

        self.calendar_layout = GridLayout(cols=7, spacing=5)
        
        self.confirm_button = RoundedDateButton(
            text="Zatwierdź",
            size_hint_y=None,
            height=45,
            bg_color=get_color_from_hex("#4b9e5e")
        )
        self.confirm_button.bind(on_press=self.confirmDate)
        
        self.root.add_widget(header)
        self.root.add_widget(self.calendar_layout)
        self.root.add_widget(self.confirm_button)
        
        self.refreshCalendar()
        return self.root
    
    def setDate(self, selected_date: date):
        self.selected_date = selected_date
        self.refreshCalendar()

    def openCalendar(self, instance=None):
        return self.root
    

    def refreshCalendar(self):
        app = App.get_running_app()
        lang = app.language
        if hasattr(self, 'title_label'):
            self.title_label.text = app.translations[lang].get("calendar_title", "Wybierz datę sesji")
        
        months_names = app.translations[lang].get("calendar_months", [])
        days_names = app.translations[lang].get("calendar_days", [])
        confirm_text = app.translations[lang].get("confirm_button", "Confirm")
        
        if self.confirm_button:
            self.confirm_button.text = confirm_text

        self.calendar_layout.clear_widgets()
        
        if months_names:
            self.month_label.text = f"{months_names[self.current_month - 1]} {self.current_year}"
        
        for name in days_names:
            self.calendar_layout.add_widget(Label(text=name, bold=True, color=get_color_from_hex("#aaaaaa")))
            
        month_days = calendar.monthcalendar(self.current_year, self.current_month)
        today = date.today()
        
        c_base = get_color_from_hex("#2e588c")       
        c_selected = get_color_from_hex("#0b3d91")   
        c_today = get_color_from_hex("#4a76a8")      
        c_text = [1, 1, 1, 1]                        

        for week in month_days:
            for day in week:
                if day == 0:
                    self.calendar_layout.add_widget(Label(text=""))
                else:
                    current_date = date(self.current_year, self.current_month, day)
                    
                    day_button = RoundedDateButton(text=str(day))
                    day_button.color = c_text
                    
                    if self.selected_date == current_date:
                        day_button.bg_color = c_selected
                    elif today == current_date:
                        day_button.bg_color = c_today
                    else:
                        day_button.bg_color = c_base
                        
                    day_button.bind(on_press=self.selectDay)
                    self.calendar_layout.add_widget(day_button)
                    
    def selectDay(self, instance):
        day = int(instance.text)
        self.selected_date = date(
            self.current_year,
            self.current_month,
            day
        )
        self.refreshCalendar()

    def confirmDate(self, instance):
        print("Zatwierdzona data:", self.selected_date)

    def previousMonth(self, instance):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refreshCalendar()

    def nextMonth(self, instance):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.refreshCalendar()

    def previousYear(self, instance):
        self.current_year -= 1
        self.refreshCalendar()

    def nextYear(self, instance):
        self.current_year += 1
        self.refreshCalendar()