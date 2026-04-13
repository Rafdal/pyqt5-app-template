from utils.ParamList import ParameterList, NumParam, BoolParam, TextParam, ChoiceParam, ConstParam
from PyQt6.QtWidgets import QApplication

from backend.Settings import Settings
from backend.handlers.SerialPortHandler import SerialPortHandler
from backend.handlers.TelemetryHandler import TelemetryHandler

class MainModel:
    # Model attributes
    count = 0

    def __init__(self, app: QApplication) -> None:
        self.app = app
        self.settings = Settings(app)
        self.settings.load()
        self.settings.apply()

        self.serial = SerialPortHandler()
        self.serial.auto_connect(include_manufacturer="arduino")
        self.serial.set_wait_time(10)

        self.telemetry = TelemetryHandler()
        self.telemetry.on_error.connect(self.serial.error)
        self.serial.data_received.connect(self.telemetry.handle_serial_data)

    # Model methods
    def increment_count(self):
        self.count += 1