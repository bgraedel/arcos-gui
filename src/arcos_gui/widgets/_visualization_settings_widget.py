from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from qtpy import QtWidgets, uic
from qtpy.QtCore import Qt
from superqt import QDoubleRangeSlider

if TYPE_CHECKING:
    import napari.viewer
    from arcos_gui.processing import DataStorage

# local imports
from arcos_gui.tools import ARCOS_LAYERS, get_layer_list
from napari.utils.colormaps import AVAILABLE_COLORMAPS
from scipy.spatial import KDTree

# icons
ICONS = Path(__file__).parent / "_icons"


class _layer_propertiesUI:
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

    def setup_ui(self):
        uic.loadUi(self.UI_FILE, self)  # load QtDesigner .ui file


class LayerPropertiesWidget(QtWidgets.QWidget, _layer_propertiesUI):
    def __init__(
        self,
        viewer: napari.viewer.Viewer,
        data_storage_instance: DataStorage,
        parent=None,
    ):
        super().__init__(parent)
        self.setup_ui()
        self.viewer = viewer
        self.data_storage_instance = data_storage_instance

        self.LUT.addItems(AVAILABLE_COLORMAPS)
        self.LUT.setCurrentText("inferno")
        self._init_ranged_sliderts()
        self._connect_ranged_sliders_to_spinboxes()
        self._init_size_contrast_callbacks()

    def _init_ranged_sliderts(self):
        """Initialize ranged sliders from superqt."""
        self.lut_slider = QDoubleRangeSlider(Qt.Horizontal)
        self.horizontalLayout_lut.addWidget(self.lut_slider)

        # set starting values
        self.lut_slider.setRange(0, 10)
        self.lut_slider.setValue((0, 10))

    def _handleSlider_lut_ValueChange(self):
        """Method to handle lut value changes."""
        slider_vals = self.lut_slider.value()
        self.min_lut_spinbox.setValue(slider_vals[0])
        self.max_lut_spinbox.setValue(slider_vals[1])

    def _handle_min_lut_box_ValueChange(self, value):
        """Method to handle lut min spinbox value change."""
        slider_vals = self.lut_slider.value()
        self.lut_slider.setValue((value, slider_vals[1]))

    def _handle_max_lut_box_ValueChange(self, value):
        """Method to handle lut max spinbox value change."""
        slider_vals = self.lut_slider.value()
        self.lut_slider.setValue((slider_vals[0], value))

    def _connect_ranged_sliders_to_spinboxes(self):
        """Connect ranged sliders to spinboxes."""
        self.lut_slider.valueChanged.connect(self._handleSlider_lut_ValueChange)
        self.min_lut_spinbox.valueChanged.connect(self._handle_min_lut_box_ValueChange)
        self.max_lut_spinbox.valueChanged.connect(self._handle_max_lut_box_ValueChange)

    def _init_size_contrast_callbacks(self):
        """Connects various callbacks that correspond to size,
        contrast and lut changes."""
        # execute LUT and point functions
        self.reset_lut.clicked.connect(self._reset_contrast)
        # update size and LUT
        self.lut_slider.valueChanged.connect(self._change_lut_colors)
        self.LUT.currentIndexChanged.connect(self._change_lut_colors)
        self.point_size.valueChanged.connect(self._change_size)
        self.data_storage_instance.original_data.value_changed_connect(
            self._set_default_point_size
        )
        self.data_storage_instance.original_data.value_changed_connect(
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
        min_max = self.data_storage_instance.min_max_meas
        # change slider values
        self.max_lut_spinbox.setMaximum(min_max[1])
        self.max_lut_spinbox.setMinimum(min_max[0])
        self.min_lut_spinbox.setMaximum(min_max[1])
        self.min_lut_spinbox.setMinimum(min_max[0])
        self.lut_slider.setRange(*min_max)
        self.max_lut_spinbox.setValue(min_max[1])
        self.min_lut_spinbox.setValue(min_max[0])

    def _change_lut_colors(self):
        """Method to update lut and corresponding lut mappings."""
        layer_list = get_layer_list(self.viewer)
        min_value = self.min_lut_spinbox.value()
        max_value = self.max_lut_spinbox.value()
        if ARCOS_LAYERS["all_cells"] in layer_list:
            self.viewer.layers[
                ARCOS_LAYERS["all_cells"]
            ].face_colormap = self.LUT.currentText()
            self.viewer.layers[ARCOS_LAYERS["all_cells"]].face_contrast_limits = (
                min_value,
                max_value,
            )
            self.viewer.layers[ARCOS_LAYERS["all_cells"]].refresh_colors()

    def _change_size(self):
        """Method to update size of points and shapes layers:
        concernts layers defined in ARCOS_LAYERS
        and if created ARCOS_LAYERS["event_boundingbox"].
        """
        layer_list = get_layer_list(self.viewer)
        size = self.point_size.value()
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
        x_coord = self.data_storage_instance.columns.x_column
        y_coord = self.data_storage_instance.columns.y_column
        frame_col = self.data_storage_instance.columns.frame_column

        if not data.empty:
            data_po_np = data[data[frame_col] == 0][[x_coord, y_coord]].to_numpy()
            avg_nn_dist = (
                KDTree(data_po_np).query(data_po_np, k=2)[0][:, 1].mean() * 0.75
            )

            self.point_size.setValue(avg_nn_dist)

            self.data_storage_instance.point_size = avg_nn_dist


if __name__ == "__main__":
    import sys

    from arcos_gui.processing import DataStorage  # noqa: F811
    from napari import Viewer

    viewer = Viewer()
    app = QtWidgets.QApplication(sys.argv)
    widget = LayerPropertiesWidget(viewer, DataStorage(), parent=None)
    widget.show()
    sys.exit(app.exec_())
