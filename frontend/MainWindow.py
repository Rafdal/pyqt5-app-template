# MainWindow.py
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from frontend.pages.BaseClassPage import BaseClassPage

from frontend.MenuBar import CreateMenuBar

# DO NOT TOUCH THIS CODE
class MainWindow(QMainWindow):
    """ 
    Main Window class that contains a Page Navigator (tab widget)
    1) The pages object instances should be derived from BaseClassPage and passed as a list
    2) Each page must have:
        - a .title (str) attribute
        - a method initUI(layout) that initializes the page layout (layout is a QVBoxLayout object)
        - a model attribute that is set by the main window
    3) Each page can have:
        - a method on_tab_focus() that is called when the page is focused
        - a method on_tab_unfocus() that is called when the page is unfocused
    """ 
    def __init__(self, pages, model, title):
        super().__init__()
        self.last_page_index = 0
        self.model = model
        self.setWindowTitle(title)
        self.initUI(pages)

    def initUI(self, pages):

        # center window on screen
        self.resize(1600, 1000)
        screen = QApplication.primaryScreen()
        if screen is None:
            raise Exception(f"No primary screen found")
        rect = screen.availableGeometry()
        sw, sh = self.width(), self.height()
        rw, rh = rect.width(), rect.height()
        self.setMinimumSize(400, 300)
        self.setGeometry(rw // 2 - sw // 2, rh // 2 - sh // 2, sw, sh)

        image_label = QLabel()
        pixmap = QPixmap('frontend/assets/icon.png')
        if not pixmap.isNull():
            image_label.setPixmap(pixmap.scaled(600, 600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(image_label)
        self.show()

        # Check we don't have repeated titles
        titles = [page.title for page in pages]
        if len(titles) != len(set(titles)):
            raise Exception("All pages must have unique titles")

        # create tab widget (Page Navigator) and add pages
        tab_widget = QTabWidget()
        for page in pages:
            # Check if page is a BaseClassPage object
            if not isinstance(page, BaseClassPage):
                raise Exception("All pages must be subclasses of BaseClassPage")
            page.set_model(self.model)
            page_layout = getattr(page, "layout", None)
            if not isinstance(page_layout, QVBoxLayout):
                raise Exception("All pages must define a QVBoxLayout in page.layout")
            page.initUI(page_layout)
            page.setLayout(page_layout)
            tab_widget.addTab(page, page.title)

        # set tab change event
        tab_widget.currentChanged.connect(self.tab_changed)

        # add menu bar
        menu_bar = self.menuBar()
        if menu_bar is not None:
            self.menuBarData = CreateMenuBar(self, menu_bar, self.model)

        self.setCentralWidget(tab_widget)
        self.show()


    def tab_changed(self, index):
        tab_widget = self.centralWidget()
        if not isinstance(tab_widget, QTabWidget):
            return

        # unfocus last active tab
        last_page = tab_widget.widget(self.last_page_index)
        if isinstance(last_page, BaseClassPage) and hasattr(last_page, 'on_tab_unfocus'):
            print(f"Page {self.last_page_index} '{last_page.title}' unfocused")
            last_page.on_tab_unfocus()

        # get newly active tab
        current_page = tab_widget.widget(index)
        self.last_page_index = index

        # check if method exists
        if isinstance(current_page, BaseClassPage) and hasattr(current_page, 'on_tab_focus'):
            print(f"Page {index} '{current_page.title}' focused")
            current_page.on_tab_focus()