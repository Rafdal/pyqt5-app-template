from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt6.QtCore import pyqtSignal, QObject, QThread, QTimer, pyqtBoundSignal
import typing, dataclasses

@dataclasses.dataclass
class SerialPortData:
    name: str = "None"
    description: str = "None"
    manufacturer: str = "None"
    baudrate: int = 115200
    def prettyPrint(self):
        return f"Port: {self.name}, Description: {self.description}, Manufacturer: {self.manufacturer}, Baud Rate: {self.baudrate}"
    def __str__(self):
        return f"{self.name} | {self.description} | {self.manufacturer}"

class SerialPacketFilter(QObject):
    received = pyqtSignal(bytearray)
    def __init__(self, header: bytes, terminator: bytes):
        super().__init__()
        self.header = header
        self.terminator = terminator

    def process_buffer(self, buffer: bytearray):
        if not (buffer and self.header and self.terminator):
            return

        while True:
            # Find first header
            header_pos = buffer.find(self.header)

            if header_pos < 0:
                # Keep only possible partial header tail
                keep = len(self.header) - 1
                buffer = buffer[-keep:] if keep > 0 else bytearray()
                return

            if header_pos > 0:
                # Drop noise before header
                buffer = buffer[header_pos:]

            # Find terminator after header
            terminator_pos = buffer.find(self.terminator, len(self.header))
            if terminator_pos < 0:
                # Incomplete frame, wait for next read
                return

            # Extract payload between header and terminator
            data_chunk = buffer[len(self.header):terminator_pos]
            self.received.emit(bytearray(data_chunk))  # emit copy

            # Remove processed frame and continue (handles multiple frames)
            buffer = buffer[terminator_pos + len(self.terminator):]

