from PyQt6.QtWidgets import QVBoxLayout, QWidget
from PyQt6.QtCore import pyqtSignal

import pyqtgraph as pg
import numpy as np


class LivePlotWidget(QWidget):
    regionChanged = pyqtSignal(float, float)

    def __init__(
        self,
        navHeight=100,
        enable_region=True,
        initial_region=None,
        max_points=None,
        max_visible_points=None,
        auto_adjust_on_new_data=True,
    ):
        super().__init__()
        self.enable_region = bool(enable_region)
        self.max_points = max_points
        self.max_visible_points = max_visible_points
        self.auto_adjust_on_new_data = bool(auto_adjust_on_new_data)
        self._x = np.array([], dtype=float)
        self._y = np.array([], dtype=float)
        self._sync_targets = []
        self._sync_guard = False

        self.plotLayoutWidget = pg.GraphicsLayoutWidget()
        self.plotLayout = self.plotLayoutWidget.ci
        self.mainPlot = self.plotLayout.addPlot(row=1, col=0)
        self.navPlot = self.plotLayout.addPlot(row=2, col=0)

        self.mainCurve = self.mainPlot.plot([], [])
        self.navCurve = self.navPlot.plot([], [])

        self.mainPlot.showGrid(x=True, y=True)
        self.mainPlot.setLabel('bottom', 'Time', units='s')
        self.navPlot.setLabel('bottom', 'Time', units='s')
        self.navPlot.setMaximumHeight(navHeight)

        self.mainPlot.getViewBox().setMouseEnabled(y=False, x=True)
        self.navPlot.getViewBox().setMouseEnabled(y=False, x=False)

        self.region = pg.LinearRegionItem(pen=pg.mkPen('y', width=3))
        self.region.setZValue(10)

        if self.enable_region:
            self.navPlot.addItem(self.region, ignoreBounds=True)
            self.region.sigRegionChanged.connect(self._on_region_changed)
            self.mainPlot.sigRangeChanged.connect(self._on_main_range_changed)

        if initial_region is not None and self.enable_region:
            self.set_region(*initial_region, emit=False)

        layout = QVBoxLayout()
        layout.addWidget(self.plotLayoutWidget)
        self.setLayout(layout)

    def set_data(self, x, y, auto_range=None):
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

        if x.size == 0 or y.size == 0:
            return
        if x.size != y.size:
            raise ValueError('x and y must have the same length')

        if self.max_points is not None and x.size > self.max_points:
            x = x[-self.max_points:]
            y = y[-self.max_points:]

        self._x = x
        self._y = y
        self.mainCurve.setData(self._x, self._y)
        self.navCurve.setData(self._x, self._y)

        self._update_view(auto_range)

    def append_samples(self, x, y, auto_range=None):
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

        if x.size == 0 or y.size == 0:
            return
        if x.size != y.size:
            raise ValueError('x and y must have the same length')

        self._x = np.concatenate((self._x, x))
        self._y = np.concatenate((self._y, y))

        if self.max_points is not None and self._x.size > self.max_points:
            self._x = self._x[-self.max_points:]
            self._y = self._y[-self.max_points:]

        self.mainCurve.setData(self._x, self._y)
        self.navCurve.setData(self._x, self._y)

        self._update_view(auto_range)

    def append_sample(self, x, y, auto_range=None):
        self.append_samples([x], [y], auto_range=auto_range)

    def clear(self):
        self._x = np.array([], dtype=float)
        self._y = np.array([], dtype=float)
        self.mainCurve.setData([], [])
        self.navCurve.setData([], [])

    def autoRange(self):
        self.mainPlot.getViewBox().autoRange()
        self.navPlot.getViewBox().autoRange()
        if self.enable_region:
            x_range = self.mainPlot.getViewBox().viewRange()[0]
            self.set_region(*x_range, emit=False)

    def getViewRangeX(self):
        return tuple(self.mainPlot.getViewBox().viewRange()[0])

    def set_auto_adjust_on_new_data(self, enabled):
        self.auto_adjust_on_new_data = bool(enabled)

    def set_max_visible_points(self, max_visible_points):
        self.max_visible_points = max_visible_points

    def set_region(self, min_x, max_x, emit=True):
        if not self.enable_region:
            return

        lo = float(min(min_x, max_x))
        hi = float(max(min_x, max_x))

        self.region.blockSignals(True)
        self.region.setRegion((lo, hi))
        self.region.blockSignals(False)

        self._set_x_range(lo, hi)

        if emit:
            self.regionChanged.emit(lo, hi)
            self._propagate_region(lo, hi)

    def link_time_sync(self, other_widget, sync_region=True):
        if other_widget is None or other_widget is self:
            return
        self.mainPlot.getViewBox().setXLink(other_widget.mainPlot.getViewBox())
        if sync_region and self.enable_region and getattr(other_widget, 'enable_region', False):
            if other_widget not in self._sync_targets:
                self._sync_targets.append(other_widget)

    def _on_region_changed(self):
        rgn = np.asarray(self.region.getRegion(), dtype=float).ravel()
        lo = float(rgn[0])
        hi = float(rgn[1])
        self._set_x_range(lo, hi)
        self.regionChanged.emit(lo, hi)
        self._propagate_region(lo, hi)

    def _on_main_range_changed(self, _window, view_range):
        if not self.enable_region:
            return
        lo, hi = view_range[0]
        self.region.blockSignals(True)
        self.region.setRegion((float(lo), float(hi)))
        self.region.blockSignals(False)

    def _propagate_region(self, lo, hi):
        if self._sync_guard:
            return
        self._sync_guard = True
        try:
            for target in self._sync_targets:
                target.set_region(lo, hi, emit=False)
        finally:
            self._sync_guard = False

    def _update_view(self, auto_range):
        should_adjust = self.auto_adjust_on_new_data if auto_range is None else bool(auto_range)
        if not should_adjust:
            return

        if self.max_visible_points is None or self._x.size == 0:
            self.autoRange()
            return

        visible_count = min(int(self.max_visible_points), self._x.size)
        lo = float(self._x[-visible_count])
        hi = float(self._x[-1])

        if self.enable_region:
            self.set_region(lo, hi, emit=False)
        else:
            self._set_x_range(lo, hi)

    def _set_x_range(self, lo, hi):
        self.mainPlot.getViewBox().setXRange(float(lo), float(hi), padding=0)