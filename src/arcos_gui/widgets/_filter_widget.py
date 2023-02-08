from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from arcos_gui.processing import filter_data, get_tracklengths
from arcos_gui.tools import (
    ARCOS_LAYERS,
    remove_layers_after_columnpicker,
    set_track_lenths,
)
from napari.utils.notifications import show_info
from qtpy import QtWidgets, uic
from qtpy.QtCore import Qt
from superqt import QRangeSlider

if TYPE_CHECKING:
    from arcos_gui.processing import DataStorage
    from napari.viewer import Viewer


class _filter_dataUI:
    UI_FILE = str(Path(__file__).parent.parent / "_ui" / "filter_data.ui")

    # The UI_FILE above contains these objects:
    frame_interval_label: QtWidgets.QLabel
    tracklength_label: QtWidgets.QLabel
    position_label: QtWidgets.QLabel
    position: QtWidgets.QComboBox
    additional_filter_combobox: QtWidgets.QComboBox
    additional_filter_combobox_label: QtWidgets.QLabel
    frame_interval: QtWidgets.QSpinBox
    min_tracklength: QtWidgets.QSlider
    min_tracklength_spinbox: QtWidgets.QDoubleSpinBox
    max_tracklength: QtWidgets.QSlider
    max_tracklength_spinbox: QtWidgets.QDoubleSpinBox
    filter_groupBox: QtWidgets.QGroupBox
    filter_input_data: QtWidgets.QPushButton
    horizontalLayout_tracklength: QtWidgets.QHBoxLayout

    def setup_ui(self):
        uic.loadUi(self.UI_FILE, self)  # load QtDesigner .ui file


