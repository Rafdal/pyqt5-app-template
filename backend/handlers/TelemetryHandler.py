from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from backend.handlers.SerialPortHandler import SerialPortHandler
from dataclasses import dataclass, field

@dataclass
class Vector3D:
    x: float = field(default=0.0)
    y: float = field(default=0.0)
    z: float = field(default=0.0)

@dataclass
class IMUData:
    accel: Vector3D
    gyro: Vector3D
    mag: Vector3D

class TelemetryHandler(QObject):
    on_data = pyqtSignal(IMUData)
    on_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def handle_serial_data(self, data: bytearray):
        try:
            # Assuming the data format is "accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z"
            decoded_data = data.decode('utf-8').strip()
            values = list(map(float, decoded_data.split(',')))
            if len(values) == 9:
                imu_data = IMUData(
                    accel=Vector3D(values[0], values[1], values[2]),
                    gyro=Vector3D(values[3], values[4], values[5]),
                    mag=Vector3D(values[6], values[7], values[8])
                )
                self.on_data.emit(imu_data)
        except Exception as e:
            self.on_error.emit(f"Error processing telemetry data: {e}")