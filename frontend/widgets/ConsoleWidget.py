from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea, QHBoxLayout, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor, QTextOption
from frontend.widgets.BasicWidgets import TextInput, Button

class ConsoleWidget(QWidget):
    def __init__(self, textSelectable=True, wordWrap=True, defaultText="Console output will appear here...", fixedWidth=None, maxBlockCount=1000):
        super(ConsoleWidget, self).__init__()
        
        self.defaultText = defaultText

        self.setFixedWidth(fixedWidth) if fixedWidth else None
        
        # Create the QLabel that will display the console output
        self.consoleOutput = QTextEdit()
        self.consoleOutput.setReadOnly(True)
        self.consoleOutput.setWordWrapMode(
            QTextOption.WrapMode.WordWrap if wordWrap else QTextOption.WrapMode.NoWrap
        )
        self.consoleOutput.setFont(QFont("Monospace", 10))
        self.consoleOutput.setText(defaultText + '\n')
        self.consoleOutput.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        if textSelectable:
            self.consoleOutput.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        self.consoleOutput.document().setMaximumBlockCount(maxBlockCount)
        
        self.lineCount = QLabel("Lines: 0")
        
        # Create a QVBoxLayout for this widget and add the QScrollArea to it
        vlayout = QVBoxLayout(self)
        topHLayout = QHBoxLayout()
        topHLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        topHLayout.addWidget(self.lineCount)
        topHLayout.addStretch(1)
        topHLayout.addWidget(Button("Clear Console", on_click=lambda: self.clearConsole()))
        vlayout.addLayout(topHLayout)
        vlayout.addWidget(self.consoleOutput)
        
        # Set the layout for this widget
        self.setLayout(vlayout)
        
        # Additional styling or functionality can be added here as needed

    def clear(self):
        self.clearConsole()

    def clearConsole(self):
        self.consoleOutput.clear()
        self.setText(self.defaultText)

    def setText(self, text):
        self.consoleOutput.setText(text)
        newlines = text.count('\n')+1
        self.lineCount.setText(f"Lines: {newlines}")

    def appendText(self, text):
        # Method to append text to the console, improving performance for large updates
        self.consoleOutput.moveCursor(QTextCursor.End)
        self.consoleOutput.insertPlainText(text)
        # Update line count
        newlines = self.consoleOutput.toPlainText().count('\n') + 1
        self.lineCount.setText(f"Lines: {newlines}")