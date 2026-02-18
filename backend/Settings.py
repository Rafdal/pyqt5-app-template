import json
from utils.ParamList import ParameterList, NumParam, BoolParam, TextParam, ChoiceParam, ConstParam
from qt_material import list_themes

import os

class Settings(ParameterList):
    def __init__(self):
        super().__init__([
            ChoiceParam("theme", options=list_themes(), value="dark_blue.xml", text="Color Theme"),
        ])

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