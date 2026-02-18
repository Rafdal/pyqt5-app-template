from PyQt6.QtWidgets import QMainWindow, QMenuBar, QDialog
from PyQt6.QtGui import QIcon, QAction, QFont
from PyQt6.QtWidgets import QSizePolicy

from qt_material import list_themes, apply_stylesheet

from backend.MainModel import MainModel
from frontend.widgets.SettingsDialog import SettingsDialog

def create_menu_bar(main: QMainWindow, menuBar: QMenuBar, model: MainModel):
    fileMenu = menuBar.addMenu('&File')
    if fileMenu is None:
        return
    
    settingsAction = QAction(QIcon('settings.png'), '&Settings', main)
    dialog = SettingsDialog(title="Settings", settings=model.settings, app=model.app)
    settingsAction.triggered.connect(lambda: dialog.exec())
    fileMenu.addAction(settingsAction)

    exitAction = QAction(QIcon('exit.png'), '&Exit', main)
    exitAction.setShortcut('Ctrl+Q')
    exitAction.setStatusTip('Exit application')
    exitAction.triggered.connect(main.close)

    fileMenu.addAction(exitAction)


    # Dark Theme menu
    darkThemeMenu = menuBar.addMenu('&Dark Theme')
    if darkThemeMenu is None:
        return
    themes = list_themes()
    for theme in themes:
        if not theme.startswith('dark'):
            continue
        themeAction = QAction(theme, main)
        themeAction.triggered.connect(lambda _, t=theme: apply_stylesheet(main, theme=t))
        darkThemeMenu.addAction(themeAction)


    # Light Theme menu
    lightThemeMenu = menuBar.addMenu('&Light Theme')
    if lightThemeMenu is None:
        return
    for theme in themes:
        if not theme.startswith('light'):
            continue
        themeAction = QAction(theme, main)
        themeAction.triggered.connect(lambda _, t=theme: apply_stylesheet(main, theme=t))
        lightThemeMenu.addAction(themeAction)