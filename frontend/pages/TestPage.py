from frontend.pages.BaseClassPage import BaseClassPage
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QPushButton

class TestPage(BaseClassPage):
    title = "Test Page"

    def initUI(self, layout):

        # Add widgets to layout
        layout.addWidget(QLabel("Test Page"))

        # Add a button
        button = QPushButton("Click me!")
        button.clicked.connect(self.on_button_click)
        layout.addWidget(button)

    def on_button_click(self):
        print("Button clicked")

    def on_tab_focus(self):
        print("Test Page focused")

    def on_tab_unfocus(self):
        print("Test Page unfocused")