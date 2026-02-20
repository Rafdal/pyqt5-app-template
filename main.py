# main.py
import sys
from PyQt6.QtWidgets import QApplication

print("Running main.py")

from backend.MainModel import *
from frontend.MainWindow import *
from frontend.pages.DemoPage import *
from frontend.pages.BlankPage import *
from frontend.pages.ParamListExample import *
from frontend.pages.DefaultWidgetsPage import *

from qt_material import apply_stylesheet

import faulthandler

import signal
from PyQt6.QtCore import QTimer

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('frontend/assets/icon.png'))

    # Handle Ctrl+C in terminal
    signal.signal(signal.SIGINT, lambda *_: app.quit())
    sigint_timer = QTimer()
    sigint_timer.timeout.connect(lambda: None)
    sigint_timer.start(200)

    # create a Data Model
    mainModel = MainModel(app)

    # create pages
    pages = [
        DemoPage(),
        BlankPage(),
        ParamListExample(),
        DefaultWidgetsPage()
    ]

    print("Pages created, creating main window")
    apply_stylesheet(app, theme=mainModel.settings['theme'])

    ex = MainWindow(pages=pages, model=mainModel, title="App Title")

    faulthandler.enable()
    sys.exit(app.exec())