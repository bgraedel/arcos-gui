from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest
from arcos_gui.processing import DataStorage
from arcos_gui.widgets import InputdataController
from qtpy.QtCore import QEventLoop, Qt

if TYPE_CHECKING:
    import napari
    from pytestqt.qtbot import QtBot


@pytest.fixture()
def make_input_widget(qtbot, make_napari_viewer):
    ds = DataStorage()
    viewer = make_napari_viewer()
    controller = InputdataController(ds, print, viewer)
    qtbot.addWidget(controller.widget)
    yield controller, qtbot
    try:
        controller.closeEvent()
    except RuntimeError:
        pass
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
    qtbot.mouseClick(controller.widget.load_data_button, Qt.LeftButton)

    # assert that the columnpicker window was opened
    assert controller.picker.isVisibleTo(controller.widget)
    qtbot.mouseClick(controller.picker.abort_button, Qt.LeftButton)
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
    qtbot.mouseClick(controller.widget.load_data_button, Qt.LeftButton)

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
    qtbot.mouseClick(controller.widget.load_data_button, Qt.LeftButton)

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
    qtbot.mouseClick(controller.widget.load_data_button, Qt.LeftButton)
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
    qtbot.mouseClick(controller.widget.load_data_button, Qt.LeftButton)
    column_names = [
        "t",
        "id",
        "x",
        "y",
        None,
        "m",
        None,
        "Position",
        None,
        None,
    ]
    qtbot.mouseClick(controller.picker.ok_button, Qt.LeftButton)

    assert controller.picker.get_column_names == column_names
    controller.widget.close()


