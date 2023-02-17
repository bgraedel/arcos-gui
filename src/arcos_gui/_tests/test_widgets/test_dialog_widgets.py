from arcos_gui.processing import columnnames
from arcos_gui.widgets import columnpicker, timestamp_options
from pytestqt import qtbot
from qtpy.QtCore import Qt


def test_timestamp_options_defaults(qtbot):
    # Create an instance of the timestamp_options dialog
    dialog = timestamp_options()
    # Attach the dialog to a QApplication instance
    qtbot.addWidget(dialog)
    # Ensure the start time spin box has the expected default value
    assert dialog.start_time.value() == 0
    # Ensure the step time spin box has the expected default value
    assert dialog.step_time.value() == 1
    # Ensure the prefix line edit has the expected default text
    assert dialog.prefix.text() == "T ="
    # Ensure the suffix line edit has the expected default text
    assert dialog.suffix.text() == "frame"
    # Ensure the position combo box has the expected default value
    assert dialog.position.currentText() == "upper_left"
    # Ensure the size spin box has the expected default value
    assert dialog.ts_size.value() == 12
    # Ensure the x shift spin box has the expected default value
    assert dialog.x_shift.value() == 12
    # Ensure the y shift spin box has the expected default value
    assert dialog.y_shift.value() == 0


def test_timestamp_options_set_values(qtbot):
    # Create an instance of the timestamp_options dialog
    dialog = timestamp_options()
    # Attach the dialog to a QApplication instance
    qtbot.addWidget(dialog)
    # Set the values of the spin boxes and line edits
    dialog.start_time.setValue(10)
    dialog.step_time.setValue(5)
    dialog.prefix.setText("Frame =")
    dialog.suffix.setText("seconds")
    dialog.position.setCurrentText("center")
    dialog.ts_size.setValue(24)
    dialog.x_shift.setValue(50)
    dialog.y_shift.setValue(100)
    # Ensure the values have been set correctly
    assert dialog.start_time.value() == 10
    assert dialog.step_time.value() == 5
    assert dialog.prefix.text() == "Frame ="
    assert dialog.suffix.text() == "seconds"
    assert dialog.position.currentText() == "center"
    assert dialog.ts_size.value() == 24
    assert dialog.x_shift.value() == 50
    assert dialog.y_shift.value() == 100


def test_columnpicker_defaults(qtbot: qtbot):
    # Attach the dialog to a QApplication instance
    dialog = columnpicker()
    qtbot.addWidget(dialog)

    column_names = ["", "", "", "", "", "", "", "", "", "None"]
    assert sorted(dialog.get_column_names) == sorted(column_names)


def test_columnpicker_set_columns(qtbot):
    column_names = ["", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
    dialog = columnpicker()
    qtbot.addWidget(dialog)
    dialog.set_column_names(column_names)
    for i in dialog.settable_columns:
        if i in [
            dialog.z_coordinates,
            dialog.additional_filter,
            dialog.field_of_view_id,
            dialog.second_measurement,
        ]:
            assert sorted(i.itemText(j) for j in range(i.count())) == sorted(
                [
                    "a",
                    "b",
                    "c",
                    "d",
                    "e",
                    "f",
                    "g",
                    "h",
                    "i",
                    "j",
                    "None",
                ]
            )
        elif i == dialog.measurement_math:
            assert sorted(i.itemText(j) for j in range(i.count())) == sorted(
                ["Add", "Divide", "Multiply", "None", "Subtract"]
            )
        else:
            assert sorted(i.itemText(j) for j in range(i.count())) == sorted(
                [
                    "a",
                    "b",
                    "c",
                    "d",
                    "e",
                    "f",
                    "g",
                    "h",
                    "i",
                    "j",
                ]
            )


def test_columnpicker_okpress(qtbot):
    dialog = columnpicker()
    qtbot.addWidget(dialog)
    assert dialog.ok_pressed is False
    qtbot.mouseClick(dialog.ok_button, Qt.LeftButton)
    assert dialog.ok_pressed is True


def test_columnpicker_cancelpress(qtbot):
    dialog = columnpicker()
    qtbot.addWidget(dialog)
    assert dialog.ok_pressed is False
    qtbot.mouseClick(dialog.abort_button, Qt.LeftButton)
    assert dialog.ok_pressed is False


def test_columnpicker_as_columnnames_object(qtbot):
    column_names = [
        "frame",
        "track_id",
        "x",
        "y",
        "z",
        "measurement",
        "measurement_2",
        "position_id",
        "additional_filter",
    ]
    dialog = columnpicker()
    qtbot.addWidget(dialog)
    dialog.set_column_names(column_names)
    columnames_instance = columnnames()
    # set values to what columnames has as defaults
    dialog.frame.setCurrentText("frame")
    dialog.track_id.setCurrentText("track_id")
    dialog.x_coordinates.setCurrentText("x")
    dialog.y_coordinates.setCurrentText("y")
    dialog.z_coordinates.setCurrentText("z")
    dialog.measurement.setCurrentText("measurement")
    dialog.measurement_math.setCurrentText("None")
    dialog.second_measurement.setCurrentText("measurement_2")
    dialog.field_of_view_id.setCurrentText("position_id")
    dialog.additional_filter.setCurrentText("additional_filter")
    assert dialog.as_columnames_object == columnames_instance
