from frontend.pages.BaseClassPage import BaseClassPage

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSlider

class DefaultWidgetsPage(BaseClassPage):
    title = "Default Widgets Page"

    def initUI(self, layout):
        # Create and add widgets to the layout
        label = QLabel("This is a default widgets page.")
        layout.addWidget(label)

        slider = QSlider()
        slider.setOrientation(Qt.Orientation.Horizontal)
        layout.addWidget(slider)

        button = QPushButton("Click me!")
        layout.addWidget(button)

    def on_tab_focus(self):
        pass

    def on_tab_unfocus(self):
        pass