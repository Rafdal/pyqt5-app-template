from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QApplication
from PyQt6.QtCore import Qt

from backend.Settings import Settings
from frontend.widgets.DynamicSettingsWidget import DynamicSettingsWidget

from qt_material import apply_stylesheet

class SettingsDialog(QDialog):
    def __init__(self, title: str, settings: Settings, app:QApplication, on_submit=lambda: None):
        super().__init__()
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        self.on_submit = on_submit
        self.app = app
        self.settings = settings
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.dynamicSettingsWidget = DynamicSettingsWidget(settings, on_edit=self.on_edit, title=None)
        layout.addWidget(self.dynamicSettingsWidget)

        button = QPushButton("Save")
        button.clicked.connect(self.submit)
        layout.addWidget(button)

        button = QPushButton("Cancel")
        button.clicked.connect(self.reject)
        layout.addWidget(button)

    def on_edit(self):
        apply_stylesheet(self.app, theme=self.settings['theme'])

    def exec(self) -> int:
        return super().exec()

    def submit(self):
        self.settings.save()
        self.on_submit()
        super().accept()

    def reject(self) -> None:
        super().reject()