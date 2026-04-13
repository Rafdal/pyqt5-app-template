from frontend.pages.BaseClassPage import BaseClassPage
import time

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout

from frontend.widgets.LivePlotWidget import LivePlotWidget
from backend.handlers.TelemetryHandler import IMUData
from frontend.widgets.BasicWidgets import Button, IntNumberInput

class PlotPage(BaseClassPage):
    title = "Plot Page"

    def initUI(self, layout: QVBoxLayout):
        # Create the plot widget and add it to the layout

        toggle_adjust_btn = Button("Toggle Auto-Adjust", on_click=self.toggle_auto_adjust)
        max_points_input = IntNumberInput("Max Points", interval=(100, 10000), step=100, default=2000)
        max_visible_points_input = IntNumberInput("Max Visible Points", interval=(100, 10000), step=100, default=300)

        max_points_input.on_change.connect(lambda value: setattr(self.plot_widget, 'max_points', value))
        max_visible_points_input.on_change.connect(lambda value: setattr(self.plot_widget, 'max_visible_points', value))

        hlayout = QHBoxLayout()
        hlayout.addWidget(toggle_adjust_btn)
        hlayout.addWidget(max_points_input)
        hlayout.addWidget(max_visible_points_input)

        self.plot_widget = LivePlotWidget(
            enable_region=True,
            max_points=2000,
            max_visible_points=300,
            auto_adjust_on_new_data=True,
        )
        self._t0 = time.monotonic()
        layout.addLayout(hlayout)
        layout.addWidget(self.plot_widget)

        self.init_signals()

    def init_signals(self):
        self.model.telemetry.on_data.connect(self.handle_telemetry_data)

    def handle_telemetry_data(self, data: IMUData):
        x = time.monotonic() - self._t0
        y = float(data.accel.x)
        self.plot_widget.append_sample(x, y)

    def toggle_auto_adjust(self):
        current_state = self.plot_widget.auto_adjust_on_new_data
        self.plot_widget.auto_adjust_on_new_data = not current_state