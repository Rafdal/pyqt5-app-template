from frontend.pages.BaseClassPage import BaseClassPage
import time

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout

from frontend.widgets.LivePlotWidget import LivePlotWidget
from frontend.widgets.LiveMultiPlotWidget import LiveMultiPlotWidget
from backend.handlers.TelemetryHandler import IMUData
from frontend.widgets.BasicWidgets import Button, IntNumberInput

class PlotPage(BaseClassPage):
    title = "Plot Page"

    def initUI(self, layout: QVBoxLayout):
        # Create the plot widget and add it to the layout

        toggle_adjust_btn = Button("Toggle Auto-Tracking", on_click=self.toggle_auto_adjust)
        buffer_size_input = IntNumberInput("Buffer Size", interval=(100, 10000), step=100, default=2000)

        self.plot_widget = LiveMultiPlotWidget(
            line_count=3,
            labels=["Accel X", "Accel Y", "Accel Z"],
            enable_region=True,
            buffer_size=2000,
            auto_adjust_on_new_data=True,
            stop_auto_adjust_on_click=True,
            max_region_size=100,
        )

        # self.plot_widget.set_style(background_color="#fff", pen_color="#f00", line_width=2)
        self.plot_widget.set_style(background_color="#fff")
        self.plot_widget.set_line_style(0, pen_color="#f00", line_width=2)
        self.plot_widget.set_line_style(1, pen_color="#090", line_width=2)
        self.plot_widget.set_line_style(2, pen_color="#00f", line_width=2)

        buffer_size_input.on_change.connect(self.plot_widget.set_buffer_size)

        hlayout = QHBoxLayout()
        hlayout.addWidget(toggle_adjust_btn)
        hlayout.addWidget(buffer_size_input)
        self._t0 = time.monotonic()
        layout.addLayout(hlayout)
        layout.addWidget(self.plot_widget)

        self.init_signals()

    def init_signals(self):
        self.model.telemetry.on_data.connect(self.handle_telemetry_data)

    def handle_telemetry_data(self, data: IMUData):
        x = time.monotonic() - self._t0
        # y = float(data.accel.z)
        self.plot_widget.append_sample(x, [data.accel.x, data.accel.y, data.accel.z])

    def toggle_auto_adjust(self):
        current_state = self.plot_widget.auto_adjust_on_new_data
        self.plot_widget.auto_adjust_on_new_data = not current_state