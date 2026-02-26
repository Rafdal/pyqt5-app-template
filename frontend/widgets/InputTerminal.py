from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from collections import deque

class InputTerminal(QLineEdit):
    returnPressed = pyqtSignal(str)  # Signal to emit when Enter is pressed
    include_endl = True  # Whether to include a newline character at the end of the input

    def __init__(self, parent=None):
        super(InputTerminal, self).__init__(parent)
        self.setPlaceholderText("Enter text here...")
        self.setFont(QFont("Monospace", 10))
        self.user_input_history = deque(maxlen=20)
        self.user_input_index = 0   # 0 means the last element in the deque, 1 means the second last, etc.

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            user_input = self.text()
            if user_input:
                self.user_input_history.append(user_input)
                self.user_input_index = 0
                self.clear()
                self.returnPressed.emit(user_input + ("\n" if self.include_endl else ""))  # Emit the signal with the user input and optional newline
            else:
                event.ignore()
        if event.key() == Qt.Key.Key_Up:
            if self.user_input_history:
                self.user_input_index += 1
                if self.user_input_index <= 1:
                    self.setText(self.user_input_history[-1])
                elif self.user_input_index >= len(self.user_input_history):
                    self.user_input_index = len(self.user_input_history) - 1
                else:
                    self.setText(self.user_input_history[-(self.user_input_index + 1)])
        if event.key() == Qt.Key.Key_Down:
            if self.user_input_history:
                self.user_input_index -= 1
                if self.user_input_index < 0:
                    self.user_input_index = 0
                    self.setText("")
                else:
                    self.setText(self.user_input_history[-(self.user_input_index + 1)])
        super(InputTerminal, self).keyPressEvent(event)