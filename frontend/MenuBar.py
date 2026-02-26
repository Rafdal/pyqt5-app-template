from PyQt6.QtWidgets import QMainWindow, QMenuBar, QLabel, QPushButton, QMessageBox
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt

from backend.MainModel import MainModel
from frontend.widgets.SettingsDialog import SettingsDialog
from frontend.widgets.IconButtons import SwitchThemeButton
from frontend.widgets.SerialPortMenu import SerialPortMenuDialog

class CreateMenuBar():
    def __init__(self, main: QMainWindow, menuBar: QMenuBar, model: MainModel):
        menuBar.setNativeMenuBar(False)
        self.menuBar = menuBar
        self.model = model
        self.main = main

        self.create_fileMenu()
        self.create_serialMenu()

        # menuBar.addSeparator()
        self.themeBtn = SwitchThemeButton()
        self.themeBtn.update(selected=self.model.settings["dark_mode"])
        self.themeBtn.on_click.connect(self.toggle_theme)

        menuBar.setCornerWidget(self.themeBtn, Qt.Corner.TopRightCorner)


    def create_fileMenu(self):
        fileMenu = self.menuBar.addMenu('&File')
        if fileMenu is None:
            raise Exception("Failed to create File menu")
        
        settingsAction = QAction(QIcon('settings.png'), '&Settings', self.main)
        dialog = SettingsDialog(title="Settings", settings=self.model.settings)
        settingsAction.triggered.connect(lambda: dialog.exec())
        fileMenu.addAction(settingsAction)

        exitAction = QAction(QIcon('exit.png'), '&Exit', self.main)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.main.close)

        fileMenu.addAction(exitAction)


    def create_serialMenu(self):
        serialMenu = self.menuBar.addMenu('&Serial')
        if serialMenu is None:
            raise Exception("Failed to create Serial menu")
        
        openSerialAction = QAction('Open Serial Port', self.main)
        openSerialAction.triggered.connect(lambda: SerialPortMenuDialog(self.model.serial).exec())
        toggleDTRAction = QAction('Toggle DTR/RTS', self.main)
        toggleDTRAction.triggered.connect(lambda: self.model.serial.toggle_dtr_rts())
        closeSerialAction = QAction('Close Port', self.main)
        closeSerialAction.setEnabled(False) # Initially disabled, will be enabled when a port is connected
        closeSerialAction.triggered.connect(self.confirm_close_port)
        killPortAction = QAction('Kill Port', self.main)
        killPortAction.triggered.connect(self.confirm_kill_port)
        serialMenu.addAction(openSerialAction)
        serialMenu.addAction(toggleDTRAction)
        serialMenu.addAction(closeSerialAction)
        serialMenu.addSeparator()
        serialMenu.addAction(killPortAction)

        self.model.serial.connected.connect(lambda status: closeSerialAction.setEnabled(status))  # Enable/disable Close Port based on connection status
        self.model.serial.connected.connect(lambda status: killPortAction.setEnabled(status))  # Enable/disable Kill Port based on connection status

    def confirm_close_port(self):
        """Show confirmation dialog before closing port"""
        port_name = self.model.serial.selected_port.name if hasattr(self.model.serial, 'selected_port') and self.model.serial.selected_port else "current port"
        reply = QMessageBox.question(
            self.main, 
            'Close Port Confirmation',
            f'Are you sure you want to close {port_name}?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.model.serial.disconnect()

    def confirm_kill_port(self):
        """Show confirmation dialog before killing port"""
        port_name = self.model.serial.selected_port.name if hasattr(self.model.serial, 'selected_port') and self.model.serial.selected_port else "current port"
        reply = QMessageBox.question(
            self.main, 
            'Kill Port Confirmation',
            f'Are you sure you want to kill {port_name}? This will forcefully close the port and may cause issues if the port is in use.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.model.serial.kill_port()

    def toggle_theme(self, selected):
        self.model.settings["dark_mode"] = selected
        self.model.settings.apply()
        self.model.settings.save()