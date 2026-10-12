from kivy.event import EventDispatcher
from kivy.properties import StringProperty , NumericProperty

class SubjectData(EventDispatcher):
    id = NumericProperty(allownone=False)
    title = StringProperty("")
    teacher = StringProperty(None, allownone=True)
    note = StringProperty(None , allownone=True)

    status = StringProperty("completed")
    absences = NumericProperty(1)
    max_absences = NumericProperty(2)
    conditions = StringProperty("bleble" , allownone=True)
    max_pluses = NumericProperty(10.0)
    max_colloquium_pluses = NumericProperty(0.0)
    current_pluses = NumericProperty(0)
    current_colloquium_pluses = NumericProperty(0)

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        
    @classmethod
    def create_from_db_dict(cls, db_dict: dict):
  
        
        instance = cls()
        instance.id = db_dict.get("id")
        instance.title = db_dict.get("name", "Brak nazwy")
        instance.teacher=db_dict.get("teacher", "Nieznany")
        instance.note=db_dict.get("note") or ""
        instance.status = db_dict.get("status", "inprogress")
        instance.absences = db_dict.get("current_absences", 0)
        instance.max_absences = db_dict.get("max_absences", 0)
        instance.conditions = db_dict.get("grading_rules", "")
        instance.max_pluses = float(db_dict.get("max_activity_points", 0.0))
        instance.max_colloquium_pluses = float(db_dict.get("max_colloquium_points", 0.0))
        instance.current_pluses = int(db_dict.get("current_activity_points") or 0)
        instance.current_colloquium_pluses = int(db_dict.get("current_colloquium_points") or 0)

        return instance