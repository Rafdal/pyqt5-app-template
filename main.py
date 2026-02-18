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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('frontend/assets/icon.png'))

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