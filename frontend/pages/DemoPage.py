from PyQt6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QToolButton, QWidget
from frontend.pages.BaseClassPage import BaseClassPage
from PyQt6.QtGui import QIcon, QColor

from frontend.widgets.BasicWidgets import Button, Slider, NumberInput
from frontend.widgets.IconButtons import SwitchThemeButton

class DemoPage(BaseClassPage):
    title = "Demo Page"

    def initUI(self, layout):
        hlayout = QHBoxLayout()

        # Add a QPushButton
        button = QPushButton("Click me!")
        button.clicked.connect(self.on_button_click)

        # Add a custom (round) Button
        customButton = Button("Custom Button", on_click=lambda: print("Custom button clicked"))

        # Add a label
        self.label = QLabel("Count: 0")

        slider = Slider("Demo Slider", interval=(0, 100), step=1, defaultVal=50)
        slider.on_change.connect(self.on_slider_change)

        num_input = NumberInput("Number Input", interval=(0, 100), step=1, default=50)
        num_input.on_change.connect(self.on_slider_change)

        
        # Set layouts
        hlayout.addWidget(button)
        hlayout.addWidget(customButton)
        layout.addLayout(hlayout)
        layout.addWidget(self.label)
        layout.addWidget(slider)
        layout.addWidget(num_input)

    def on_button_click(self):
        print("Button clicked")
        self.model.increment_count()
        self.label.setText(f"Count: {self.model.count}")

    def on_slider_change(self, value):
        print(f"Slider value: {value} ({type(value).__name__})")