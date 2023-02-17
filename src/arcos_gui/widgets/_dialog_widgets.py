"""Popupdialog widgets for the arcos_gui package."""

from __future__ import annotations

from typing import Union

from arcos_gui.processing import columnnames
from arcos_gui.tools import measurement_math_options
from qtpy import QtWidgets
from qtpy.QtCore import Signal


class timestamp_options(QtWidgets.QDialog):
    """Dialog for setting timestamp options.

    Parameters
    ----------
    parent : QtWidgets.QWidget, optional
        Parent widget, by default None

    Attributes
    ----------
    start_time_label : QtWidgets.QLabel
        Label for start time
    start_time : QtWidgets.QSpinBox
        Spinbox for start time
    step_time_label : QtWidgets.QLabel
        Label for step time
    step_time : QtWidgets.QSpinBox
        Spinbox for step time
    prefix_label : QtWidgets.QLabel
        Label for prefix
    prefix : QtWidgets.QLineEdit
        Line edit for prefix
    suffix_label : QtWidgets.QLabel
        Label for suffix
    suffix : QtWidgets.QLineEdit
        Line edit for suffix
    position_label : QtWidgets.QLabel
        Label for position
    position : QtWidgets.QComboBox
        Combo box for position
    size_label : QtWidgets.QLabel
        Label for size
    ts_size : QtWidgets.QSpinBox
        Spinbox for size
    x_shift_label : QtWidgets.QLabel
        Label for x shift
    x_shift : QtWidgets.QSpinBox
        Spinbox for x shift
    y_shift_label : QtWidgets.QLabel
        Label for y shift
    y_shift : QtWidgets.QSpinBox
        Spinbox for y shift
    set_options : QtWidgets.QPushButton
        Button for setting options
    """

    def __init__(self, parent=None):
        super().__init__()
        self._setupUi()

    def _setupUi(self):
        self.setObjectName("Timestamp Options")
        self.gridLayout = QtWidgets.QGridLayout()
        self.start_time_label = QtWidgets.QLabel("Start Time")
        self.start_time = QtWidgets.QSpinBox()
        self.start_time.setRange(0, 10000)
        self.start_time.setValue(0)
        self.step_time_label = QtWidgets.QLabel("Step Time")
        self.step_time = QtWidgets.QSpinBox()
        self.step_time.setRange(0, 10000)
        self.step_time.setValue(1)
        self.prefix_label = QtWidgets.QLabel("Prefix")
        self.prefix = QtWidgets.QLineEdit()
        self.prefix.setText("T =")
        self.suffix_label = QtWidgets.QLabel("Suffix")
        self.suffix = QtWidgets.QLineEdit()
        self.suffix.setText("frame")
        self.position_label = QtWidgets.QLabel("Position")
        self.position = QtWidgets.QComboBox()
        self.position.addItems(
            ["upper_right", "upper_left", "lower_right", "lower_left", "center"]
        )
        self.position.setCurrentIndex(1)
        self.size_label = QtWidgets.QLabel("Size")
        self.ts_size = QtWidgets.QSpinBox()
        self.ts_size.setRange(0, 1000)
        self.ts_size.setValue(12)
        self.x_shift_label = QtWidgets.QLabel("X Shift")
        self.x_shift = QtWidgets.QSpinBox()
        self.x_shift.setRange(-1000, 1000)
        self.x_shift.setValue(12)
        self.y_shift_label = QtWidgets.QLabel("Y Shift")
        self.y_shift = QtWidgets.QSpinBox()
        self.y_shift.setRange(-1000, 1000)
        self.y_shift.setValue(0)
        self.set_options = QtWidgets.QPushButton("OK")
        self.gridLayout.addWidget(self.start_time_label, 0, 0)
        self.gridLayout.addWidget(self.start_time, 0, 1)
        self.gridLayout.addWidget(self.step_time_label, 1, 0)
        self.gridLayout.addWidget(self.step_time, 1, 1)
        self.gridLayout.addWidget(self.prefix_label, 2, 0)
        self.gridLayout.addWidget(self.prefix, 2, 1)
        self.gridLayout.addWidget(self.suffix_label, 3, 0)
        self.gridLayout.addWidget(self.suffix, 3, 1)
        self.gridLayout.addWidget(self.position_label, 4, 0)
        self.gridLayout.addWidget(self.position, 4, 1)
        self.gridLayout.addWidget(self.size_label, 5, 0)
        self.gridLayout.addWidget(self.ts_size, 5, 1)
        self.gridLayout.addWidget(self.x_shift_label, 6, 0)
        self.gridLayout.addWidget(self.x_shift, 6, 1)
        self.gridLayout.addWidget(self.y_shift_label, 7, 0)
        self.gridLayout.addWidget(self.y_shift, 7, 1)
        self.gridLayout.addWidget(self.set_options, 8, 0, 1, 2)
        self.setLayout(self.gridLayout)
        self.set_options.clicked.connect(self._set_options_clicked)

    def _set_options_clicked(self):
        self.close()


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
        self.set_measurement_math(measurement_math_options)
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

        self.frame.addItems(column_names)
        self.track_id.addItems(column_names)
        self.x_coordinates.addItems(column_names)
        self.y_coordinates.addItems(column_names)
        self.z_coordinates.addItems(column_names)
        self.measurement.addItems(column_names)
        self.second_measurement.addItems(column_names)
        self.field_of_view_id.addItems(column_names)
        self.additional_filter.addItems(column_names)

        self.additional_filter.addItem("None", None)
        self.field_of_view_id.addItem("None", None)
        self.z_coordinates.addItem("None", None)
        self.second_measurement.addItem("None", None)

        self.additional_filter.setCurrentText("None")
        self.field_of_view_id.setCurrentText("None")
        self.z_coordinates.setCurrentText("None")
        self.second_measurement.setCurrentText("None")

    def set_measurement_math(self, measurement_math):
        """Set the measurement math options in the dialog."""
        self.measurement_math.clear()
        self.measurement_math.addItems(measurement_math)

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
            self.frame.currentText(),
            self.track_id.currentText(),
            self.x_coordinates.currentText(),
            self.y_coordinates.currentText(),
            self.z_coordinates.currentText(),
            self.measurement.currentText(),
            self.second_measurement.currentText(),
            self.field_of_view_id.currentText(),
            self.additional_filter.currentText(),
            self.measurement_math.currentText(),
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
        columnames_instance.frame_column = self.frame.currentText()
        columnames_instance.position_id = self.field_of_view_id.currentText()
        columnames_instance.object_id = self.track_id.currentText()
        columnames_instance.x_column = self.x_coordinates.currentText()
        columnames_instance.y_column = self.y_coordinates.currentText()
        columnames_instance.z_column = self.z_coordinates.currentText()
        columnames_instance.measurement_column_1 = self.measurement.currentText()
        columnames_instance.measurement_column_2 = self.second_measurement.currentText()
        columnames_instance.additional_filter_column = (
            self.additional_filter.currentText()
        )
        columnames_instance.measurement_math_operatoin = (
            self.measurement_math.currentText()
        )

        return columnames_instance


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = columnpicker()
    window2 = timestamp_options()
    window.set_column_names(["a", "b", "c", "d", "e", "f", "g", "h", "i"])
    window.show()
    window2.show()
    print(window.get_column_names)
    sys.exit(app.exec_())
