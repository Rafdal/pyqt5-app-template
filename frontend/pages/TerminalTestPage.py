from frontend.pages.BaseClassPage import BaseClassPage
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

from frontend.widgets.ConsoleWidget import ConsoleWidget
from frontend.widgets.InputTerminal import InputTerminal

class TerminalTestPage(BaseClassPage):
    title = "Terminal Test Page"

    def initUI(self, layout):
        # layout is a QVBoxLayout
        # you can access to the model here and its methods/attributes with self.model
        self.consoleWidget = ConsoleWidget()
        self.inputTerminal = InputTerminal()
        self.port_data = QLabel("No data received yet.")
        self.port_data.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.port_data.setMargin(5)

        layout.addWidget(self.consoleWidget)
        layout.addWidget(self.port_data)
        layout.addWidget(self.inputTerminal)

        self.initSignals()

    def initSignals(self):
        self.inputTerminal.returnPressed.connect(self.handleInput)
        self.model.serial.data_received.connect(self.serial_data_received)
        self.model.serial.error.connect(self.consoleWidget.appendError)
        self.model.serial.connected.connect(lambda status: self.consoleWidget.appendInfo(f"Serial port {'connected' if status else 'disconnected'}.\n"))
        self.model.serial.bytes_per_second.connect(lambda bps: self.port_data.setText(f"Data Rate: {bps} B/s"))

    def handleInput(self, inputText: str):
        self.consoleWidget.appendText(f"SENT: {inputText}\n")
        self.model.serial.send_data(bytearray(inputText, 'utf-8'))  # Send the input text as bytes to the serial port

    def serial_data_received(self, data: bytearray):
        try:
            decoded_data = data.decode('utf-8')
            self.consoleWidget.appendText(decoded_data)
        except UnicodeDecodeError:
            self.consoleWidget.appendText(f"RAW: {data}\n")

    def on_tab_focus(self):
        # define what happens when the tab is focused (optional)
        pass

    def on_tab_unfocus(self):
        # define what happens when the tab is unfocused (optional)
        pass