import json
from utils.ParamList import ParameterList, NumParam, BoolParam, TextParam, ChoiceParam, ConstParam
from qt_material import list_themes, apply_stylesheet
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

import os

class Settings(ParameterList):
    def __init__(self, app: QApplication):
        self.app = app
        super().__init__([
            ChoiceParam("theme", value="blue", text="Color Theme", options=["amber","pink","blue","purple","cyan","red","lightgreen","teal","yellow"]),
            BoolParam("dark_mode", value=True, text="Dark Mode", render=False),
            BoolParam("invert_secondary", value=False, text="Invert Secondary Color"),
            # TextParam("font_size", value="12", text="Font Size", regex="^[0-9]+$")
            NumParam("font_size", value=12, text="Font Size", interval=(8, 24), step=1)
        ])

    @property
    def theme(self) -> str:
        mode = "dark" if self["dark_mode"] else "light"
        return f"{mode}_{self['theme']}.xml"
    
    def apply(self):
        apply_stylesheet(self.app, theme=self.theme, 
                         invert_secondary=self["invert_secondary"],
                         extra={"font_size": f"{self['font_size']}px",})


    def save(self):
        current_dir = os.getcwd()
        settings_folder = os.path.join(current_dir, 'settings')
        if not os.path.exists(settings_folder):
            os.makedirs(settings_folder)
        filename = os.path.join(settings_folder, 'settings.json')
        with open(filename, 'w') as f:
            json.dump(self.toDict(), f, indent=4)

    def load(self):
        current_dir = os.getcwd()
        settings_folder = os.path.join(current_dir, 'settings')
        if not os.path.exists(settings_folder):
            os.makedirs(settings_folder)
        filename = os.path.join(settings_folder, 'settings.json')
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.fromDict(data)
                print("Settings loaded")
        except FileNotFoundError:
            self.save()
        except KeyError as e:
            print(f"Error loading settings.json, KeyError: {e}")
            self.save()
        except ValueError as e:
            print(f"Error loading settings.json, ValueError: {e}")
            self.save()