def test_data_loading(make_input_widget: tuple[InputdataController, QtBot]):
    # need this event loop thingy to wait for the creation of the preprocessing worker
    loopy = QEventLoop()
    controller, qtbot = make_input_widget

    # set the file_LineEdit field to a csv file path
    controller.widget.file_LineEdit.setText(
        "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )
    # simulate a click on the open_file_button
    qtbot.mouseClick(controller.widget.load_data_button, Qt.LeftButton)
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
    controller.loading_worker.started.connect(lambda: print("started"))
    controller.loading_worker.finished.connect(lambda: print("finished"))
    controller.loading_worker.finished.connect(lambda: print("worker finished"))
    # quit event loop when the thread is finished
    controller.loading_worker.finished.connect(loopy.quit)

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
    controller.widget.load_data_button.click()
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

    with qtbot.waitSignal(controller.loading_worker.finished):
        # press abort to close the picker widget
        controller.picker.abort_button.click()

    catptured = capsys.readouterr()
    assert controller.data_storage_instance.original_data.value.empty
    assert "Loading aborted" in catptured.out


def test_on_selection(make_input_widget: tuple[InputdataController, QtBot]):
    controller, qtbot = make_input_widget

    # Add mock layers to the viewer's layers
    controller.viewer.add_labels(np.zeros((10, 10), dtype=int), name="labels")
    controller.viewer.add_tracks(np.random.rand(5, 4).astype(int), name="random tracks")
    controller._on_selection()

    # Check that the lists in the widget are updated as expected
    assert controller.widget.data_layer_selector.count() == 1
    assert (
        controller.widget.tracks_layer_selector.count() == 2
    )  # One for 'None', one for the track layer


def test_update_labels_layers_list(
    make_input_widget: tuple[InputdataController, QtBot]
):
    controller, qtbot = make_input_widget

    # Mock layers in the viewer
    controller.viewer.add_labels(np.zeros((10, 10), dtype=int), name="labels")
    controller.viewer.add_labels(np.zeros((10, 10), dtype=int), name="labels")
    controller._update_labels_layers_list()

    # Check that the list in the widget has the right count
    assert controller.widget.data_layer_selector.count() == 2


def test_update_tracks_layers_list(
    make_input_widget: tuple[InputdataController, QtBot]
):
    controller, qtbot = make_input_widget

    # Mock layers in the viewer
    controller.viewer.add_tracks(np.random.rand(5, 4).astype(int), name="random tracks")
    controller.viewer.add_tracks(np.random.rand(5, 4).astype(int), name="random tracks")
    controller._update_tracks_layers_list()

    # Check that the list in the widget has the right count
    assert (
        controller.widget.tracks_layer_selector.count() == 3
    )  # One for 'None', two for the track layers


def test_convert_selected_tracks_layer_data_to_dataframe(
    make_input_widget: tuple[InputdataController, QtBot]
):
    controller, qtbot = make_input_widget

    # Mock the layer
    layer = MagicMock()
    layer.data = np.random.rand(5, 4).astype(int)
    layer.properties = {"track_id": np.arange(5)}
    layer.name = "random tracks"
    controller.viewer.add_tracks(layer.data, name=layer.name)
    controller._update_tracks_layers_list()

    # Mock the layer selector
    controller.widget.tracks_layer_selector.setCurrentIndex(1)

    # Convert the layer data to a dataframe
    df = controller._convert_selected_tracks_layer_data_to_dataframe()

    # Check that the dataframe has the right shape
    assert df.shape == (5, 4)


def test_set_loading_worker_columnpicker(
    make_input_widget: tuple[InputdataController, QtBot]
):
    controller, qtbot = make_input_widget

    # Mock the worker
    controller.loading_worker = Mock()
    controller._set_loading_worker_columnpicker()

    # Check that the worker's attribute was set correctly
    assert not controller.loading_worker.wait_for_columnpicker


def test_abort_loading_worker(make_input_widget: tuple[InputdataController, QtBot]):
    controller, qtbot = make_input_widget

    # Mock the worker
    controller.loading_worker = Mock()
    controller._abort_loading_worker()

    # Check that the worker's attributes were set correctly
    assert not controller.loading_worker.wait_for_columnpicker
    assert controller.loading_worker.abort_loading


def test_succesfully_loaded_from_layer(
    make_input_widget: tuple[InputdataController, QtBot]
):
    controller, qtbot = make_input_widget

    # Mock the necessary methods and data
    mock_dataframe = pd.DataFrame()

    with patch.object(
        controller,
        "_convert_selected_tracks_layer_data_to_dataframe",
        return_value="mock_df",
    ) as mock_method:
        with patch.object(
            controller, "_run_dataframe_matching", return_value=mock_dataframe
        ) as mock_method2:
            # Call the method
            controller._succesfully_loaded_from_layer(mock_dataframe)
            controller.picker.set_column_names(
                ["From napari tracks layer", "mock_frame_column", "x", "y"]
            )
            controller.picker.track_id.setCurrentText("From napari tracks layer")
            controller.picker.frame.setCurrentText("mock_frame_column")
            controller.picker.x_coordinates.setCurrentText("x")
            controller.picker.y_coordinates.setCurrentText("y")

            # Call the method
            controller._succesfully_loaded_from_layer(mock_dataframe)

            # Check that the methods were called with the expected arguments
            mock_method.assert_called_once()
            mock_method2.assert_called_with(
                mock_dataframe, "mock_df", "mock_frame_column", ["y", "x"]
            )


@patch("arcos_gui.widgets._input_data_widget.preprocess_data")
def test_on_matching_success(
    mock_preprocess, make_input_widget: tuple[InputdataController, QtBot]
):
    mock_preprocessed_df = Mock(spec=pd.DataFrame)
    matched_df = Mock(spec=pd.DataFrame)
    mock_preprocess.return_value = ("mock_out_meas_name", mock_preprocessed_df)
    controller, qtbot = make_input_widget

    controller._on_matching_success(matched_df)

    # Check that the data storage instance was updated correctly
    assert (
        controller.data_storage_instance.columns.value.measurement_column
        == "mock_out_meas_name"
    )
    assert controller.data_storage_instance.original_data.value == mock_preprocessed_df


@patch("arcos_gui.widgets._input_data_widget.DataFrameMatcher")
def test_run_dataframe_matching(
    mock_DataFrameMatcher,
    make_input_widget: tuple[InputdataController, QtBot],
):
    controller, qtbot = make_input_widget

    # Mock the necessary methods and data
    df1, df2, frame_col, coord_cols1 = Mock(), Mock(), Mock(), Mock()

    # Call the method
    controller._run_dataframe_matching(df1, df2, frame_col, coord_cols1)

    # Check that the methods were called with the expected arguments and the thread was started
    mock_DataFrameMatcher.assert_called_once_with(
        df1, df2, frame_col=frame_col, coord_cols1=coord_cols1
    )
    controller.matching_worker.start.assert_called_once()


def test_matching_aborted(make_input_widget: tuple[InputdataController, QtBot], capsys):
    controller, qtbot = make_input_widget

    # Mock the necessary methods and data
    controller.matching_worker = Mock()
    controller.matching_worker.abort_loading = True

    # Call the method
    controller._matching_aborted("error message")

    catptured = capsys.readouterr()
    assert "error message" in catptured.out

    # Check that the data storage instance was updated correctly
    assert (
        controller.data_storage_instance.columns.value.measurement_column
        == "measurement"
    )  # i.e. default value
    assert controller.data_storage_instance.original_data.value.empty


def test_set_datastorage_to_default(
    make_input_widget: tuple[InputdataController, QtBot]
):
    controller, qtbot = make_input_widget

    # Mock the necessary methods and data
    controller.data_storage_instance = Mock()
    controller.data_storage_instance.original_data.value = Mock(spec=pd.DataFrame)
    controller.data_storage_instance.columns.measurement_column = "mock_meas_col"

    # Call the method
    controller._set_datastorage_to_default()

    # Check that the data storage instance was updated correctly
    assert controller.data_storage_instance.original_data.value.empty


def test_convert_selected_layer_properties_to_dataframe(
    make_input_widget: tuple[InputdataController, QtBot]
):
    controller, _ = make_input_widget

    # Mock the layer
    layer = MagicMock()
    layer.properties = {"frame": np.arange(5), "id": np.arange(5)}
    layer.name = "labels"
    controller.viewer.add_labels(
        np.zeros((10, 10), dtype=int), name=layer.name, properties=layer.properties
    )

    controller.widget.data_layer_selector.setCurrentRow(0)

    # Convert the layer data to a dataframe
    df = controller._convert_selected_layer_properties_to_dataframe()

    # Check that the dataframe has the right shape
    assert df.shape == (5, 2)


def test_load_data_from_labels_no_tracks(
    make_input_widget: tuple[InputdataController, QtBot]
):
    controller, _ = make_input_widget
    viewer = controller.viewer
    properties = {
        "labels": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "t": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "x": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "y": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "m": [1, 2, 3, 1, 2, 3, 1, 2, 3],
    }
    viewer.add_labels(np.random.randint(0, 3, size=(10, 10)), properties=properties)

    assert controller.data_storage_instance.original_data.value.empty

    controller.widget.from_layers_selector.click()
    controller.widget.data_layer_selector.setCurrentRow(0)
    controller.widget.load_data_button.click()

    assert controller.picker.isVisibleTo(controller.widget)

    controller.picker.frame.setCurrentText("t")
    controller.picker.track_id.setCurrentText("None")
    controller.picker.x_coordinates.setCurrentText("x")
    controller.picker.y_coordinates.setCurrentText("y")
    controller.picker.z_coordinates.setCurrentText("None")
    controller.picker.measurement.setCurrentText("m")
    controller.picker.second_measurement.setCurrentText("None")
    controller.picker.field_of_view_id.setCurrentText("None")
    controller.picker.additional_filter.setCurrentText("None")
    controller.picker.measurement_math.setCurrentText("None")
    controller.picker.ok_button.click()

    assert controller.data_storage_instance.original_data.value.empty is False


def test_load_data_from_labels(make_input_widget: tuple[InputdataController, QtBot]):
    controller, qtbot = make_input_widget
    viewer: napari.viewer.Viewer = controller.viewer
    properties = {
        "labels": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "t": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "x": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "y": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "m": [1, 2, 3, 1, 2, 3, 1, 2, 3],
    }
    tracks = np.array(
        [
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [3, 3, 3, 3],
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [3, 3, 3, 3],
            [1, 1, 1, 1],
            [2, 2, 2, 2],
            [3, 3, 3, 3],
        ]
    )

    viewer.add_labels(np.random.randint(0, 3, size=(3, 10, 10)), properties=properties)
    viewer.add_tracks(tracks, properties=properties)

    assert controller.data_storage_instance.original_data.value.empty

    controller.widget.from_layers_selector.click()
    controller.widget.data_layer_selector.setCurrentRow(0)
    controller.widget.tracks_layer_selector.setCurrentIndex(1)
    controller.widget.load_data_button.click()

    assert controller.picker.isVisibleTo(controller.widget)

    controller.picker.frame.setCurrentText("t")
    controller.picker.track_id.setCurrentText("From napari tracks layer")
    controller.picker.x_coordinates.setCurrentText("x")
    controller.picker.y_coordinates.setCurrentText("y")
    controller.picker.z_coordinates.setCurrentText("None")
    controller.picker.measurement.setCurrentText("m")
    controller.picker.second_measurement.setCurrentText("None")
    controller.picker.field_of_view_id.setCurrentText("None")
    controller.picker.additional_filter.setCurrentText("None")
    controller.picker.measurement_math.setCurrentText("None")
    controller.picker.ok_button.click()
    qtbot.waitSignal(controller.matching_worker.finished)
    # wait until original_data is not empty
    qtbot.waitUntil(
        lambda: controller.data_storage_instance.original_data.value.empty is False,
        timeout=1000,
    )

    assert controller.data_storage_instance.original_data.value.empty is False
    assert controller.data_storage_instance.original_data.value[
        "track_id"
    ].unique().tolist() == [1, 2, 3]


def test_load_data_from_multiple_label_properties(
    make_input_widget: tuple[InputdataController, QtBot]
):
    controller, _ = make_input_widget
    viewer: napari.viewer.Viewer = controller.viewer
    properties = {
        "label": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "frame": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "x": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "y": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "m": [1, 2, 3, 1, 2, 3, 1, 2, 3],
    }

    viewer.add_labels(
        np.random.randint(0, 3, size=(3, 10, 10)), properties=properties, name="labels1"
    )
    viewer.add_labels(
        np.random.randint(0, 3, size=(3, 10, 10)), properties=properties, name="labels2"
    )

    assert controller.data_storage_instance.original_data.value.empty

    controller.widget.from_layers_selector.click()
    controller.widget.data_layer_selector.item(0).setSelected(True)
    controller.widget.data_layer_selector.item(1).setSelected(True)
    controller.widget.tracks_layer_selector.setCurrentIndex(1)
    controller.widget.load_data_button.click()

    assert controller.picker.isVisibleTo(controller.widget)

    controller.picker.frame.setCurrentText("t_labels1")
    controller.picker.track_id.setCurrentText("None")
    controller.picker.x_coordinates.setCurrentText("x_labels1")
    controller.picker.y_coordinates.setCurrentText("y_labels2")
    controller.picker.z_coordinates.setCurrentText("None")
    controller.picker.measurement.setCurrentText("m_labels2")
    controller.picker.second_measurement.setCurrentText("None")
    controller.picker.field_of_view_id.setCurrentText("None")
    controller.picker.additional_filter.setCurrentText("None")
    controller.picker.measurement_math.setCurrentText("None")
    controller.picker.ok_button.click()

    assert controller.data_storage_instance.original_data.value.empty is False
    assert controller.data_storage_instance.original_data.value[
        "x_labels1"
    ].unique().tolist() == [1, 2, 3]
    assert controller.data_storage_instance.original_data.value[
        "y_labels2"
    ].unique().tolist() == [1, 2, 3]


def test_load_data_from_multiple_label_properties_with_tracks_fail(
    make_input_widget: tuple[InputdataController, QtBot], capsys
):
    controller, qtbot = make_input_widget
    viewer: napari.viewer.Viewer = controller.viewer
    properties = {
        "labels": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "t": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "x": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "y": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "m": [1, 2, 3, 1, 2, 3, 1, 2, 3],
    }
    tracks = np.array(
        [
            [1, 1, 5, 1],
            [2, 2, 6, 2],
            [3, 3, 7, 3],
            [1, 1, 5, 1],
            [2, 2, 6, 2],
            [3, 3, 7, 3],
            [1, 1, 5, 1],
            [2, 2, 6, 2],
            [3, 3, 7, 3],
        ]
    )

    viewer.add_labels(np.random.randint(0, 3, size=(3, 10, 10)), properties=properties)
    viewer.add_tracks(tracks, properties=properties)

    assert controller.data_storage_instance.original_data.value.empty

    controller.widget.from_layers_selector.click()
    controller.widget.data_layer_selector.setCurrentRow(0)
    controller.widget.tracks_layer_selector.setCurrentIndex(1)
    # Initiate the worker
    controller.widget.load_data_button.click()

    assert controller.picker.isVisibleTo(controller.widget)

    controller.picker.frame.setCurrentText("t")
    controller.picker.track_id.setCurrentText("From napari tracks layer")
    controller.picker.x_coordinates.setCurrentText("x")
    controller.picker.y_coordinates.setCurrentText("y")
    controller.picker.z_coordinates.setCurrentText("None")
    controller.picker.measurement.setCurrentText("m")
    controller.picker.second_measurement.setCurrentText("None")
    controller.picker.field_of_view_id.setCurrentText("None")
    controller.picker.additional_filter.setCurrentText("None")
    controller.picker.measurement_math.setCurrentText("None")

    controller.picker.ok_button.click()
    qtbot.waitSignal(controller.matching_worker.finished)
    qtbot.wait(500)

    capture_output = capsys.readouterr()
    assert (
        "Direct merge of tracking data failed, falling back to nearest neighbor approach"
        in capture_output.out
    )
    assert controller.data_storage_instance.original_data.value.empty
