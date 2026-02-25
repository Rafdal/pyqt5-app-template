from PyQt6.QtWidgets import QMainWindow, QMenuBar, QLabel, QPushButton
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt

from backend.MainModel import MainModel
from frontend.widgets.SettingsDialog import SettingsDialog
from frontend.widgets.IconButtons import SwitchThemeButton

class CreateMenuBar():
    def __init__(self, main: QMainWindow, menuBar: QMenuBar, model: MainModel):
        menuBar.setNativeMenuBar(False)

        fileMenu = menuBar.addMenu('&File')
        if fileMenu is None:
            return
        
        self.model = model
        
        settingsAction = QAction(QIcon('settings.png'), '&Settings', main)
        dialog = SettingsDialog(title="Settings", settings=model.settings)
        settingsAction.triggered.connect(lambda: dialog.exec())
        fileMenu.addAction(settingsAction)

        exitAction = QAction(QIcon('exit.png'), '&Exit', main)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(main.close)

        fileMenu.addAction(exitAction)

        # menuBar.addSeparator()
        self.themeBtn = SwitchThemeButton()
        self.themeBtn.update(selected=self.model.settings["dark_mode"])
        self.themeBtn.on_click.connect(self.toggle_theme)

        menuBar.setCornerWidget(self.themeBtn, Qt.Corner.TopRightCorner)

    def toggle_theme(self, selected):
        self.model.settings["dark_mode"] = selected
        self.model.settings.apply()
        self.model.settings.save()