class FilterDataWidget(QtWidgets.QWidget, _filter_dataUI):
    def __init__(self, viewer: Viewer, data_storage_instance: DataStorage, parent=None):
        super().__init__(parent)
        self.viewer = viewer
        self.setup_ui()
        self._init_ranged_sliderts()
        self._connect_ranged_sliders_to_spinboxes()

        self.data_storage_instance = data_storage_instance
        self.data_storage_instance.original_data.value_changed_connect(
            self._original_data_changed
        )
        self._set_defaults()
        self.filter_input_data.clicked.connect(self._filter_data)

    def _init_ranged_sliderts(self):
        """Initialize ranged sliders from superqt."""
        self.tracklenght_slider = QRangeSlider(Qt.Horizontal)
        self.horizontalLayout_tracklength.addWidget(self.tracklenght_slider)

        # set starting values
        self.tracklenght_slider.setRange(0, 10)
        self.tracklenght_slider.setValue((0, 10))

    def _handleSlider_tracklength_ValueChange(self):
        """Method to handle trancklenght value changes."""
        slider_vals = self.tracklenght_slider.value()
        self.min_tracklength_spinbox.setValue(slider_vals[0])
        self.max_tracklength_spinbox.setValue(slider_vals[1])

    def _handle_min_tracklenght_box_ValueChange(self, value):
        """Method to handle min tracklenght spinbox."""
        slider_vals = self.tracklenght_slider.value()
        self.tracklenght_slider.setValue((value, slider_vals[1]))

    def _handle_max_tracklength_box_ValueChange(self, value):
        """Method to handle max tracklength spinbox."""
        slider_vals = self.tracklenght_slider.value()
        self.tracklenght_slider.setValue((slider_vals[0], value))

    def _connect_ranged_sliders_to_spinboxes(self):
        """Method to connect ranged sliders to spinboxes to sync values."""
        self.tracklenght_slider.valueChanged.connect(
            self._handleSlider_tracklength_ValueChange
        )
        self.min_tracklength_spinbox.valueChanged.connect(
            self._handle_min_tracklenght_box_ValueChange
        )
        self.max_tracklength_spinbox.valueChanged.connect(
            self._handle_max_tracklength_box_ValueChange
        )

    def _reset_filter_combobox(self):
        self.additional_filter_combobox.clear()
        self.position.clear()

    def _set_defaults(self):
        """Method that sets the default visible widgets in the main window."""
        self.position.setVisible(False)
        self.position_label.setVisible(False)
        self.additional_filter_combobox.setVisible(False)
        self.additional_filter_combobox_label.setVisible(False)
        self._reset_filter_combobox()
        self._set_tracklengths()

    def _set_position_visible(self):
        """Method that sets the visible widgets in the main window."""
        self.position.setVisible(True)
        self.position_label.setVisible(True)

    def _set_additional_filter_visible(self):
        self.additional_filter_combobox.setVisible(True)
        self.additional_filter_combobox_label.setVisible(True)

    def _filter_data(self):
        """Method to filter the data."""
        self._remove_old_layers()
        selected_position_value = self.position.currentData()
        selected_additional_filter_value = self.additional_filter_combobox.currentData()
        selected_frame_interval_value = self.frame_interval.value()

        # get tracklengths
        min_tracklength = self.min_tracklength_spinbox.value()
        max_tracklength = self.max_tracklength_spinbox.value()

        # get input data
        input_data = self.data_storage_instance.original_data.value

        # get column names
        selected_fov_column = self.data_storage_instance.columns.position_id
        selected_object_id_column = self.data_storage_instance.columns.object_id
        selected_additional_filter_column = (
            self.data_storage_instance.columns.additional_filter_column
        )
        selected_frame_column = self.data_storage_instance.columns.frame_column
        measurement_name_column = self.data_storage_instance.columns.measurement_column
        coordinate_column = self.data_storage_instance.columns.posCol

        # filter data
        self.data_filtered, max_meas, min_meas = filter_data(
            df_in=input_data,
            field_of_view_id_name=selected_fov_column,
            frame_name=selected_frame_column,
            track_id_name=selected_object_id_column,
            measurement_name=measurement_name_column,
            additional_filter_column_name=selected_additional_filter_column,
            posCols=coordinate_column,
            fov_val=selected_position_value,
            additional_filter_value=selected_additional_filter_value,
            min_tracklength_value=min_tracklength,
            max_tracklength_value=max_tracklength,
            frame_interval=selected_frame_interval_value,
            st_out=show_info,
        )

        self._update_data_storage(self.data_filtered, min_meas, max_meas)

    def _original_data_changed(self):
        self._set_defaults()

        df_orig = self.data_storage_instance.original_data.value
        pos_col = self.data_storage_instance.columns.position_id
        add_filter_col = self.data_storage_instance.columns.additional_filter_column

        if pos_col != "None":
            if len(df_orig[pos_col].unique()) > 1:
                self._set_position_visible()
                for pos in df_orig[pos_col].unique():
                    self.position.addItem(str(pos), pos)

        if add_filter_col != "None":
            self._set_additional_filter_visible()
            for add_filter in df_orig[add_filter_col].unique():
                self.additional_filter_combobox.addItem(str(add_filter), add_filter)

        self.position.setCurrentIndex(0)
        self.additional_filter_combobox.setCurrentIndex(0)
        self._filter_data()

    def _update_data_storage(self, df_filtered, min_meas, max_meas):
        """Method to update the data storage."""
        self.data_storage_instance.filtered_data = df_filtered
        self.data_storage_instance.min_max_meas = (min_meas, max_meas)

    def _set_tracklengths(self):
        """Method to set the tracklengths."""
        # work in progress
        min_t, max_t = get_tracklengths(
            self.data_storage_instance.original_data.value,
            self.data_storage_instance.columns.position_id,
            self.data_storage_instance.columns.object_id,
            self.data_storage_instance.columns.additional_filter_column,
        )
        set_track_lenths(
            (min_t, max_t),
            self.tracklenght_slider,
            self.min_tracklength_spinbox,
            self.max_tracklength_spinbox,
        )

    def _remove_old_layers(self):
        remove_layers_after_columnpicker(self.viewer, ARCOS_LAYERS.values())


if __name__ == "__main__":
    import sys

    import pandas as pd
    from arcos_gui.processing import DataStorage  # noqa: F811
    from napari import Viewer  # noqa: F811

    data_storage_instance = DataStorage()
    viewer = Viewer()
    app = QtWidgets.QApplication(sys.argv)
    widget = FilterDataWidget(viewer, data_storage_instance=data_storage_instance)
    widget.show()
    ai = pd.read_csv("C:/Users/benig/test.csv")
    data_storage_instance.columns.frame_column = "time"
    data_storage_instance.columns.object_id = "trackID"
    data_storage_instance.columns.position_id = "None"
    data_storage_instance.columns.additional_filter_column = "None"
    data_storage_instance.columns.measurement_column_1 = "ERK_KTR"
    data_storage_instance.columns.measurement_column_2 = "None"
    data_storage_instance.columns.measurement_column = "ERK_KTR"
    data_storage_instance.columns.measurement_math_operatoin = "None"
    data_storage_instance.columns.x_column = "posx"
    data_storage_instance.columns.y_column = "posy"
    data_storage_instance.columns.z_column = "posz"

    data_storage_instance.original_data = ai

    sys.exit(app.exec_())
