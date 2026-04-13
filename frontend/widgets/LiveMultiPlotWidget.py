from PyQt6.QtWidgets import QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal

import pyqtgraph as pg
import numpy as np

import typing as T

PenStyleName = T.Literal['solid', 'dash', 'dot', 'dashdot', 'dashdotdot']
LineStyleInput = T.Union[Qt.PenStyle, PenStyleName]
SeriesInput = T.Union[T.Sequence[float], np.ndarray]
YValuesInput = T.Union[SeriesInput, T.Sequence[SeriesInput], np.ndarray]
RegionTuple = T.Tuple[float, float]


class LiveMultiPlotWidget(QWidget):
    regionChanged = pyqtSignal(float, float)

    def __init__(
        self,
        line_count: int = 1,
        labels: T.Optional[T.Sequence[str]] = None,
        navHeight: int = 100,
        enable_region: bool = True,
        initial_region: T.Optional[RegionTuple] = None,
        buffer_size: T.Optional[int] = None,
        max_region_size: T.Optional[int] = None,
        auto_adjust_on_new_data: bool = True,
        stop_auto_adjust_on_click: bool = True,
    ) -> None:
        super().__init__()
        if int(line_count) < 1:
            raise ValueError('line_count must be >= 1')

        self.line_count: int = int(line_count)
        self.enable_region = bool(enable_region)
        self.buffer_size = buffer_size
        self.max_region_size = max_region_size
        self.auto_adjust_on_new_data = bool(auto_adjust_on_new_data)
        self.stop_auto_adjust_on_click = bool(stop_auto_adjust_on_click)

        self._x = np.array([], dtype=float)
        self._ys = np.empty((self.line_count, 0), dtype=float)

        self._sync_targets: T.List['LiveMultiPlotWidget'] = []
        self._sync_guard: bool = False
        self._background_color: T.Any = None

        self._line_labels: T.List[str] = self._build_labels(labels)
        self._line_pen_colors: T.List[T.Any] = [None] * self.line_count
        self._line_pen_widths: T.List[float] = [1.0] * self.line_count
        self._line_pen_styles: T.List[Qt.PenStyle] = [Qt.PenStyle.SolidLine] * self.line_count

        self.plotLayoutWidget = pg.GraphicsLayoutWidget()
        self.plotLayout = self.plotLayoutWidget.ci
        self.mainPlot = self.plotLayout.addPlot(row=1, col=0)

        self.mainPlot.addLegend()
        self.mainCurves: T.List[T.Any] = []
        for index in range(self.line_count):
            curve = self.mainPlot.plot([], [], pen=self._build_curve_pen(index), name=self._line_labels[index])
            self.mainCurves.append(curve)
        self.mainCurve = self.mainCurves[0]

        self.navCurves: T.List[T.Any] = []
        if self.enable_region:
            self.navPlot = self.plotLayout.addPlot(row=2, col=0)
            for index in range(self.line_count):
                curve = self.navPlot.plot([], [], pen=self._build_curve_pen(index))
                self.navCurves.append(curve)
            self.navCurve = self.navCurves[0]

        self.mainPlot.showGrid(x=True, y=True)
        self.mainPlot.setLabel('bottom', 'Time', units='s')
        if self.enable_region:
            self.navPlot.setLabel('bottom', 'Time', units='s')
            self.navPlot.setMaximumHeight(navHeight)

        self.mainPlot.getViewBox().setMouseEnabled(y=False, x=True)
        if self.enable_region:
            self.navPlot.getViewBox().setMouseEnabled(y=False, x=False)

        self.region = pg.LinearRegionItem(pen=pg.mkPen('y', width=3))
        self.region.setZValue(10)

        if self.stop_auto_adjust_on_click:
            self.mainPlot.sigRangeChangedManually.connect(self._on_range_changed_manually)
        if self.enable_region:
            self.navPlot.addItem(self.region, ignoreBounds=True)
            self.region.sigRegionChanged.connect(self._on_region_changed)
            self.mainPlot.sigRangeChanged.connect(self._on_main_range_changed)

            if self.stop_auto_adjust_on_click:
                def mouse_event(ev: T.Any) -> T.Any:
                    if ev.button() == pg.QtCore.Qt.MouseButton.LeftButton:
                        self.auto_adjust_on_new_data = False
                    return pg.ViewBox.mousePressEvent(self.mainPlot.getViewBox(), ev)

                self.region.mousePressEvent = lambda event: mouse_event(event)

        if initial_region is not None and self.enable_region:
            self.set_region(*initial_region, emit=False)

        layout = QVBoxLayout()
        layout.addWidget(self.plotLayoutWidget)
        self.setLayout(layout)

    def _build_labels(self, labels: T.Optional[T.Sequence[str]]) -> T.List[str]:
        if labels is None:
            return [f'Line {index + 1}' for index in range(self.line_count)]
        label_list = [str(value) for value in labels]
        if len(label_list) != self.line_count:
            raise ValueError('labels length must match line_count')
        return label_list

    def _validate_line_index(self, line_index: int) -> int:
        normalized = int(line_index)
        if normalized < 0 or normalized >= self.line_count:
            raise IndexError(f'line_index out of range: {line_index}')
        return normalized

    def _normalize_pen_style(self, line_style: T.Optional[LineStyleInput]) -> Qt.PenStyle:
        if line_style is None:
            return Qt.PenStyle.SolidLine
        if isinstance(line_style, Qt.PenStyle):
            return line_style
        if isinstance(line_style, str):
            style_map = {
                'solid': Qt.PenStyle.SolidLine,
                'dash': Qt.PenStyle.DashLine,
                'dot': Qt.PenStyle.DotLine,
                'dashdot': Qt.PenStyle.DashDotLine,
                'dashdotdot': Qt.PenStyle.DashDotDotLine,
            }
            normalized = line_style.strip().lower()
            if normalized in style_map:
                return style_map[normalized]
        raise ValueError('line_style must be Qt.PenStyle or one of: solid, dash, dot, dashdot, dashdotdot')

    def _build_curve_pen(self, line_index: int) -> T.Any:
        index = self._validate_line_index(line_index)
        return pg.mkPen(
            color=self._line_pen_colors[index],
            width=float(self._line_pen_widths[index]),
            style=self._line_pen_styles[index],
        )

    def _apply_curve_pens(self) -> None:
        for index in range(self.line_count):
            pen = self._build_curve_pen(index)
            self.mainCurves[index].setPen(pen)
            if self.enable_region:
                self.navCurves[index].setPen(pen)

    def _coerce_y_values(self, y_values: YValuesInput, expected_size: int) -> np.ndarray:
        y_array = np.asarray(y_values, dtype=float)

        if y_array.ndim == 1:
            if self.line_count == 1:
                if y_array.size != expected_size:
                    raise ValueError('x and y_values length must match')
                return y_array.reshape(1, expected_size)

            if expected_size == 1 and y_array.size == self.line_count:
                return y_array.reshape(self.line_count, 1)

            raise ValueError(
                'for multiple lines, pass y_values as 2D data; '
                'or pass a 1D vector of length line_count when len(x) == 1'
            )

        if y_array.ndim != 2:
            raise ValueError('y_values must be a 1D or 2D numeric array-like')

        if y_array.shape == (self.line_count, expected_size):
            return y_array
        if y_array.shape == (expected_size, self.line_count):
            return y_array.T

        raise ValueError(
            'y_values shape must be (line_count, len(x)) or (len(x), line_count)'
        )

    def _update_curve_names(self) -> None:
        for index, curve in enumerate(self.mainCurves):
            if hasattr(curve, 'setName'):
                curve.setName(self._line_labels[index])

    def set_labels(self, labels: T.Sequence[str]) -> None:
        self._line_labels = self._build_labels(labels)
        self._update_curve_names()

    def set_line_style(
        self,
        line_index: int,
        pen_color: T.Optional[T.Any] = None,
        line_width: T.Optional[float] = None,
        line_style: T.Optional[LineStyleInput] = None,
        label: T.Optional[str] = None,
    ) -> None:
        index = self._validate_line_index(line_index)

        if pen_color is not None:
            self._line_pen_colors[index] = pen_color
        if line_width is not None:
            self._line_pen_widths[index] = float(line_width)
        if line_style is not None:
            self._line_pen_styles[index] = self._normalize_pen_style(line_style)
        if label is not None:
            self._line_labels[index] = str(label)
            self._update_curve_names()

        pen = self._build_curve_pen(index)
        self.mainCurves[index].setPen(pen)
        if self.enable_region:
            self.navCurves[index].setPen(pen)

    def set_style(
        self,
        background_color: T.Optional[T.Any] = None,
        pen_color: T.Optional[T.Any] = None,
        line_width: T.Optional[float] = None,
        line_style: T.Optional[LineStyleInput] = None,
    ) -> None:
        if background_color is not None:
            self._background_color = background_color
            self.plotLayoutWidget.setBackground(background_color)

        if pen_color is not None:
            self._line_pen_colors = [pen_color] * self.line_count
        if line_width is not None:
            normalized_width = float(line_width)
            self._line_pen_widths = [normalized_width] * self.line_count
        if line_style is not None:
            normalized_style = self._normalize_pen_style(line_style)
            self._line_pen_styles = [normalized_style] * self.line_count

        self._apply_curve_pens()

    def set_buffer_size(self, buffer_size: T.Optional[int]) -> None:
        self.buffer_size = buffer_size
        if self.buffer_size is not None and self._x.size > self.buffer_size:
            self._x = self._x[-self.buffer_size:]
            self._ys = self._ys[:, -self.buffer_size:]
            self._refresh_curves()
            self._update_view(auto_range=False)

    def _refresh_curves(self) -> None:
        for index in range(self.line_count):
            self.mainCurves[index].setData(self._x, self._ys[index])
            if self.enable_region:
                self.navCurves[index].setData(self._x, self._ys[index])

    def set_data(self, x: SeriesInput, y_values: YValuesInput, auto_range: T.Optional[bool] = None) -> None:
        x = np.asarray(x, dtype=float)
        if x.size == 0:
            return

        ys = self._coerce_y_values(y_values, x.size)

        if self.buffer_size is not None and x.size > self.buffer_size:
            x = x[-self.buffer_size:]
            ys = ys[:, -self.buffer_size:]

        self._x = x
        self._ys = ys
        self._refresh_curves()

        self._update_view(auto_range)

    def append_samples(self, x: SeriesInput, y_values: YValuesInput, auto_range: T.Optional[bool] = None) -> None:
        x = np.asarray(x, dtype=float)
        if x.size == 0:
            return

        ys = self._coerce_y_values(y_values, x.size)

        self._x = np.concatenate((self._x, x))
        self._ys = np.concatenate((self._ys, ys), axis=1)

        if self.buffer_size is not None and self._x.size > self.buffer_size:
            self._x = self._x[-self.buffer_size:]
            self._ys = self._ys[:, -self.buffer_size:]

        self._refresh_curves()

        self._update_view(auto_range)

    def append_sample(self, x: float, y_values: YValuesInput, auto_range: T.Optional[bool] = None) -> None:
        self.append_samples([x], y_values, auto_range=auto_range)

    def clear(self) -> None:
        self._x = np.array([], dtype=float)
        self._ys = np.empty((self.line_count, 0), dtype=float)
        for index in range(self.line_count):
            self.mainCurves[index].setData([], [])
            if self.enable_region:
                self.navCurves[index].setData([], [])

    def autoRange(self) -> None:
        self.mainPlot.getViewBox().autoRange()
        if self.enable_region:
            self.navPlot.getViewBox().autoRange()
            x_range = self.mainPlot.getViewBox().viewRange()[0]
            self.set_region(*x_range, emit=False)

    def getViewRangeX(self) -> RegionTuple:
        x_range = self.mainPlot.getViewBox().viewRange()[0]
        return float(x_range[0]), float(x_range[1])

    def set_auto_adjust_on_new_data(self, enabled: bool) -> None:
        self.auto_adjust_on_new_data = bool(enabled)

    def set_max_region_size(self, max_region_size: T.Optional[int]) -> None:
        self.max_region_size = max_region_size

    def set_region(self, min_x: float, max_x: float, emit: bool = True) -> None:
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

    def link_time_sync(self, other_widget: T.Optional['LiveMultiPlotWidget'], sync_region: bool = True) -> None:
        if other_widget is None or other_widget is self:
            return
        self.mainPlot.getViewBox().setXLink(other_widget.mainPlot.getViewBox())
        if sync_region and self.enable_region and getattr(other_widget, 'enable_region', False):
            if other_widget not in self._sync_targets:
                self._sync_targets.append(other_widget)

    def _on_range_changed_manually(self, window: T.Any) -> None:
        if self.stop_auto_adjust_on_click:
            self.auto_adjust_on_new_data = False

    def _on_region_changed(self) -> None:
        rgn = np.asarray(self.region.getRegion(), dtype=float).ravel()
        lo = float(rgn[0])
        hi = float(rgn[1])
        self._set_x_range(lo, hi)
        self.regionChanged.emit(lo, hi)
        self._propagate_region(lo, hi)

    def _on_main_range_changed(self, _window: T.Any, view_range: T.Sequence[T.Sequence[float]]) -> None:
        if not self.enable_region:
            return
        lo, hi = view_range[0]
        self.region.blockSignals(True)
        self.region.setRegion((float(lo), float(hi)))
        self.region.blockSignals(False)

    def _propagate_region(self, lo: float, hi: float) -> None:
        if self._sync_guard:
            return
        self._sync_guard = True
        try:
            for target in self._sync_targets:
                target.set_region(lo, hi, emit=False)
        finally:
            self._sync_guard = False

    def _update_view(self, auto_range: T.Optional[bool]) -> None:
        should_adjust = self.auto_adjust_on_new_data if auto_range is None else bool(auto_range)
        if not should_adjust:
            return

        if self.max_region_size is None or self._x.size == 0:
            self.autoRange()
            return

        visible_count = min(int(self.max_region_size), self._x.size)
        lo = float(self._x[-visible_count])
        hi = float(self._x[-1])

        if self.enable_region:
            self.set_region(lo, hi, emit=False)
        else:
            self._set_x_range(lo, hi)

    def _set_x_range(self, lo: float, hi: float) -> None:
        self.mainPlot.getViewBox().setXRange(float(lo), float(hi), padding=0)
