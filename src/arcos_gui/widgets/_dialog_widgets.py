"""Popupdialog widgets for the arcos_gui package."""

from __future__ import annotations

from typing import Iterable, Union

from arcos_gui.processing import columnnames
from arcos_gui.tools import OPERATOR_DICTIONARY
from qtpy import QtWidgets
from qtpy.QtCore import Signal


class columnpicker(QtWidgets.QDialog):
    """Dialog to pick the columns of the data file.

    Parameters
    ----------
    parent : QtWidgets.QWidget, optional
        Parent widget, by default None
    columnames_instance : Union[columnnames, None], optional
        Instance of the columnnames class, by default None

    Attributes
    ----------
    frame : QtWidgets.QComboBox
        Combobox to select the frame column
    track_id : QtWidgets.QComboBox
        Combobox to select the track id column
    x : QtWidgets.QComboBox
        Combobox to select the x column
    y : QtWidgets.QComboBox
        Combobox to select the y column
    measurement : QtWidgets.QComboBox
        Combobox to select the measurement column
    measurement_math : QtWidgets.QComboBox
        Combobox to select the measurement math column
    second_measurement : QtWidgets.QComboBox
        Combobox to select the second measurement column
    ok_button : QtWidgets.QPushButton
        Button to confirm the selection
    abort_button : QtWidgets.QPushButton
        Button to abort the selection
    ok_pressed : bool
        True if ok button was pressed, False if abort button was pressed

    Signals
    -------
    aborted : Signal
        Signal emitted if abort button was pressed
    ok : Signal
        Signal emitted if ok button was pressed
    """

    aborted = Signal()
    ok = Signal()

    def __init__(
        self, parent=None, columnames_instance: Union[columnnames, None] = None
    ):
        super().__init__(parent)

        self._setupUi()
        self._add_tooltipps()
        self.columnames_instance = columnames_instance
        self.set_measurement_math(list(OPERATOR_DICTIONARY.keys()))
        self.measurement_math.setCurrentText("None")
        self.measurement_math.currentTextChanged.connect(
            self.toggle_visible_second_measurment
        )
        self.second_measurement.setVisible(False)
        self.label_7.setVisible(False)

        self.ok_button.clicked.connect(self._on_ok)
        self.abort_button.clicked.connect(self._on_abort)
        self.ok_pressed = False

    def _on_ok(self, event):
        _ = event
        self.ok_pressed = True
        self.accept()

    def _on_abort(self, event):
        _ = event
        self.ok_pressed = False
        self.reject()

    def _setupUi(self):
        self.setObjectName("columnpicker")
        self.grid_layout = QtWidgets.QGridLayout()
        self.grid_layout.setObjectName("gridLayout")
        self.frame = QtWidgets.QComboBox()
        self.frame.setObjectName("frame")

        self.label = QtWidgets.QLabel("Frame Column:")
        self.label.setObjectName("frame_label")

        self.track_id = QtWidgets.QComboBox()
        self.track_id.setObjectName("track_id")

        self.label_2 = QtWidgets.QLabel("Object id Column:")
        self.label_2.setObjectName("track_id_label")

        self.label_3 = QtWidgets.QLabel("X Coordinate Column:")
        self.label_3.setObjectName("x_coordinates_label")

        self.x_coordinates = QtWidgets.QComboBox()
        self.x_coordinates.setObjectName("x_coordinates")

        self.label_4 = QtWidgets.QLabel("Y Coordinate Column:")
        self.label_4.setObjectName("y_coordinates_label")

        self.y_coordinates = QtWidgets.QComboBox()
        self.y_coordinates.setObjectName("y_coordinates")

        self.label_5 = QtWidgets.QLabel("Z Coordinate Column:")
        self.label_5.setObjectName("z_coordinates_label")

        self.z_coordinates = QtWidgets.QComboBox()
        self.z_coordinates.setObjectName("z_coordinates")

        self.label_6 = QtWidgets.QLabel("Measurement Column:")
        self.label_6.setObjectName("measurment_label")

        self.measurement = QtWidgets.QComboBox()
        self.measurement.setObjectName("measurment")

        self.label_7 = QtWidgets.QLabel("Second Measurement Column:")
        self.label_7.setObjectName("second_measurment_label")

        self.second_measurement = QtWidgets.QComboBox()
        self.second_measurement.setObjectName("second_measurment")

        self.label_8 = QtWidgets.QLabel("Field of View/Position Column:")
        self.label_8.setObjectName("field_of_view_id_label")

        self.field_of_view_id = QtWidgets.QComboBox()
        self.field_of_view_id.setObjectName("field_of_view_id")

        self.label_9 = QtWidgets.QLabel("Additional Filter Column:")
        self.label_9.setObjectName("additional_filter_label")

        self.additional_filter = QtWidgets.QComboBox()
        self.additional_filter.setObjectName("additional_filter")

        self.label_10 = QtWidgets.QLabel("Math on first and second measurement:")
        self.label_10.setObjectName("measurement_math_label")

        self.measurement_math = QtWidgets.QComboBox()
        self.measurement_math.setObjectName("measurement_math")

        self.ok_button = QtWidgets.QPushButton("Ok")
        self.ok_button.setObjectName("Ok")

        self.abort_button = QtWidgets.QPushButton("Abort")
        self.abort_button.setObjectName("Abort")
        self.abort_button.setStyleSheet("background-color : #7C0A02; color : white")

        self.grid_layout.addWidget(self.frame, 1, 1, 1, 1)
        self.grid_layout.addWidget(self.label, 1, 0, 1, 1)
        self.grid_layout.addWidget(self.label_2, 2, 0, 1, 1)
        self.grid_layout.addWidget(self.track_id, 2, 1, 1, 1)
        self.grid_layout.addWidget(self.label_3, 3, 0, 1, 1)
        self.grid_layout.addWidget(self.x_coordinates, 3, 1, 1, 1)
        self.grid_layout.addWidget(self.label_4, 4, 0, 1, 1)
        self.grid_layout.addWidget(self.y_coordinates, 4, 1, 1, 1)
        self.grid_layout.addWidget(self.label_5, 5, 0, 1, 1)
        self.grid_layout.addWidget(self.z_coordinates, 5, 1, 1, 1)
        self.grid_layout.addWidget(self.label_6, 6, 0, 1, 1)
        self.grid_layout.addWidget(self.measurement, 6, 1, 1, 1)
        self.grid_layout.addWidget(self.label_7, 7, 0, 1, 1)
        self.grid_layout.addWidget(self.second_measurement, 7, 1, 1, 1)
        self.grid_layout.addWidget(self.label_8, 8, 0, 1, 1)
        self.grid_layout.addWidget(self.field_of_view_id, 8, 1, 1, 1)
        self.grid_layout.addWidget(self.label_9, 9, 0, 1, 1)
        self.grid_layout.addWidget(self.additional_filter, 9, 1, 1, 1)
        self.grid_layout.addWidget(self.label_10, 10, 0, 1, 1)
        self.grid_layout.addWidget(self.measurement_math, 10, 1, 1, 1)
        self.grid_layout.addWidget(self.ok_button, 12, 1, 1, 1)
        self.grid_layout.addWidget(self.abort_button, 12, 0, 1, 1)
        # add it to our layout
        self.setLayout(self.grid_layout)

    def _add_tooltipps(self):
        """Add tooltipps to the widgets."""
        self.frame.setToolTip("Select frame column in input data")
        self.track_id.setToolTip("Select object id column in input data")
        self.x_coordinates.setToolTip("Column with x coordinates")
        self.y_coordinates.setToolTip("Column with y coordinates")
        self.z_coordinates.setToolTip("Column with z coordinates")
        self.measurement.setToolTip("Column with measurement")
        self.second_measurement.setToolTip(
            "Select second measurement for measurement math"
        )
        self.field_of_view_id.setToolTip(
            "Select fov column in input data, select None if column does not exist"
        )
        self.additional_filter.setToolTip(
            "Select additional filter column, for example Well of a wellplate, select None if column does not exist"
        )
        self.measurement_math.setToolTip(
            "Choose operation to calculate the measurment to be used in\n\
            arcos calculation on first and second measurement"
        )

    def _add_item_data_pair(
        self, combobox: QtWidgets.QComboBox, text: Iterable, data: Iterable
    ):
        """Add items to comboboxes."""
        for i, j in zip(text, data):
            combobox.addItem(i, j)

    def set_column_names(self, column_names):
        """Set column names in comboboxes."""
        while "" in column_names:
            column_names.remove("")

        self.frame.clear()
        self.track_id.clear()
        self.x_coordinates.clear()
        self.y_coordinates.clear()
        self.z_coordinates.clear()
        self.measurement.clear()
        self.second_measurement.clear()
        self.field_of_view_id.clear()
        self.additional_filter.clear()

        self._add_item_data_pair(self.frame, column_names, column_names)
        self._add_item_data_pair(self.track_id, column_names, column_names)
        self._add_item_data_pair(self.x_coordinates, column_names, column_names)
        self._add_item_data_pair(self.y_coordinates, column_names, column_names)
        self._add_item_data_pair(self.z_coordinates, column_names, column_names)
        self._add_item_data_pair(self.measurement, column_names, column_names)
        self._add_item_data_pair(self.second_measurement, column_names, column_names)
        self._add_item_data_pair(self.field_of_view_id, column_names, column_names)
        self._add_item_data_pair(self.additional_filter, column_names, column_names)

        self.additional_filter.addItem("None", None)
        self.field_of_view_id.addItem("None", None)
        self.z_coordinates.addItem("None", None)
        self.second_measurement.addItem("None", None)
        self.track_id.addItem("None", None)

        self.additional_filter.setCurrentText("None")
        self.field_of_view_id.setCurrentText("None")
        self.z_coordinates.setCurrentText("None")
        self.second_measurement.setCurrentText("None")
        self.track_id.setCurrentText("None")

    def set_measurement_math(self, measurement_math):
        """Set the measurement math options in the dialog."""
        self.measurement_math.clear()
        self._add_item_data_pair(
            self.measurement_math, measurement_math, measurement_math
        )
        self.measurement_math.addItem("None", None)

    def toggle_visible_second_measurment(self):
        """Toggles visibility of second measurement column."""
        curr_value = self.measurement_math.currentText()
        if curr_value in ["None", "1/X"]:
            self.second_measurement.setVisible(False)
            self.label_7.setVisible(False)
        else:
            self.second_measurement.setVisible(True)
            self.label_7.setVisible(True)

    @property
    def get_column_names(self):
        """Returns a tuple of all column names in the columnnames dialog."""
        return [
            self.frame.currentData(),
            self.track_id.currentData(),
            self.x_coordinates.currentData(),
            self.y_coordinates.currentData(),
            self.z_coordinates.currentData(),
            self.measurement.currentData(),
            self.second_measurement.currentData(),
            self.field_of_view_id.currentData(),
            self.additional_filter.currentData(),
            self.measurement_math.currentData(),
        ]

    @property
    def settable_columns(self):
        """Returns a tuple of all settable columns in the columnnames dialog."""
        return (
            self.frame,
            self.track_id,
            self.x_coordinates,
            self.y_coordinates,
            self.z_coordinates,
            self.measurement,
            self.second_measurement,
            self.field_of_view_id,
            self.additional_filter,
            self.measurement_math,
        )

    @property
    def as_columnames_object(self):
        """Retunrs a new columnames object with the current column names."""
        # set column_names
        columnames_instance = columnnames()
        columnames_instance.frame_column = self.frame.currentData()
        columnames_instance.position_id = self.field_of_view_id.currentData()
        columnames_instance.object_id = self.track_id.currentData()
        columnames_instance.x_column = self.x_coordinates.currentData()
        columnames_instance.y_column = self.y_coordinates.currentData()
        columnames_instance.z_column = self.z_coordinates.currentData()
        columnames_instance.measurement_column_1 = self.measurement.currentData()
        columnames_instance.measurement_column_2 = self.second_measurement.currentData()
        columnames_instance.additional_filter_column = (
            self.additional_filter.currentData()
        )
        columnames_instance.measurement_math_operation = (
            self.measurement_math.currentData()
        )

        return columnames_instance


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = columnpicker()
    window.set_column_names(["a", "b", "c", "d", "e", "f", "g", "h", "i"])
    window.show()
    print(window.get_column_names)
    sys.exit(app.exec_())
