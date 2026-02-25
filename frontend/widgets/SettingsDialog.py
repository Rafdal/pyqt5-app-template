from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QApplication
from PyQt6.QtCore import Qt, pyqtSignal

from backend.Settings import Settings
from frontend.widgets.DynamicSettingsWidget import DynamicSettingsWidget

class SettingsDialog(QDialog):
    on_submit = pyqtSignal()

    def __init__(self, title: str, settings: Settings):
        super().__init__()
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        self.settings = settings
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.dynamicSettingsWidget = DynamicSettingsWidget(settings)
        self.dynamicSettingsWidget.on_edit.connect(self.on_edit)
        layout.addWidget(self.dynamicSettingsWidget)

        button = QPushButton("Save")
        button.clicked.connect(self.submit)
        layout.addWidget(button)

        button = QPushButton("Cancel")
        button.clicked.connect(self.reject)
        layout.addWidget(button)

    def on_edit(self):
        self.settings.apply()

    def exec(self) -> int:
        return super().exec()

    def submit(self):
        self.settings.save()
        self.on_submit.emit()
        super().accept()

    def reject(self) -> None:
        super().reject()