"""Collection of various functions for the GUI."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from arcos_gui.tools._config import AVAILABLE_OPTIONS_FOR_BATCH
from napari.qt import get_stylesheet
from napari.settings import get_settings
from qtpy.QtCore import QTimer
from qtpy.QtGui import QValidator
from qtpy.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

if TYPE_CHECKING:
    import napari.viewer
    from qtpy import QtWidgets
    from superqt import QRangeSlider


class ThrottledCallback:
    def __init__(self, callback, max_interval):
        self.callback = callback
        self.max_interval = max_interval
        self.last_call_time = 0
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.args, self.kwargs = None, None

    def __call__(self, *args, **kwargs):
        current_time = time.time()
        self.args, self.kwargs = args, kwargs  # store the latest args and kwargs

        if current_time - self.last_call_time > self.max_interval:
            self.last_call_time = current_time
            self.callback(*self.args, **self.kwargs)
        else:
            self.timer.stop()
            self.timer.timeout.connect(self._timeout_callback)
            self.timer.start(int(self.max_interval * 1000))

    def _timeout_callback(self):
        self.last_call_time = time.time()
        self.callback(*self.args, **self.kwargs)
        self.timer.timeout.disconnect(self._timeout_callback)


class OutputOrderValidator(QValidator):
    def __init__(self, vColsCore, parent=None):
        super().__init__(parent)
        self.vColsCore = vColsCore
        self.required_chars = ["t", "x", "y"]
        self.allowed_chars = ["t", "x", "y", "z"]
        self.max_length = 4

    def validate(self, string, pos):
        if len(string) > self.max_length:
            return QValidator.Invalid, string, pos

        for char in string:
            if char not in self.allowed_chars:
                return QValidator.Invalid, string, pos

        if len(set(string)) != len(string):
            return QValidator.Invalid, string, pos

        if len(string) < len(self.vColsCore):
            return QValidator.Intermediate, string, pos

        for char in self.required_chars:
            if char not in string:
                return QValidator.Intermediate, string, pos

        return QValidator.Acceptable, string, pos


class BatchFileDialog(QFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Use non-native file dialog to allow customizations
        self.setOption(QFileDialog.DontUseNativeDialog, True)
        self.setFileMode(QFileDialog.Directory)
        self.setOption(QFileDialog.ShowDirsOnly, True)

        # Create a new grid layout for your widgets
        layout = QGridLayout()

        # Create and add a label to the first row
        layout.addWidget(
            QLabel("Select what to export"), 0, 0, 1, 4
        )  # Spanning across 4 columns

        # Create and add checkboxes to the second row
        self.checkboxes = {}
        values = AVAILABLE_OPTIONS_FOR_BATCH
        for index, value in enumerate(values):
            self.checkboxes[value] = QCheckBox(value.replace("_", " ").title())
            self.checkboxes[value].setChecked(True)
            layout.addWidget(self.checkboxes[value], 1, index)

        # Add expanding spacers to the right of your widgets
        layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum),
            0,
            len(values),
        )
        layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum),
            1,
            len(values),
        )

        # Get the existing layout and add your layout to it
        self.layout().addWidget(QWidget(), 3, 0)  # Add a spacer widget
        self.layout().addLayout(
            layout, 4, 0, 1, 4
        )  # Adjust row and column indices as needed

        # Set stylesheet
        style_sheet = get_stylesheet(get_settings().appearance.theme)
        self.setStyleSheet(style_sheet)


def remove_layers_after_columnpicker(viewer: napari.viewer.Viewer, arcos_layers: list):
    """Remove existing arcos layers before loading new data"""
    layer_list = get_layer_list(viewer)
    for layer in arcos_layers:
        if layer in layer_list:
            viewer.layers.remove(layer)


def get_layer_list(viewer: napari.viewer.Viewer):
    """Get list of open layers."""
    layer_list = [layer.name for layer in viewer.layers]
    return layer_list


def set_track_lenths(
    track_lenths_minmax: tuple,
    tracklenght_slider: QRangeSlider,
    min_tracklength_spinbox: QtWidgets.QDoubleSpinBox,
    max_tracklength_spinbox: QtWidgets.QDoubleSpinBox,
):
    """Set track length slider and spinboxes to min and max values of track lengths.

    Parameters
    ----------
    track_lenths_minmax : tuple
        Tuple of min and max track length.
    tracklenght_slider : QRangeSlider
    tracklenght_slider : QRangeSlider
    min_tracklength_spinbox : QtWidgets.QDoubleSpinBox
    max_tracklength_spinbox : QtWidgets.QDoubleSpinBox
    """
    if track_lenths_minmax[1] - track_lenths_minmax[0] > 1:
        tracklenght_slider.setMinimum(track_lenths_minmax[0])
        tracklenght_slider.setMaximum(track_lenths_minmax[1])

    min_tracklength_spinbox.setMinimum(track_lenths_minmax[0])
    max_tracklength_spinbox.setMinimum(track_lenths_minmax[0])

    min_tracklength_spinbox.setMaximum(track_lenths_minmax[1])
    max_tracklength_spinbox.setMaximum(track_lenths_minmax[1])

    min_tracklength_spinbox.setValue(track_lenths_minmax[0])
    max_tracklength_spinbox.setValue(track_lenths_minmax[1])
