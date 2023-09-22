from arcos_gui.processing import columnnames
from arcos_gui.widgets import columnpicker
from pytestqt import qtbot
from qtpy.QtCore import Qt


def test_columnpicker_defaults(qtbot: qtbot):
    # Attach the dialog to a QApplication instance
    dialog = columnpicker()
    qtbot.addWidget(dialog)

    column_names = [None, None, None, None, None, None, None, None, None, None]
    assert dialog.get_column_names == column_names


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
            dialog.track_id,
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
