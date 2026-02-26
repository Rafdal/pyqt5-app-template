from frontend.pages.BaseClassPage import BaseClassPage

from frontend.widgets.ConsoleWidget import ConsoleWidget
from frontend.widgets.InputTerminal import InputTerminal

class TerminalTestPage(BaseClassPage):
    title = "Terminal Test Page"

    def initUI(self, layout):
        # layout is a QVBoxLayout
        # you can access to the model here and its methods/attributes with self.model
        self.consoleWidget = ConsoleWidget()
        self.inputTerminal = InputTerminal()
        self.inputTerminal.returnPressed.connect(self.handleInput)

        layout.addWidget(self.consoleWidget)
        layout.addWidget(self.inputTerminal)

    def handleInput(self, inputText):
        self.consoleWidget.appendText(f"Input received: {inputText}\n")

    def on_tab_focus(self):
        # define what happens when the tab is focused (optional)
        pass

    def on_tab_unfocus(self):
        # define what happens when the tab is unfocused (optional)
        pass