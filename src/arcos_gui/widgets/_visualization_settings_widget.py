"""Visualization settings widget. Contains the layer properties widget and the loader for the UI file."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from arcos_gui.tools import ARCOS_LAYERS, ThrottledCallback, get_layer_list
from napari.utils.colormaps import AVAILABLE_COLORMAPS
from qtpy import QtWidgets, uic
from qtpy.QtCore import Qt
from scipy.spatial import KDTree
from superqt import QDoubleRangeSlider

if TYPE_CHECKING:
    import napari.viewer
    from arcos_gui.processing import DataStorage

# icons
ICONS = Path(__file__).parent / "_icons"


class _layer_properties_UI(QtWidgets.QWidget):
    UI_FILE = str(Path(__file__).parent.parent / "_ui" / "Layer_properties.ui")

    # The UI_FILE above contains these objects:

    point_size_label: QtWidgets.QLabel
    select_lut_label: QtWidgets.QLabel
    max_lut_mapping_label: QtWidgets.QLabel
    min_lut_mapping_label: QtWidgets.QLabel
    point_size: QtWidgets.QDoubleSpinBox
    LUT: QtWidgets.QComboBox
    max_lut: QtWidgets.QSlider
    max_lut_spinbox: QtWidgets.QDoubleSpinBox
    min_lut: QtWidgets.QSlider
    min_lut_spinbox: QtWidgets.QDoubleSpinBox
    reset_lut: QtWidgets.QPushButton
    layer_properties: QtWidgets.QGroupBox
    horizontalLayout_lut: QtWidgets.QHBoxLayout

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def _init_ranged_sliderts(self):
        """Initialize ranged sliders from superqt."""
        self.lut_slider = QDoubleRangeSlider(Qt.Horizontal)
        self.horizontalLayout_lut.addWidget(self.lut_slider)

        # set starting values
        self.lut_slider.setRange(0, 10)
        self.lut_slider.setValue((0, 10))

    def _handle_slider_lut_value_change(self):
        """Method to handle lut value changes."""
        slider_vals = self.lut_slider.value()
        self.min_lut_spinbox.setValue(slider_vals[0])
        self.max_lut_spinbox.setValue(slider_vals[1])

    def _handle_min_lut_box_value_change(self, value):
        """Method to handle lut min spinbox value change."""
        slider_vals = self.lut_slider.value()
        self.lut_slider.setValue((value, slider_vals[1]))

    def _handle_max_lut_box_value_change(self, value):
        """Method to handle lut max spinbox value change."""
        slider_vals = self.lut_slider.value()
        self.lut_slider.setValue((slider_vals[0], value))

    def _connect_ranged_sliders_to_spinboxes(self):
        """Connect ranged sliders to spinboxes."""
        self.lut_slider.valueChanged.connect(self._handle_slider_lut_value_change)
        self.min_lut_spinbox.valueChanged.connect(self._handle_min_lut_box_value_change)
        self.max_lut_spinbox.valueChanged.connect(self._handle_max_lut_box_value_change)

    def set_contrast_slider(self, min_max):
        self.max_lut_spinbox.setMaximum(min_max[1])
        self.max_lut_spinbox.setMinimum(min_max[0])
        self.min_lut_spinbox.setMaximum(min_max[1])
        self.min_lut_spinbox.setMinimum(min_max[0])
        self.lut_slider.setRange(*min_max)
        self.max_lut_spinbox.setValue(min_max[1])
        self.min_lut_spinbox.setValue(min_max[0])

    def setup_ui(self):
        """Setup UI. Loads it from ui file"""
        uic.loadUi(self.UI_FILE, self)
        self.LUT.addItems(AVAILABLE_COLORMAPS)
        self.LUT.setCurrentText("inferno")
        self._init_ranged_sliderts()
        self._connect_ranged_sliders_to_spinboxes()


class LayerpropertiesController:
    """Widget to handle layer properties related to the visualization."""

    def __init__(
        self,
        viewer: napari.viewer.Viewer,
        data_storage_instance: DataStorage,
        parent=None,
    ):
        self.widget = _layer_properties_UI(parent)
        self.viewer = viewer
        self.data_storage_instance = data_storage_instance

        self._init_size_contrast_callbacks()
        self._register_datastorage_update()

    def _init_size_contrast_callbacks(self):
        """Connects various callbacks that correspond to size,
        contrast and lut changes."""
        # execute LUT and point functions
        self.widget.reset_lut.clicked.connect(self._reset_contrast)
        # update size and LUT
        throttled_change_colors = ThrottledCallback(
            self._change_lut_colors, max_interval=0.1
        )
        throttled_change_size = ThrottledCallback(self._change_size, max_interval=0.1)
        self.widget.lut_slider.valueChanged.connect(throttled_change_colors)
        self.widget.LUT.currentIndexChanged.connect(throttled_change_colors)
        self.widget.point_size.valueChanged.connect(throttled_change_size)
        self.data_storage_instance.original_data.value_changed.connect(
            self._set_default_point_size
        )

        self.data_storage_instance.filtered_data.value_changed.connect(
            self._reset_contrast
        )
        self.data_storage_instance.original_data.value_changed.connect(
            self._reset_contrast
        )
        self.viewer.layers.events.emitters["inserted"].connect(
            self._set_chosen_settings
        )

    def _set_chosen_settings(self):
        """Sets chosen settings for layer properties."""
        self._change_size()
        self._change_lut_colors()

    def _reset_contrast(self):
        """updates values in lut mapping slider."""
        min_max = self.data_storage_instance.min_max_meas.value
        # change slider values
        self.widget.set_contrast_slider(tuple(min_max))

    def _change_lut_colors(self, min_max=None):
        """Method to update lut and corresponding lut mappings."""
        min_max = self.widget.lut_slider.value()
        layer_list = get_layer_list(self.viewer)
        if min_max is None:
            min_value = self.widget.min_lut_spinbox.value()
            max_value = self.widget.max_lut_spinbox.value()
        else:
            min_value = min_max[0]
            max_value = min_max[1]
        if ARCOS_LAYERS["all_cells"] in layer_list:
            self.viewer.layers[
                ARCOS_LAYERS["all_cells"]
            ].face_colormap = self.widget.LUT.currentText()
            self.viewer.layers[ARCOS_LAYERS["all_cells"]].face_contrast_limits = (
                min_value,
                max_value,
            )
            self.viewer.layers[ARCOS_LAYERS["all_cells"]].refresh_colors()

    def _change_size(self, point_size=None):
        """Method to update size of points and shapes layers:
        concernts layers defined in ARCOS_LAYERS
        and if created ARCOS_LAYERS["event_boundingbox"].
        """
        layer_list = get_layer_list(self.viewer)
        size = self.widget.point_size.value()
        if ARCOS_LAYERS["all_cells"] in layer_list:
            self.viewer.layers[ARCOS_LAYERS["all_cells"]].size = size

        if ARCOS_LAYERS["active_cells"] in layer_list:
            self.viewer.layers[ARCOS_LAYERS["active_cells"]].size = round(size / 2.5, 2)

        if ARCOS_LAYERS["collective_events_cells"] in layer_list:
            self.viewer.layers[ARCOS_LAYERS["collective_events_cells"]].size = round(
                size / 1.7, 2
            )

        if ARCOS_LAYERS["event_boundingbox"] in self.viewer.layers:
            self.viewer.layers[ARCOS_LAYERS["event_boundingbox"]].edge_width = size / 5

    def _set_default_point_size(self):
        """
        updates values in lut mapping sliders
        """
        data = self.data_storage_instance.original_data.value
        data = self.data_storage_instance.filtered_data.value
        x_coord = self.data_storage_instance.columns.value.x_column
        y_coord = self.data_storage_instance.columns.value.y_column
        frame_col = self.data_storage_instance.columns.value.frame_column

        if not data.empty:
            data_po_np = data[data[frame_col] == 0][[x_coord, y_coord]].to_numpy()
            # drop nan values
            data_po_np = data_po_np[~np.isnan(data_po_np).any(axis=1)]
            avg_nn_dist = (
                KDTree(data_po_np).query(data_po_np, k=2)[0][:, 1].mean() * 0.75
            )

            self.widget.point_size.setValue(avg_nn_dist)
            self.data_storage_instance.point_size.value = float(avg_nn_dist)

    def _update_lut_value(self):
        """Updates widget values."""
        self.data_storage_instance.toggle_callback_block(True)
        self.widget.LUT.setCurrentText(self.data_storage_instance.lut.value)
        self.data_storage_instance.toggle_callback_block(False)
        self._reset_contrast()

    def _update_size_value(self):
        """Updates widget values."""
        self.data_storage_instance.toggle_callback_block(True)
        self.widget.point_size.setValue(self.data_storage_instance.point_size.value)
        self.data_storage_instance.toggle_callback_block(False)

    def _update_contrast_value(self):
        """Updates widget values."""
        self.data_storage_instance.toggle_callback_block(True)
        self.widget.set_contrast_slider(
            tuple(self.data_storage_instance.min_max_meas.value)
        )
        self.data_storage_instance.toggle_callback_block(False)
        self._change_lut_colors()

    def _update_ds_with_data(self):
        """Updates data storage with data."""
        self.data_storage_instance.toggle_callback_block(True)
        self.data_storage_instance.point_size.value = self.widget.point_size.value()
        self.data_storage_instance.lut.value = self.widget.LUT.currentText()
        self.data_storage_instance.min_max_meas.value = [
            self.widget.min_lut_spinbox.minimum(),
            self.widget.max_lut_spinbox.maximum(),
        ]
        self.data_storage_instance.toggle_callback_block(False)

    def _register_datastorage_update(self):
        """Registers data storage update."""
        self.data_storage_instance.point_size.value_changed.connect(
            self._update_size_value
        )
        self.data_storage_instance.lut.value_changed.connect(self._update_lut_value)
        self.data_storage_instance.min_max_meas.value_changed.connect(
            self._update_contrast_value
        )

        for spinbox in [
            self.widget.point_size,
            self.widget.min_lut_spinbox,
            self.widget.max_lut_spinbox,
        ]:
            spinbox.valueChanged.connect(self._update_ds_with_data)

        self.widget.LUT.currentIndexChanged.connect(self._update_ds_with_data)


if __name__ == "__main__":
    import sys

    from arcos_gui.processing import DataStorage  # noqa: F811
    from napari import Viewer

    viewer = Viewer()
    app = QtWidgets.QApplication(sys.argv)
    controller = LayerpropertiesController(viewer, DataStorage(), parent=None)
    controller.widget.show()
    sys.exit(app.exec_())
