from PyQt6.QtWidgets import QHBoxLayout, QListWidget, QListWidgetItem, QLineEdit, QVBoxLayout, QWidget, QSizePolicy, QLabel, QDialog, QCompleter
from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QColor, QBrush

from frontend.widgets.BasicWidgets import Button, TextInput

class SerialPortMenu(QWidget):
    """
    A widget that provides a menu for serial port operations.
    It includes buttons for scanning ports, connecting, disconnecting, and killing the port.
    """
    def __init__(self, serial_handler):
        super().__init__()
        self.serial_handler = serial_handler
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.initUI(layout)
        self.initSignals()
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.scan_ports()  # Initial scan to populate the list with available ports

    def initUI(self, layout):
        hlayout = QHBoxLayout()
        refresh_btn = Button("Scan Ports", on_click=self.scan_ports)
        connect_btn = Button("Connect", on_click=self.connect_to_port)
        disconnect_btn = Button("Disconnect", on_click=self.disconnect_from_port)
        hlayout.addWidget(refresh_btn)
        hlayout.addWidget(connect_btn)
        hlayout.addWidget(disconnect_btn)

        self.baud_input = TextInput("Baud Rate", regex=r"^\d+$", layout='h', callOnEnter=False)
        completer = QCompleter(["115200", "230400", "460800", "500000", "921600", "1000000"])
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        if completer is None:
            raise Exception("Failed to create QCompleter for baud rate input.")
        self.baud_input.textbox.setCompleter(completer)
        self.baud_input.textbox.setFixedWidth(100)  # Set a fixed width for the baud rate input

        self.connection_status = QLabel("Connected", styleSheet="color: green;") if self.serial_handler.connected_status else QLabel("Disconnected", styleSheet="color: red;")
        self.connection_status.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.connection_status.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.connection_status.setFixedWidth(self.connection_status.sizeHint().width() + 20)  # Add some padding

        hlayout.addWidget(self.baud_input)
        hlayout.addWidget(self.connection_status)
        hlayout.addStretch()
        hlayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        kill_port_btn = Button("Kill Port", on_click=self.serial_handler.kill_port)
        hlayout.addWidget(kill_port_btn)

        # Add a list widget to display serial ports - with styling to ensure visibility
        portListHLayout = QHBoxLayout()
        self.port_list = QListWidget()
        self.port_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.port_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded) # ScrollBarAsNeeded
        self.port_list.setFixedHeight(0)  # Start with no height
        self.port_list.setMinimumWidth(200)  # Set a minimum width for the list widget

        # Add widgets to the main layout
        layout.addLayout(hlayout)
        # layout.addLayout(portListHLayout)
        layout.addWidget(self.port_list)

    def initSignals(self):
        self.serial_handler.connected.connect(self.on_connection_status_changed)
        self.port_list.itemClicked.connect(self.on_port_clicked)

    def scan_ports(self):
        # Clear the list before updating
        self.port_list.clear()
    
        # Fetch available serial ports using SerialPortHandler
        ports = self.serial_handler.list_serial_ports()
    
        # Populate the list widget with port information - with explicit text setting
        for port in ports:            
            list_item = QListWidgetItem()
            list_item.setText(str(port))
            list_item.setForeground(QBrush(QColor(0, 0, 0)))  # Black text
            list_item.setData(Qt.ItemDataRole.UserRole, port)  # Store port data with explicit role
            self.port_list.addItem(list_item)
    
        # Adjust the height of the port_list to fit its content
        total_items = self.port_list.count()
        if total_items > 0:
            row_height = self.port_list.sizeHintForRow(0)
            new_height = row_height * total_items + 2 * self.port_list.frameWidth()
            new_height = min(new_height, 600)  # Set a maximum height to prevent it from growing too large
            self.port_list.setFixedHeight(new_height)
            self.port_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)  # Show scrollbar if needed
        else:
            self.port_list.setFixedHeight(0)

        self.port_list.update()

    def on_port_clicked(self, item):
        # Retrieve the SerialPortData object stored in the clicked item
        port_data = item.data(Qt.ItemDataRole.UserRole)
        self.serial_handler.selected_port = port_data

    def connect_to_port(self):
        # Attempt to connect to the selected port
        self.serial_handler.set_baudrate(int(self.baud_input.text()))
        if self.serial_handler.connect():
            print(f"Page: Port Connected")
        else:
            print(f"Page: Failed to connect.")
        print(f"Port status: {'Open' if self.serial_handler.serial_port.isOpen() else 'Closed'}")

    def on_connection_status_changed(self, connected):
        # Update the UI based on connection status
        if connected:
            # print("Connected to serial port.")
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet("color: green;")
        else:
            self.connection_status.setText("Disconnected")
            self.connection_status.setStyleSheet("color: red;")

    def disconnect_from_port(self):
        # Disconnect from the current port
        self.serial_handler.disconnect()
        print("Disconnected from port.")


class SerialPortMenuDialog(QDialog):
    """
    A dialog that contains the SerialPortMenu widget.
    """
    def __init__(self, serial_handler):
        super().__init__()
        self.setWindowTitle("Serial Port Menu")
        self.setModal(True)
        layout = QVBoxLayout()
        self.serial_menu = SerialPortMenu(serial_handler)
        layout.addWidget(self.serial_menu)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)  # Allow resizing
        serial_handler.connected.connect(lambda status: self.accept() if status else None)  # Close dialog on successful connection