class SerialPortHandler(QObject):
    connected = pyqtSignal(bool)
    connected_status: bool = False
    error = pyqtSignal(str)

    data_received = pyqtSignal(bytearray)
    data_sent = pyqtSignal(bytearray)
    bytes_per_second = pyqtSignal(int)
    filters: list[SerialPacketFilter] = []  # List of SerialPacketFilter instances to process incoming data

    max_buffer_size = 2048  # Define a maximum buffer size
    bytes_received = 0      # Initialize bytes received counter

    def __init__(self):
        super().__init__()
        self.serial_port = QSerialPort()
        self.buffer = bytearray()  # Initialize buffer as a bytearray
        self.serial_port.errorOccurred.connect(self._serial_error_handler)
        self.serial_port.readyRead.connect(self._handle_read)
        self.selected_port = SerialPortData()

        self.bps_timer = QTimer()
        self.bps_timer.timeout.connect(self._on_bps_timeout)
        self.bps_timer.setSingleShot(False)
        self.bps_timer.setInterval(1000)  # Update every second
        self.bps_timer.start(1000)  # Update every second

    def add_filter(self, header: bytes, terminator: bytes, callback = None) -> None:
        """Add a SerialPacketFilter to process incoming data"""
        f = SerialPacketFilter(header, terminator)
        f.received.connect(callback)
        if f not in self.filters:
            self.filters.append(f)

    def set_baudrate(self, baudrate: int):
        """Set the baud rate for the serial port"""
        self.selected_port.baudrate = baudrate

    def connect(self):
        """Connect to a serial port with the specified baud rate"""
        if not self.selected_port.name or self.selected_port.name == "None":
            self.error.emit("No port selected")
            return False
        
        if self.serial_port is None:
            raise ValueError("Serial port object is not initialized")

        # Close any existing connection
        if self.serial_port.isOpen():
            self.serial_port.close()
            
        try:
            # Configure port with explicit settings
            self.serial_port.setPortName(self.selected_port.name)
            self.serial_port.setBaudRate(self.selected_port.baudrate)
            self.serial_port.setDataBits(QSerialPort.DataBits.Data8)
            self.serial_port.setParity(QSerialPort.Parity.NoParity)
            self.serial_port.setStopBits(QSerialPort.StopBits.OneStop)
            self.serial_port.setFlowControl(QSerialPort.FlowControl.NoFlowControl)
            
            # Try to open the port
            if not self.serial_port.open(QSerialPort.OpenModeFlag.ReadWrite):
                error_msg = f"Failed to open port {self.selected_port.name}: {self.serial_port.errorString()}"
                self.error.emit(error_msg)
                return False
            else:
                # Clear buffer on new connection
                self.buffer.clear()
                self.connected.emit(True)
                self.connected_status = True
                self.toggle_dtr_rts()
                return True
        except Exception as e:
            self.error.emit(f"Error connecting to port {self.selected_port.name}: {str(e)}")
            return False
        
    def list_serial_ports(self) -> typing.List[SerialPortData]:
        """Lists all available serial ports with their information."""
        ports = []
        for info in QSerialPortInfo.availablePorts():
            port_data = SerialPortData(
                name=info.portName(),
                description=info.description(),
                manufacturer=info.manufacturer(),
            )
            ports.append(port_data)
        return ports
    
    def auto_connect(self, exclude_manufacturer: str):
        """Automatically connect to the first available serial port that is not excluded."""
        ports = self.list_serial_ports()
        for port in ports:
            if exclude_manufacturer not in port.manufacturer:
                self.selected_port = port
                if self.connect():
                    return True
        self.error.emit("No suitable serial port found")
        return False

    def disconnect(self) -> None:
        """Disconnect from the current serial port"""
        if self.serial_port is None:
            raise ValueError("Serial port object is not initialized")
        try:
            if self.serial_port.isOpen():
                self.serial_port.close()
            self.connected.emit(False)
            self.connected_status = False
        except Exception as e:
            self.error.emit(f"Error disconnecting: {str(e)}")

    def kill_port(self) -> None:
        if self.serial_port is None:
            raise ValueError("Serial port object is not initialized")
        self.serial_port.errorOccurred.disconnect(self._serial_error_handler)
        self.serial_port.readyRead.disconnect(self._handle_read)
        self.disconnect()
        del self.serial_port
        self.serial_port = None
        self.buffer.clear()
        self.connected.emit(False)
        self.connected_status = False
        self.serial_port = QSerialPort()
        self.selected_port = SerialPortData()
        self.serial_port.errorOccurred.connect(self._serial_error_handler)
        self.serial_port.readyRead.connect(self._handle_read)

    def toggle_dtr_rts(self) -> None:
        """Toggle DTR and RTS lines to wake up the device."""
        if self.serial_port is None:
            raise ValueError("Serial port object is not initialized")
        if self.serial_port.isOpen():
            self.serial_port.setDataTerminalReady(False)
            self.serial_port.setRequestToSend(False)
            QThread.msleep(100)  # Wait 100ms
            self.serial_port.setDataTerminalReady(True)
            self.serial_port.setRequestToSend(True)

    def send_data(self, data: bytearray) -> bool:
        """Send data to the serial port"""
        if self.serial_port is None:
            raise ValueError("Serial port object is not initialized")
        if not self.serial_port.isOpen():
            self.error.emit("Cannot send data: Port is not open")
            return False

        try:
            bytes_written = self.serial_port.write(data)
            self.data_sent.emit(data)
            return bytes_written == len(data)
        except TypeError as e:
            self.error.emit(f"Data must be bytes or bytearray: {str(e)}. {type(data)} is not supported.")
            return False
        except Exception as e:
            self.error.emit(f"Error sending data: {str(e)}")
            return False
        
    def _handle_read(self) -> None:
        """Handle data received from the serial port"""
        if self.serial_port is None:
            raise ValueError("Serial port object is not initialized")
        if self.serial_port.bytesAvailable() > 0:
            try:
                # Convert QByteArray to bytes properly
                raw_data = self.serial_port.readAll()
                newData = bytes(raw_data.data())
                self.bytes_received += len(newData)  # Update bytes received counter
                                
                if newData:
                    # Add new data to buffer
                    self.buffer.extend(newData)
                    self.data_received.emit(bytearray(newData))  # Emit raw data received signal
                    
                    # Limit buffer size
                    if len(self.buffer) > self.max_buffer_size:
                        self.buffer = self.buffer[-self.max_buffer_size:]
                    
                    # Process complete lines
                    for f in self.filters:
                        f.process_buffer(self.buffer)
                    # self._process_buffer()
                    # self._process_buffer_with_header()
                    # self._process_buffer_str()
            except Exception as e:
                self.error.emit(f"Error reading from serial port: {str(e)}")

    # def _process_buffer_with_header(self) -> None:
    #     if not (self.buffer and self.header and self.terminator):
    #         return

    #     while True:
    #         # Find first header
    #         header_pos = self.buffer.find(self.header)

    #         if header_pos < 0:
    #             # Keep only possible partial header tail
    #             keep = len(self.header) - 1
    #             self.buffer = self.buffer[-keep:] if keep > 0 else bytearray()
    #             return

    #         if header_pos > 0:
    #             # Drop noise before header
    #             self.buffer = self.buffer[header_pos:]

    #         # Find terminator after header
    #         terminator_pos = self.buffer.find(self.terminator, len(self.header))
    #         if terminator_pos < 0:
    #             # Incomplete frame, wait for next read
    #             return

    #         # Extract payload between header and terminator
    #         data_chunk = self.buffer[len(self.header):terminator_pos]
    #         self.data_chunk_received.emit(bytearray(data_chunk))  # emit copy

    #         # Remove processed frame and continue (handles multiple frames)
    #         self.buffer = self.buffer[terminator_pos + len(self.terminator):]

    # def _process_buffer(self) -> None:
    #     """ Process buffer as raw bytes (without terminators) """
    #     if self.buffer:
    #         self.data_received.emit(self.buffer)
    #         self.buffer.clear()

    # def _process_buffer_str(self) -> None:
    #     """Process buffer for complete lines"""
    #     try:
    #         # Find position of first terminator
    #         terminator_pos = self.buffer.find(self.terminator)
            
    #         # Process all complete lines in buffer
    #         while terminator_pos >= 0:
    #             # Extract line (excluding terminator)
    #             line_bytes = self.buffer[:terminator_pos]
                
    #             # Convert to string and emit
    #             try:
    #                 line = line_bytes.decode('utf-8', errors='replace').strip()
    #                 if line:
    #                     self.data_received_str.emit(line)
    #             except Exception as e:
    #                 self.error.emit(f"Error decoding line: {str(e)}")
                
    #             # Remove processed data from buffer (including terminator)
    #             self.buffer = self.buffer[terminator_pos + len(self.terminator):]
                
    #             # Find next terminator
    #             terminator_pos = self.buffer.find(self.terminator)
    #     except Exception as e:
    #         self.error.emit(f"Error processing buffer: {str(e)}")


    # def _on_data_received_str(self, data) -> None:
    #     self.data_received_str.emit(data)

    def _on_bps_timeout(self) -> None:
        """Handle bytes per second calculation"""
        self.bytes_per_second.emit(self.bytes_received)
        self.bytes_received = 0

    def _serial_error_handler(self, error) -> None:
        if type(error) != QSerialPort.SerialPortError:
            raise ValueError("The error is not a QSerialPort.SerialPortError")
        
        match error:
            case QSerialPort.SerialPortError.NoError:
                return
            case QSerialPort.SerialPortError.DeviceNotFoundError:
                self.error.emit(f"Device {self.selected_port.name} not found")
            case QSerialPort.SerialPortError.PermissionError:
                self.error.emit(f"Permission error on {self.selected_port.name}")
            case QSerialPort.SerialPortError.OpenError:
                self.error.emit(f"Error opening {self.selected_port.name}")
            case QSerialPort.SerialPortError.WriteError:
                self.error.emit(f"Error on {self.selected_port.name} WriteError")
            case QSerialPort.SerialPortError.ReadError:
                self.error.emit(f"Error on {self.selected_port.name} ReadError")
            case QSerialPort.SerialPortError.ResourceError:
                self.error.emit(f"Error on {self.selected_port.name} ResourceError")
            case QSerialPort.SerialPortError.UnsupportedOperationError:
                self.error.emit(f"Error on {self.selected_port.name} UnsupportedOperationError")
            case QSerialPort.SerialPortError.TimeoutError:
                self.error.emit(f"Error on {self.selected_port.name} TimeoutError")
            case QSerialPort.SerialPortError.NotOpenError:
                self.error.emit(f"Error on {self.selected_port.name} NotOpenError")
            case QSerialPort.SerialPortError.UnknownError:
                self.error.emit(f"Error on {self.selected_port.name} UnknownError")
            case _:
                self.error.emit(f"Undefined Error {str(error)} on {self.selected_port.name}")