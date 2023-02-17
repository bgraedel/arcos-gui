from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from arcos_gui.processing import DataStorage
from arcos_gui.widgets import InputDataWidget
from qtpy.QtCore import QEventLoop, Qt

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


@pytest.fixture()
def make_input_widget(qtbot, make_napari_viewer):
    ds = DataStorage()
    widget = InputDataWidget(ds)
    qtbot.addWidget(widget)
    yield widget, qtbot
    widget.close()
    del widget


def test_open_widget(make_input_widget):
    input_data_widget, _ = make_input_widget
    assert input_data_widget


@pytest.mark.parametrize(
    "filename", [("test.csv", "csv (*.csv)"), ("test.csv.gz", "csv (*.csv.gz)")]
)
@patch("qtpy.QtWidgets.QFileDialog.getOpenFileName")
def test_browse_files(
    mock_get_open_file_name, make_input_widget: tuple[InputDataWidget, QtBot], filename
):
    widget, qtbot = make_input_widget

    # mock out the QFileDialog.getOpenFileName method to return a fixed value
    mock_get_open_file_name.return_value = filename

    # simulate a click on the browse_file button
    qtbot.mouseClick(widget.browse_file, Qt.LeftButton)

    # assert that the file path was correctly set in the file_LineEdit field
    assert widget.file_LineEdit.text() == filename[0]


def test_open_columnpicker(make_input_widget: tuple[InputDataWidget, QtBot]):
    widget, qtbot = make_input_widget

    # set the file_LineEdit field to a csv file path
    widget.file_LineEdit.setText("src/arcos_gui/_tests/test_data/arcos_data.csv")

    # simulate a click on the open_file_button
    qtbot.mouseClick(widget.open_file_button, Qt.LeftButton)

    # assert that the columnpicker window was opened
    assert widget.picker.isVisibleTo(widget)
    qtbot.mouseClick(widget.picker.abort_button, Qt.LeftButton)
    widget.loading_thread.quit()
    widget.loading_thread.exit()
    widget.close()


def test_open_columnpicker_with_invalid_file(
    make_input_widget: tuple[InputDataWidget, QtBot], capsys
):
    widget, qtbot = make_input_widget

    # set the file_LineEdit field to a csv file path
    widget.file_LineEdit.setText(
        "src/arcos_gui/_tests/test_data/arcos_data_fake_file.csv"
    )

    # simulate a click on the open_file_button
    qtbot.mouseClick(widget.open_file_button, Qt.LeftButton)

    catptured = capsys.readouterr()
    assert catptured.out == "INFO: File does not exist\n"


def test_open_columnpicker_with_invalid_file_type(
    make_input_widget: tuple[InputDataWidget, QtBot], capsys
):
    widget, qtbot = make_input_widget

    # set the file_LineEdit field to a csv file path
    widget.file_LineEdit.setText(
        "src/arcos_gui/_tests/test_data/arcos_data_fake_file.txt"
    )

    # simulate a click on the open_file_button
    qtbot.mouseClick(widget.open_file_button, Qt.LeftButton)

    # assert that the columnpicker window was opened
    catptured = capsys.readouterr()
    assert catptured.out == "INFO: File type not supported\n"


