from PyQt6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QWidget, QScrollArea, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Optional

from .BasicWidgets import SwitchButton, IntNumberInput, DropDownMenu, TextInput

from utils.ParamList import ParameterList, TextParam, NumParam, ChoiceParam, BoolParam, ConstParam

class DynamicSettingsWidget(QWidget):
    paramList: Optional[ParameterList]
    on_edit = pyqtSignal()

    def __init__(self, paramList: Optional[ParameterList]=None, title=None, submit_on_slider_move=False, on_edit=None):
        super().__init__()
        self.paramList = paramList
        if on_edit is not None:
            self.on_edit.connect(on_edit)
        self.title = title
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.sliderRelease = not submit_on_slider_move
        self.initUI()

    def initUI(self):
        self.dynamicLayout = QVBoxLayout()
        self.dynamicLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.dynamicLayout.setContentsMargins(0, 0, 0, 0)
        self.dynamicLayout.setSpacing(0)

        hlayout = QHBoxLayout()
        hlayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        hlayout.addLayout(self.dynamicLayout)

        # Create a new widget for the scroll area
        scroll_widget = QWidget()
        scroll_widget.setLayout(hlayout)
        scroll_widget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        # Create a scroll area and set its widget
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(scroll_widget)
        self.scroll_area.setMinimumHeight(250)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)
        self.updateUI(self.paramList, self.title)

    def updateUI(self, paramList: Optional[ParameterList], title="Dynamic Settings"):
        self.paramList = paramList
        while self.dynamicLayout.count():
            child = self.dynamicLayout.takeAt(0)
            if child is None:
                continue
            child_widget = child.widget()
            if child_widget is not None:
                child_widget.deleteLater()
            child_layout = child.layout()
            if child_layout is not None:
                while child_layout.count():
                    grandchild = child_layout.takeAt(0)
                    if grandchild is None:
                        continue
                    grandchild_widget = grandchild.widget()
                    if grandchild_widget is not None:
                        grandchild_widget.deleteLater()
                    grandchild_layout = grandchild.layout()
                    if grandchild_layout is not None:
                        while grandchild_layout.count():
                            grandgrandchild = grandchild_layout.takeAt(0)
                            if grandgrandchild is None:
                                continue
                            grandgrandchild_widget = grandgrandchild.widget()
                            if grandgrandchild_widget is not None:
                                grandgrandchild_widget.deleteLater()
        
        max_widget_width = 200
        if title is not None:
            titleLabel = QLabel(title)
            font = QFont("Arial", 14, QFont.Weight.Bold)
            titleLabel.setFont(font)
            self.dynamicLayout.addWidget(titleLabel)
            max_widget_width = titleLabel.sizeHint().width() + titleLabel.frameWidth() * 2

        if self.paramList is None:
            return

        for param in self.paramList:
            key = param.name
            
            settingWidget = None
            if not param.render:
                continue
            elif param.type == "Boolean":
                settingWidget = SwitchButton(param.text + " On", param.text + " Off", 
                                      on_click=lambda v, k=key: self.on_param_set(k, v), value=param.value)

            elif param.type == "Number":
                settingWidget = IntNumberInput(param.text, interval=param.interval, step=param.step, default=param.value, 
                                    sliderRelease=self.sliderRelease)
                settingWidget.on_change.connect(lambda v, k=key: self.on_param_set(k, v))
                settingWidget.on_settings_change.connect(lambda settings, k=key: self.on_param_settings_change(k, settings))
            
            elif param.type == "Choice":
                opt_dict = {}
                for opt in param.options:
                    opt_dict[opt] = opt

                settingWidget = QWidget()
                dropLayout = QHBoxLayout()
                dropLayout.addWidget(QLabel(param.text + ": "))
                dropLayout.addWidget(DropDownMenu(self.paramList[key], options=opt_dict, 
                                      onChoose=lambda v, _, k=key: self.on_param_set(k, v)))
                settingWidget.setLayout(dropLayout)

            elif param.type == "text":
                settingWidget = TextInput(param.text, 
                                          default=param.value,
                                          regex=param.regex)
                settingWidget.on_change.connect(lambda v, k=key: self.on_param_set(k, v))
            elif param.type == "const":
                settingWidget = QLabel(param.text + ": " + str(param.value))
            else:
                raise ValueError(f"Parameter type '{param.type}' not recognized")
            
            current_width = settingWidget.sizeHint().width()
            frame_width_fn = getattr(settingWidget, "frameWidth", None)
            if callable(frame_width_fn):
                frame_width = frame_width_fn()
                if isinstance(frame_width, int):
                    current_width += frame_width * 2
            max_widget_width = max(max_widget_width, current_width)
            self.dynamicLayout.addWidget(settingWidget)

        # Resize the scroll area to fit the new content
        margins = self.dynamicLayout.contentsMargins().left() + self.dynamicLayout.contentsMargins().right()
        frameWidth = self.scroll_area.frameWidth()
        scrollbar = self.scroll_area.verticalScrollBar()
        barWidth = scrollbar.sizeHint().width() if scrollbar is not None else 0
        scroll_width = int(max_widget_width*1.2) + 2*frameWidth + barWidth + margins
        self.scroll_area.setMinimumWidth(scroll_width)

    def on_param_set(self, key, value):
        if self.paramList is None:
            return
        self.paramList[key] = value
        self.on_edit.emit()

    def on_param_settings_change(self, key, settings):
        print(f"Settings for '{key}' changed: {settings}")
        self.paramList[key].data = settings