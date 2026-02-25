from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QPushButton, QWidget, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
import qtawesome as qta
import os

# Run `qta-browser` in terminal to see available icons and their names
import typing as T

class AlternatingIconButton(QLabel):
    on_click = pyqtSignal(bool)

    def __init__(self, icon0: str = "", icon1: str = "", color0: str = "red", color1: str = "red", size: int = 30):
        super().__init__()
        self.selected = False
        self.icon0 = icon0
        self.icon1 = icon1
        self.color0 = color0
        self.color1 = color1
        self._size = size
        self.setIcon(icon0, color0)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setContentsMargins(5, 2, 5, 2)
    
    def setIcon(self, icon, color):
        self.setPixmap(qta.icon(icon, color=color, size=self._size).pixmap(self._size, self._size))

    def update(self, selected=None):
        if selected is not None:
            self.selected = selected
        if self.selected:
            self.setIcon(self.icon1, self.color1)
        else:
            self.setIcon(self.icon0, self.color0)

    def mousePressEvent(self, a0: QMouseEvent | None) -> None:
        self.selected = not self.selected
        self.on_click.emit(self.selected)
        self.update()
        return super().mousePressEvent(a0)


class SwitchThemeButton(AlternatingIconButton):
    def __init__(self):
        super().__init__(icon0="mdi6.theme-light-dark", icon1="mdi6.theme-light-dark", color0="black", color1="white")
        self.selected = True    # Start with dark mode selected
        self.setIcon(self.icon1, self.color1)

        self.setToolTip("Toggle between light and dark themes")


class ToolButton(QLabel):
    on_click = pyqtSignal()

    def __init__(self, icon: str, color: T.Union[str, None] = None, size: int = 30):
        super().__init__()
        self.icon = icon
        self.color = color if color is not None else os.getenv("QTMATERIAL_PRIMARYCOLOR", "black")
        self._size = size
        self.setIcon(icon, self.color)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setContentsMargins(2, 2, 2, 2)

    def changeEvent(self, a0: QEvent | None) -> None:
        if a0 is not None and a0.type() == QEvent.Type.PaletteChange:
            self.color = os.getenv("QTMATERIAL_PRIMARYCOLOR", "black")
            self.setIcon(self.icon, self.color)
        return super().changeEvent(a0)
    
    def setIcon(self, icon, color):
        self.setPixmap(qta.icon(icon, color=color, size=self._size).pixmap(self._size, self._size))

    def mousePressEvent(self, a0: QMouseEvent | None) -> None:
        self.on_click.emit()
        return super().mousePressEvent(a0)