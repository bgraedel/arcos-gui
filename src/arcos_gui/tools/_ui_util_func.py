"""Collection of various functions for the GUI."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from napari.qt import get_stylesheet
from napari.settings import get_settings
from qtpy.QtCore import Qt, QTimer
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


class SelectionDialog(QFileDialog):
    def __init__(self, selection_values, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Use non-native file dialog to allow customizations
        self.setOption(QFileDialog.DontUseNativeDialog, True)

        # Create a new grid layout for your widgets
        layout = QGridLayout()
        self.selection_title = QLabel("Select:")

        # Create and add a label to the first row
        layout.addWidget(self.selection_title, 0, 0, 1, 4)

        # Create and add "Select All" checkbox above the selection_values checkboxes
        self.selectAllCheckbox = QCheckBox("Select All")
        self.selectAllCheckbox.setTristate(False)
        self.selectAllCheckbox.setChecked(True)
        layout.addWidget(self.selectAllCheckbox, 1, 0, 1, 4)

        self.checkboxes = {}
        for index, value in enumerate(selection_values):
            self.checkboxes[value] = QCheckBox(value.replace("_", " ").title())
            self.checkboxes[value].setChecked(True)

            row = 2 + index // 5  # Compute the row, starting from the 3rd row
            col = index % 5  # Compute the column, up to 4 columns

            layout.addWidget(self.checkboxes[value], row, col)

        # Add expanding spacers to the right of your widgets
        layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum),
            0,
            len(selection_values),
        )
        layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum),
            1,
            len(selection_values),
        )

        # Get the existing layout and add your layout to it
        self.layout().addWidget(QWidget(), 3, 0)  # Add a spacer widget
        self.layout().addLayout(
            layout, 4, 0, 1, 4
        )  # Adjust row and column indices as needed

        # Connect "Select All" checkbox to selectAll function
        self.selectAllCheckbox.stateChanged.connect(self.selectAll)
        # Connect each individual checkbox to updateSelectAllState function
        for checkbox in self.checkboxes.values():
            checkbox.stateChanged.connect(self.updateSelectAllState)

        # Set stylesheet
        style_sheet = get_stylesheet(get_settings().appearance.theme)
        self.setStyleSheet(style_sheet)

        # Override mousePressEvent for selectAllCheckbox
        def new_mousePressEvent(
            event, original_method=self.selectAllCheckbox.mousePressEvent
        ):
            if self.selectAllCheckbox.checkState() == Qt.Unchecked:
                self.selectAllCheckbox.setCheckState(Qt.Checked)
            else:
                original_method(event)

        self.selectAllCheckbox.mousePressEvent = new_mousePressEvent

    def selectAll(self, state):
        if state == Qt.PartiallyChecked:
            return  # Ignore partially checked state

        isChecked = state == Qt.Checked

        # Block signals from individual checkboxes to prevent recursion
        for checkbox in self.checkboxes.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(isChecked)
            checkbox.blockSignals(False)

        # Now, update the "Select All" checkbox without triggering its signal
        self.selectAllCheckbox.blockSignals(True)
        self.selectAllCheckbox.setCheckState(Qt.Checked if isChecked else Qt.Unchecked)
        self.selectAllCheckbox.blockSignals(False)

    def updateSelectAllState(self):
        checkedCount = sum(
            1 for checkbox in self.checkboxes.values() if checkbox.isChecked()
        )

        # Update the state of selectAllCheckbox without triggering its signal
        self.selectAllCheckbox.blockSignals(True)
        if checkedCount == 0:
            self.selectAllCheckbox.setCheckState(Qt.Unchecked)
        elif checkedCount == len(self.checkboxes):
            self.selectAllCheckbox.setCheckState(Qt.Checked)
        else:
            self.selectAllCheckbox.setCheckState(Qt.PartiallyChecked)
        self.selectAllCheckbox.blockSignals(False)

    def get_selected_options(self):
        """Returns a list of selected checkboxes' values excluding the 'Select All' checkbox."""
        return [
            value
            for value, checkbox in self.checkboxes.items()
            if checkbox.isChecked() and value != "Select All"
        ]


class BatchFileDialog(SelectionDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFileMode(QFileDialog.Directory)
        self.setOption(QFileDialog.ShowDirsOnly, True)
        self.setWindowTitle("Select Folder to Batch Process")
        self.selection_title.setText("Select what to export:")


class ParameterFileDialog(SelectionDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFileMode(QFileDialog.ExistingFile)
        self.setOption(QFileDialog.ShowDirsOnly, False)
        # filter for .yaml files
        self.setNameFilter("*.yaml")
        self.setWindowTitle("Select Parameter File")
        self.selection_title.setText("Select what to import:")


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
