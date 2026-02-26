from utils.ParamList import ParameterList, NumParam, BoolParam, TextParam, ChoiceParam, ConstParam
from PyQt6.QtWidgets import QApplication

from backend.Settings import Settings
from backend.handlers.SerialPortHandler import SerialPortHandler

class MainModel:
    # Model attributes
    count = 0

    def __init__(self, app: QApplication) -> None:
        self.app = app
        self.settings = Settings(app)
        self.settings.load()
        self.settings.apply()

        self.serial = SerialPortHandler()

    # Model methods
    def increment_count(self):
        self.count += 1