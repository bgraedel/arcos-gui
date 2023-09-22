"""Widget to handle filtering of input data."""
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


class _filter_dataUI(QtWidgets.QWidget):
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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def _init_ranged_sliderts(self):
        """Initialize ranged sliders from superqt."""
        self.tracklenght_slider = QRangeSlider(Qt.Horizontal)
        self.horizontalLayout_tracklength.addWidget(self.tracklenght_slider)

        # set starting values
        self.tracklenght_slider.setRange(0, 10)
        self.tracklenght_slider.setValue((0, 10))

    def _handle_slider_tracklength_value_change(self):
        """Method to handle trancklenght value changes."""
        slider_vals = self.tracklenght_slider.value()
        self.min_tracklength_spinbox.setValue(slider_vals[0])
        self.max_tracklength_spinbox.setValue(slider_vals[1])

    def _handle_min_tracklenght_box_value_change(self, value):
        """Method to handle min tracklenght spinbox."""
        slider_vals = self.tracklenght_slider.value()
        self.tracklenght_slider.setValue((value, slider_vals[1]))

    def _handle_max_tracklength_box_value_change(self, value):
        """Method to handle max tracklength spinbox."""
        slider_vals = self.tracklenght_slider.value()
        self.tracklenght_slider.setValue((slider_vals[0], value))

    def _connect_ranged_sliders_to_spinboxes(self):
        """Method to connect ranged sliders to spinboxes to sync values."""
        self.tracklenght_slider.valueChanged.connect(
            self._handle_slider_tracklength_value_change
        )
        self.min_tracklength_spinbox.valueChanged.connect(
            self._handle_min_tracklenght_box_value_change
        )
        self.max_tracklength_spinbox.valueChanged.connect(
            self._handle_max_tracklength_box_value_change
        )

    def _reset_filter_combobox(self):
        self.additional_filter_combobox.clear()
        self.position.clear()

    def set_defaults(self):
        """Method that sets the default visible widgets in the main window."""
        self.position.setVisible(False)
        self.position_label.setVisible(False)
        self.additional_filter_combobox.setVisible(False)
        self.additional_filter_combobox_label.setVisible(False)
        self._reset_filter_combobox()

    def set_position_visible(self):
        """Method that sets the visible widgets in the main window."""
        self.position.setVisible(True)
        self.position_label.setVisible(True)

    def set_additional_filter_visible(self):
        self.additional_filter_combobox.setVisible(True)
        self.additional_filter_combobox_label.setVisible(True)

    def setup_ui(self):
        """Setup UI. Loads it from ui file."""
        uic.loadUi(self.UI_FILE, self)  # load QtDesigner .ui file
        self.set_defaults()
        self._init_ranged_sliderts()
        self._connect_ranged_sliders_to_spinboxes()


class FilterController:
    """Widget to handle filtering of input data."""

    def __init__(self, viewer: Viewer, data_storage_instance: DataStorage, parent=None):
        self.viewer = viewer
        self.widget = _filter_dataUI()

        self.data_storage_instance = data_storage_instance
        self.data_storage_instance.original_data.value_changed.connect(
            self._original_data_changed
        )
        self.data_storage_instance.min_max_tracklenght.value_changed.connect(
            self._set_tracklengths
        )
        self.widget.max_tracklength_spinbox.valueChanged.connect(
            self._update_data_storage_tracklenght
        )
        self.widget.min_tracklength_spinbox.valueChanged.connect(
            self._update_data_storage_tracklenght
        )
        self.widget.filter_input_data.clicked.connect(self._filter_data)
        self._set_default_values()

    def _set_default_values(self):
        self.widget.set_defaults()
        self._set_tracklengths()

    def _filter_data(self):
        """Method to filter the data."""
        self._remove_old_layers()
        selected_position_value = self.widget.position.currentData()
        selected_additional_filter_value = (
            self.widget.additional_filter_combobox.currentData()
        )
        selected_frame_interval_value = self.widget.frame_interval.value()

        # get tracklengths
        min_tracklength = self.widget.min_tracklength_spinbox.value()
        max_tracklength = self.widget.max_tracklength_spinbox.value()

        # get input data
        input_data = self.data_storage_instance.original_data.value

        # get column names
        selected_fov_column = self.data_storage_instance.columns.value.position_id
        selected_object_id_column = self.data_storage_instance.columns.value.object_id
        selected_additional_filter_column = (
            self.data_storage_instance.columns.value.additional_filter_column
        )
        selected_frame_column = self.data_storage_instance.columns.value.frame_column
        measurement_name_column = (
            self.data_storage_instance.columns.value.measurement_column
        )
        coordinate_column = self.data_storage_instance.columns.value.posCol

        # filter data
        data_filtered, max_meas, min_meas = filter_data(
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

        self._update_data_storage(data_filtered, min_meas, max_meas)

    def _original_data_changed(self):
        self._set_default_values()

        df_orig = self.data_storage_instance.original_data.value
        pos_col = self.data_storage_instance.columns.value.position_id
        add_filter_col = (
            self.data_storage_instance.columns.value.additional_filter_column
        )

        if pos_col:
            if len(df_orig[pos_col].unique()) > 1:
                self.widget.set_position_visible()
                for pos in df_orig[pos_col].unique():
                    self.widget.position.addItem(str(pos), pos)

        if add_filter_col:
            self.widget.set_additional_filter_visible()
            for add_filter in df_orig[add_filter_col].unique():
                self.widget.additional_filter_combobox.addItem(
                    str(add_filter), add_filter
                )

        self.widget.position.setCurrentIndex(0)
        self.widget.additional_filter_combobox.setCurrentIndex(0)
        self._filter_data()

    def _update_data_storage(self, df_filtered, min_meas, max_meas):
        """Method to update the data storage."""
        self.data_storage_instance.reset_relevant_attributes(True)
        self.data_storage_instance.filtered_data.value = df_filtered
        self.data_storage_instance.min_max_meas.value = [min_meas, max_meas]

    def _set_tracklengths(self):
        """Method to set the tracklengths."""
        if self.data_storage_instance.original_data.value is None:
            min_t, max_t = 0, 1
        elif self.data_storage_instance.columns.value.object_id is None:
            min_t, max_t = 0, 1
        else:
            min_t, max_t = get_tracklengths(
                self.data_storage_instance.original_data.value,
                self.data_storage_instance.columns.value.position_id,
                self.data_storage_instance.columns.value.object_id,
                self.data_storage_instance.columns.value.additional_filter_column,
            )
        set_track_lenths(
            (min_t, max_t),
            self.widget.tracklenght_slider,
            self.widget.min_tracklength_spinbox,
            self.widget.max_tracklength_spinbox,
        )

    def _remove_old_layers(self):
        remove_layers_after_columnpicker(self.viewer, ARCOS_LAYERS.values())

    def _update_data_storage_tracklenght(self):
        """Method to update the data storage."""
        self.data_storage_instance.toggle_callback_block(True)
        self.data_storage_instance.min_max_tracklenght.value = [
            self.widget.min_tracklength_spinbox.value(),
            self.widget.max_tracklength_spinbox.value(),
        ]
        self.data_storage_instance.toggle_callback_block(False)
