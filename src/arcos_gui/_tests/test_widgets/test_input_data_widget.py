from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from arcos_gui.processing import DataStorage
from arcos_gui.widgets import InputdataController
from qtpy.QtCore import QEventLoop, Qt

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


@pytest.fixture()
def make_input_widget(qtbot, make_napari_viewer):
    ds = DataStorage()
    controller = InputdataController(ds, print)
    qtbot.addWidget(controller.widget)
    yield controller, qtbot
    controller.widget.close()
    del controller


def test_open_widget(make_input_widget):
    input_data_controller, _ = make_input_widget
    assert input_data_controller


@pytest.mark.parametrize(
    "filename", [("test.csv", "csv (*.csv)"), ("test.csv.gz", "csv (*.csv.gz)")]
)
@patch("qtpy.QtWidgets.QFileDialog.getOpenFileName")
def test_browse_files(
    mock_get_open_file_name,
    make_input_widget: tuple[InputdataController, QtBot],
    filename,
):
    controller, qtbot = make_input_widget

    # mock out the QFileDialog.getOpenFileName method to return a fixed value
    mock_get_open_file_name.return_value = filename

    # simulate a click on the browse_file button
    qtbot.mouseClick(controller.widget.browse_file, Qt.LeftButton)

    # assert that the file path was correctly set in the file_LineEdit field
    assert controller.widget.file_LineEdit.text() == filename[0]


def test_open_columnpicker(make_input_widget: tuple[InputdataController, QtBot]):
    controller, qtbot = make_input_widget

    # set the file_LineEdit field to a csv file path
    controller.widget.file_LineEdit.setText(
        "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )

    # simulate a click on the open_file_button
    qtbot.mouseClick(controller.widget.open_file_button, Qt.LeftButton)

    # assert that the columnpicker window was opened
    assert controller.picker.isVisibleTo(controller.widget)
    qtbot.mouseClick(controller.picker.abort_button, Qt.LeftButton)
    controller.loading_thread.quit()
    controller.loading_thread.exit()
    controller.widget.close()


def test_open_columnpicker_with_invalid_file(
    make_input_widget: tuple[InputdataController, QtBot], capsys
):
    controller, qtbot = make_input_widget

    # set the file_LineEdit field to a csv file path
    controller.widget.file_LineEdit.setText(
        "src/arcos_gui/_tests/test_data/arcos_data_fake_file.csv"
    )

    # simulate a click on the open_file_button
    qtbot.mouseClick(controller.widget.open_file_button, Qt.LeftButton)

    catptured = capsys.readouterr()
    assert "File does not exist" in catptured.out


def test_open_columnpicker_with_invalid_file_type(
    make_input_widget: tuple[InputdataController, QtBot], capsys
):
    controller, qtbot = make_input_widget

    # set the file_LineEdit field to a csv file path
    controller.widget.file_LineEdit.setText(
        "src/arcos_gui/_tests/test_data/arcos_data_fake_file.txt"
    )

    # simulate a click on the open_file_button
    qtbot.mouseClick(controller.widget.open_file_button, Qt.LeftButton)

    # assert that the columnpicker window was opened
    catptured = capsys.readouterr()
    assert "File type not supported" in catptured.out


def test_set_choices_names_from_previous(
    make_input_widget: tuple[InputdataController, QtBot]
):
    controller, qtbot = make_input_widget

    # set the file_LineEdit field to a csv file path
    controller.widget.file_LineEdit.setText(
        "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )

    # simulate a click on the open_file_button
    qtbot.mouseClick(controller.widget.open_file_button, Qt.LeftButton)
    controller.picker.frame.setCurrentText("t")
    controller.picker.track_id.setCurrentText("id")
    controller.picker.x_coordinates.setCurrentText("x")
    controller.picker.y_coordinates.setCurrentText("y")
    controller.picker.z_coordinates.setCurrentText("None")
    controller.picker.measurement.setCurrentText("m")
    controller.picker.measurement_math.setCurrentText("None")
    controller.picker.second_measurement.setCurrentText("None")
    controller.picker.field_of_view_id.setCurrentText("Position")
    controller.picker.additional_filter.setCurrentText("None")
    # press ok to close the picker widget
    qtbot.mouseClick(controller.picker.ok_button, Qt.LeftButton)

    # reopen the picker widget
    qtbot.mouseClick(controller.widget.open_file_button, Qt.LeftButton)
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
    qtbot.mouseClick(controller.picker.ok_button, Qt.LeftButton)

    assert sorted(controller.picker.get_column_names) == sorted(column_names)
    controller.loading_thread.quit()
    controller.loading_thread.exit()
    controller.widget.close()


def test_data_loading(make_input_widget: tuple[InputdataController, QtBot]):
    # need this event loop thingy to wait for the creation of the preprocessing worker
    loopy = QEventLoop()
    controller, qtbot = make_input_widget

    # set the file_LineEdit field to a csv file path
    controller.widget.file_LineEdit.setText(
        "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )
    print("testing")
    # simulate a click on the open_file_button
    qtbot.mouseClick(controller.widget.open_file_button, Qt.LeftButton)
    # simulate setting the column names
    controller.picker.frame.setCurrentText("t")
    controller.picker.track_id.setCurrentText("id")
    controller.picker.x_coordinates.setCurrentText("x")
    controller.picker.y_coordinates.setCurrentText("y")
    controller.picker.z_coordinates.setCurrentText("None")
    controller.picker.measurement.setCurrentText("m")
    controller.picker.measurement_math.setCurrentText("None")
    controller.picker.second_measurement.setCurrentText("None")
    controller.picker.field_of_view_id.setCurrentText("None")
    controller.picker.additional_filter.setCurrentText("None")
    controller.loading_thread.started.connect(lambda: print("started"))
    controller.loading_thread.finished.connect(lambda: print("finished"))
    controller.loading_worker.finished.connect(lambda: print("worker finished"))
    # quit event loop when the thread is finished
    controller.loading_thread.finished.connect(loopy.quit)

    qtbot.mouseClick(controller.picker.ok_button, Qt.LeftButton)
    # press ok to close the picker widget

    loopy.exec_()
    assert not controller.data_storage_instance.original_data.value.empty


def test_data_loading_abort(
    make_input_widget: tuple[InputdataController, QtBot], capsys
):
    controller, qtbot = make_input_widget

    # set the file_LineEdit field to a csv file path
    controller.widget.file_LineEdit.setText(
        "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )

    # simulate a click on the open_file_button
    controller.widget.open_file_button.click()
    controller.picker.frame.setCurrentText("t")
    controller.picker.track_id.setCurrentText("id")
    controller.picker.x_coordinates.setCurrentText("x")
    controller.picker.y_coordinates.setCurrentText("y")
    controller.picker.z_coordinates.setCurrentText("None")
    controller.picker.measurement.setCurrentText("m")
    controller.picker.measurement_math.setCurrentText("None")
    controller.picker.second_measurement.setCurrentText("None")
    controller.picker.field_of_view_id.setCurrentText("Position")
    controller.picker.additional_filter.setCurrentText("None")

    # need this event loop thingy to wait for the creation of the preprocessing worker
    loop = QEventLoop()
    controller.loading_thread.finished.connect(loop.quit)
    # press abort to close the picker widget
    controller.picker.abort_button.click()
    loop.exec_()
    catptured = capsys.readouterr()
    assert controller.data_storage_instance.original_data.value.empty
    assert "Loading aborted" in catptured.out
