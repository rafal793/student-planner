from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty

from KivyWidgets.KivyBrickBackend import DashboardBrick

from models.subject_data import SubjectData


class SubjectGreen(DashboardBrick):
    pass
class SubjectRed(DashboardBrick):
    pass
class SubjectWhite(DashboardBrick):
    pass
class SubjectBlack(DashboardBrick):
    pass

class MySubjectsScreen(Screen):
    repo = ObjectProperty(None)
    app = ObjectProperty(None)

    def on_pre_enter(self, *args):
        self.ids.grid_przedmiotow.clear_widgets()

        rows = self.repo.get_all_subjects()
        
        # 3. Pętla budująca kafelki
        for row in rows:

            przedmiot = SubjectData.create_from_db_dict(row)
  
            if przedmiot.status == "completed":
                nowy_kafelek = SubjectGreen(subject_obj=przedmiot)
            elif przedmiot.status == "inprogress":
                nowy_kafelek = SubjectWhite(subject_obj=przedmiot)
            elif przedmiot.status == "atrisk":
                nowy_kafelek = SubjectRed(subject_obj=przedmiot)
            elif przedmiot.status == "failed":
                nowy_kafelek = SubjectBlack(subject_obj=przedmiot)
            else:
                print(f"expected status value but got: {przedmiot.status}")
                raise ValueError()
    
            self.ids.grid_przedmiotow.add_widget(nowy_kafelek)

