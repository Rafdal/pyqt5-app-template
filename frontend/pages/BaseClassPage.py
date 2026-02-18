from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

from backend.MainModel import MainModel

# DO NOT MODIFY THIS CLASS
class BaseClassPage(QWidget):

    model: MainModel
    title: str
    layout: QVBoxLayout

    # DO NOT MODIFY THIS CLASS
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        if not hasattr(self, 'title'):
            raise Exception("All pages must have a title attribute")
    
    # DO NOT MODIFY THIS CLASS
    def initUI(self, layout: QVBoxLayout):
        raise NotImplementedError("initUI(self, layout) must be implemented in Page class")

    def set_model(self, model: MainModel):
        self.model = model

    def on_tab_focus(self):
        pass

    def on_tab_unfocus(self):
        pass