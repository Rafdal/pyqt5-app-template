from utils.ParamList import ParameterList, NumParam, BoolParam, TextParam, ChoiceParam, ConstParam
from backend.Settings import Settings

from PyQt6.QtWidgets import QApplication

class MainModel:
    # Model attributes
    count = 0

    def __init__(self, app: QApplication) -> None:
        self.app = app
        self.settings = Settings(app)
        self.settings.load()
        self.settings.apply()

    # Model methods
    def increment_count(self):
        self.count += 1