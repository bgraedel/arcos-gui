"""Collection of various functions for the GUI."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from napari.qt import get_stylesheet
from napari.settings import get_settings
from qtpy.QtCore import Qt, QTimer, Signal
from qtpy.QtGui import QValidator
from qtpy.QtWidgets import (
    QAction,
    QCheckBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMenuBar,
    QPushButton,
    QVBoxLayout,
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


class DirectoryInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter Directory Path")
        layout = QVBoxLayout(self)

        self.line_edit = QLineEdit(self)
        layout.addWidget(self.line_edit)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)


class MenuBarWidget(QMenuBar):
    go_to_directory = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.navigate_menu = QMenu("Navigate", self)

        # Add predefined directories as actions
        self.home_action = QAction("Home", self)
        self.home_action.triggered.connect(self._go_home)
        self.navigate_menu.addAction(self.home_action)

        # Add action to navigate to a custom directory
        self.custom_dir_action = QAction("Go to directory...", self)
        self.custom_dir_action.triggered.connect(self._open_directory_input)
        self.navigate_menu.addAction(self.custom_dir_action)

        self.addMenu(self.navigate_menu)

    def _go_home(self):
        # Signal or method to set the directory to home
        self.go_to_directory.emit(".")

    def _open_directory_input(self):
        dialog = DirectoryInputDialog(self)
        if dialog.exec_():
            path = dialog.line_edit.text()
            self.go_to_directory.emit(path)


class SelectionCheckboxWidget(QWidget):
    def __init__(self, selection_values, parent=None):
        super().__init__(parent)

        layout = QGridLayout(self)
        self.selection_title = QLabel("Select:")
        layout.addWidget(self.selection_title, 0, 0, 1, 4)

        self.selectAllCheckbox = QCheckBox("Select All")
        self.selectAllCheckbox.setChecked(True)
        layout.addWidget(self.selectAllCheckbox, 1, 0, 1, 4)

        self.checkboxes = {}
        for index, value in enumerate(selection_values):
            self.checkboxes[value] = QCheckBox(value.replace("_", " ").title())
            self.checkboxes[value].setChecked(True)
            row = 2 + index // 5
            col = index % 5
            layout.addWidget(self.checkboxes[value], row, col)

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


class SelectionDialog(QFileDialog):
    def __init__(self, selection_values, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setOption(QFileDialog.DontUseNativeDialog, True)

        # Menu bar
        self.menu_bar = MenuBarWidget(self)
        self.layout().setMenuBar(self.menu_bar)

        # Checkboxes
        self.selection_widget = SelectionCheckboxWidget(selection_values, self)
        self.layout().addWidget(self.selection_widget, 4, 0, 1, 4)

        # Connect signals
        self.menu_bar.go_to_directory.connect(self.setDirectory)

        style_sheet = get_stylesheet(get_settings().appearance.theme)
        self.setStyleSheet(style_sheet)

    def navigate_to_custom_directory(self):
        self.menu_bar._open_directory_input()

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
        self.checkboxes = self.selection_widget.checkboxes
        self.setFileMode(QFileDialog.Directory)
        self.setOption(QFileDialog.ShowDirsOnly, True)
        self.setWindowTitle("Select Folder to Batch Process")
        self.selection_widget.selection_title.setText("Select what to export:")


class ParameterFileDialog(SelectionDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checkboxes = self.selection_widget.checkboxes
        self.setFileMode(QFileDialog.ExistingFile)
        self.setOption(QFileDialog.ShowDirsOnly, False)
        # filter for .yaml files
        self.setNameFilter("*.yaml")
        self.setWindowTitle("Select Parameter File")
        self.selection_widget.selection_title.setText("Select what to import:")


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