def test_set_choices_names_from_previous(
    make_input_widget: tuple[InputDataWidget, QtBot]
):
    widget, qtbot = make_input_widget

    # set the file_LineEdit field to a csv file path
    widget.file_LineEdit.setText("src/arcos_gui/_tests/test_data/arcos_data.csv")

    # simulate a click on the open_file_button
    qtbot.mouseClick(widget.open_file_button, Qt.LeftButton)
    widget.picker.frame.setCurrentText("t")
    widget.picker.track_id.setCurrentText("id")
    widget.picker.x_coordinates.setCurrentText("x")
    widget.picker.y_coordinates.setCurrentText("y")
    widget.picker.z_coordinates.setCurrentText("None")
    widget.picker.measurement.setCurrentText("m")
    widget.picker.measurement_math.setCurrentText("None")
    widget.picker.second_measurement.setCurrentText("None")
    widget.picker.field_of_view_id.setCurrentText("Position")
    widget.picker.additional_filter.setCurrentText("None")
    # press ok to close the picker widget
    qtbot.mouseClick(widget.picker.ok_button, Qt.LeftButton)

    # reopen the picker widget
    qtbot.mouseClick(widget.open_file_button, Qt.LeftButton)
    column_names = [
        "t",
        "id",
        "x",
        "y",
        "None",
        "m",
        "None",
        "None",
        "Position",
        "None",
    ]
    qtbot.mouseClick(widget.picker.ok_button, Qt.LeftButton)

    assert sorted(widget.picker.get_column_names) == sorted(column_names)
    widget.loading_thread.quit()
    widget.loading_thread.exit()
    widget.close()


def test_data_loading(make_input_widget: tuple[InputDataWidget, QtBot]):
    # need this event loop thingy to wait for the creation of the preprocessing worker
    loopy = QEventLoop()
    widget, qtbot = make_input_widget

    # set the file_LineEdit field to a csv file path
    widget.file_LineEdit.setText("src/arcos_gui/_tests/test_data/arcos_data.csv")
    print("testing")
    # simulate a click on the open_file_button
    qtbot.mouseClick(widget.open_file_button, Qt.LeftButton)
    # simulate setting the column names
    widget.picker.frame.setCurrentText("t")
    widget.picker.track_id.setCurrentText("id")
    widget.picker.x_coordinates.setCurrentText("x")
    widget.picker.y_coordinates.setCurrentText("y")
    widget.picker.z_coordinates.setCurrentText("None")
    widget.picker.measurement.setCurrentText("m")
    widget.picker.measurement_math.setCurrentText("None")
    widget.picker.second_measurement.setCurrentText("None")
    widget.picker.field_of_view_id.setCurrentText("None")
    widget.picker.additional_filter.setCurrentText("None")
    widget.loading_thread.started.connect(lambda: print("started"))
    widget.loading_thread.finished.connect(lambda: print("finished"))
    widget.loading_worker.finished.connect(lambda: print("worker finished"))
    # quit event loop when the thread is finished
    widget.loading_thread.finished.connect(loopy.quit)

    qtbot.mouseClick(widget.picker.ok_button, Qt.LeftButton)
    # press ok to close the picker widget

    loopy.exec_()
    assert not widget.data_storage_instance.original_data.value.empty


def test_data_loading_abort(make_input_widget: tuple[InputDataWidget, QtBot], capsys):
    widget, qtbot = make_input_widget

    # set the file_LineEdit field to a csv file path
    widget.file_LineEdit.setText("src/arcos_gui/_tests/test_data/arcos_data.csv")

    # simulate a click on the open_file_button
    widget.open_file_button.click()
    widget.picker.frame.setCurrentText("t")
    widget.picker.track_id.setCurrentText("id")
    widget.picker.x_coordinates.setCurrentText("x")
    widget.picker.y_coordinates.setCurrentText("y")
    widget.picker.z_coordinates.setCurrentText("None")
    widget.picker.measurement.setCurrentText("m")
    widget.picker.measurement_math.setCurrentText("None")
    widget.picker.second_measurement.setCurrentText("None")
    widget.picker.field_of_view_id.setCurrentText("Position")
    widget.picker.additional_filter.setCurrentText("None")

    # need this event loop thingy to wait for the creation of the preprocessing worker
    loop = QEventLoop(parent=widget)
    widget.loading_thread.finished.connect(loop.quit)
    # press abort to close the picker widget
    widget.picker.abort_button.click()
    loop.exec_()
    catptured = capsys.readouterr()
    assert widget.data_storage_instance.original_data.value.empty
    assert catptured.out == "INFO: Loading aborted\n"
