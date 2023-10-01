from __future__ import annotations

import gc
from typing import TYPE_CHECKING
from unittest.mock import patch

import pandas as pd
import pytest
from arcos_gui._main_widget import MainWindow
from arcos_gui.processing._arcos_wrapper import calculate_arcos_stats
from arcos_gui.tools._config import ARCOS_LAYERS
from pytestqt.qtbot import QtBot

if TYPE_CHECKING:
    import napari.viewer


@pytest.fixture()
def dock_arcos_widget(make_napari_viewer, qtbot):
    from arcos_gui._main_widget import MainWindow

    viewer = make_napari_viewer()
    mywidget = MainWindow(viewer=viewer)
    qtbot.addWidget(mywidget)
    yield viewer, mywidget, qtbot
    mywidget.deleteLater()
    viewer.close()
    gc.collect()


@pytest.fixture()
def dock_arcos_widget_w_colnames_set(
    dock_arcos_widget: tuple[napari.viewer.Viewer, MainWindow, QtBot]
):
    viewer, mywidget, qtbot = dock_arcos_widget
    mywidget.data.columns.value.frame_column = "t"
    mywidget.data.columns.value.object_id = "id"
    mywidget.data.columns.value.x_column = "x"
    mywidget.data.columns.value.y_column = "y"
    mywidget.data.columns.value.z_column = None
    mywidget.data.columns.value.measurement_column = "m"
    mywidget.data.columns.value.measurement_column_1 = "m"
    mywidget.data.columns.value.measurement_column_2 = None
    mywidget.data.columns.value.position_id = "Position"
    mywidget.data.columns.value.additional_filter_column = None
    mywidget.data.columns.value.measurement_math_operation = None
    mywidget.data.columns.value.measurement_bin = "m"
    mywidget.data.columns.value.measurement_resc = "m"
    return viewer, mywidget, qtbot


def test_get_instance_no_instance():
    from arcos_gui._main_widget import MainWindow

    assert MainWindow.get_last_instance() is None


def test_init(dock_arcos_widget: tuple[napari.viewer.Viewer, MainWindow, QtBot]):
    viewer, widget, qtbot = dock_arcos_widget
    assert widget is not None


def test_get_instance(dock_arcos_widget):
    _, mywidget, qtbot = dock_arcos_widget
    assert mywidget.get_last_instance() is not None


@patch("qtpy.QtWidgets.QFileDialog.getOpenFileName")
def test_load_data(
    mock_browse_data, dock_arcos_widget: tuple[napari.viewer.Viewer, MainWindow, QtBot]
):
    viewer, mywidget, qtbot = dock_arcos_widget
    mock_browse_data.return_value = (
        "src/arcos_gui/_tests/test_data/arcos_data.csv",
        "csv (*.csv)",
    )
    mywidget._input_controller.widget.browse_file.click()
    assert (
        mywidget._input_controller.widget.file_LineEdit.text()
        == "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )

    # asser that there indeed is no data loaded for now
    assert mywidget.data.original_data.value.empty
    # check if data was filtered / filtered_data was updated
    assert mywidget.data.filtered_data.value.empty

    # user sets columnames
    mywidget._input_controller.widget.load_data_button.click()
    mywidget._input_controller.picker.frame.setCurrentText("t")
    mywidget._input_controller.picker.track_id.setCurrentText("id")
    mywidget._input_controller.picker.x_coordinates.setCurrentText("x")
    mywidget._input_controller.picker.y_coordinates.setCurrentText("y")
    mywidget._input_controller.picker.z_coordinates.setCurrentText("None")
    mywidget._input_controller.picker.measurement.setCurrentText("m")
    mywidget._input_controller.picker.second_measurement.setCurrentText("None")
    mywidget._input_controller.picker.field_of_view_id.setCurrentText("None")
    mywidget._input_controller.picker.additional_filter.setCurrentText("None")
    mywidget._input_controller.picker.measurement_math.setCurrentText("None")
    # user clicks ok
    with qtbot.waitSignal(mywidget._input_controller.loading_worker.finished):
        mywidget._input_controller.picker.ok_button.click()

    columnames_list = mywidget.data.columns.value.pickablepickable_columns_names
    assert columnames_list == [
        "t",
        "id",
        "x",
        "y",
        None,
        "m",
        None,
        None,
        None,
        None,
    ]
    # check if data is loaded
    assert mywidget.data.original_data.value.empty is False
    # check if data was filtered / filtered_data was updated
    assert mywidget.data.filtered_data.value.empty is False


@patch("qtpy.QtWidgets.QFileDialog.getOpenFileName")
def test_load_data_with_additional_filter(
    mock_browse_data,
    dock_arcos_widget: tuple[
        napari.viewer.Viewer,
        MainWindow,
        QtBot,
    ],
):
    viewer, mywidget, qtbot = dock_arcos_widget
    mock_browse_data.return_value = (
        "src/arcos_gui/_tests/test_data/arcos_data.csv",
        "csv (*.csv)",
    )
    mywidget._input_controller.widget.browse_file.click()
    assert (
        mywidget._input_controller.widget.file_LineEdit.text()
        == "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )

    # asser that there indeed is no data loaded for now
    assert mywidget.data.original_data.value.empty
    # check if data was filtered / filtered_data was updated
    assert mywidget.data.filtered_data.value.empty

    # user sets columnames
    mywidget._input_controller.widget.load_data_button.click()
    mywidget._input_controller.picker.frame.setCurrentText("t")
    mywidget._input_controller.picker.track_id.setCurrentText("id")
    mywidget._input_controller.picker.x_coordinates.setCurrentText("x")
    mywidget._input_controller.picker.y_coordinates.setCurrentText("y")
    mywidget._input_controller.picker.z_coordinates.setCurrentText("None")
    mywidget._input_controller.picker.measurement.setCurrentText("m")
    mywidget._input_controller.picker.second_measurement.setCurrentText("None")
    mywidget._input_controller.picker.field_of_view_id.setCurrentText("None")
    mywidget._input_controller.picker.additional_filter.setCurrentText("id")
    mywidget._input_controller.picker.measurement_math.setCurrentText("None")

    with qtbot.waitSignal(mywidget._input_controller.loading_worker.finished):
        mywidget._input_controller.picker.ok_button.click()

    columnames_list = mywidget.data.columns.value.pickablepickable_columns_names
    assert columnames_list == [
        "t",
        "id",
        "x",
        "y",
        None,
        "m",
        None,
        None,
        "id",
        None,
    ]
    # check if data is loaded
    assert mywidget.data.original_data.value.empty is False
    # check if data was filtered / filtered_data was updated
    assert mywidget.data.filtered_data.value.empty is False


@patch("qtpy.QtWidgets.QFileDialog.getOpenFileName")
def test_load_data_with_measurement_math(
    mock_browse_data, dock_arcos_widget: tuple[napari.viewer.Viewer, MainWindow, QtBot]
):
    viewer, mywidget, qtbot = dock_arcos_widget = dock_arcos_widget
    test_df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    mock_browse_data.return_value = (
        "src/arcos_gui/_tests/test_data/arcos_data.csv",
        "csv (*.csv)",
    )
    mywidget._input_controller.widget.browse_file.click()
    assert (
        mywidget._input_controller.widget.file_LineEdit.text()
        == "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )

    # asser that there indeed is no data loaded for now
    assert mywidget.data.original_data.value.empty
    # check if data was filtered / filtered_data was updated
    assert mywidget.data.filtered_data.value.empty

    # user sets columnames
    mywidget._input_controller.widget.load_data_button.click()
    mywidget._input_controller.picker.frame.setCurrentText("t")
    mywidget._input_controller.picker.track_id.setCurrentText("id")
    mywidget._input_controller.picker.x_coordinates.setCurrentText("x")
    mywidget._input_controller.picker.y_coordinates.setCurrentText("y")
    mywidget._input_controller.picker.z_coordinates.setCurrentText("None")
    mywidget._input_controller.picker.measurement.setCurrentText("m")
    mywidget._input_controller.picker.second_measurement.setCurrentText("m")
    mywidget._input_controller.picker.field_of_view_id.setCurrentText("None")
    mywidget._input_controller.picker.additional_filter.setCurrentText("None")
    mywidget._input_controller.picker.measurement_math.setCurrentText("Add")
    # user clicks ok
    with qtbot.waitSignal(mywidget._input_controller.loading_worker.finished):
        mywidget._input_controller.picker.ok_button.click()

    columnames_list = mywidget.data.columns.value.pickablepickable_columns_names
    assert columnames_list == [
        "t",
        "id",
        "x",
        "y",
        None,
        "m",
        "m",
        None,
        None,
        "Add",
    ]
    # check if data is loaded
    assert mywidget.data.original_data.value.empty is False
    # check if data was filtered / filtered_data was updated
    assert mywidget.data.filtered_data.value.empty is False
    assert (
        mywidget.data.original_data.value["Measurement_Sum"].sum() / 2
        == test_df["m"].sum()
    )


def test_add_binarization_layers_with_data(
    dock_arcos_widget_w_colnames_set: tuple[napari.viewer.Viewer, MainWindow, QtBot]
):
    viewer, mywidget, qtbot = dock_arcos_widget_w_colnames_set
    test_df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    mywidget.data.original_data.value = test_df
    mywidget.data.filtered_data.value = test_df[test_df["Position"] == 1]

    mywidget._arcos_widget.widget.run_binarization_only.click()
    qtbot.waitSignal(mywidget._arcos_widget.worker.finished)

    # Wait until the condition is met (or timeout after 5 seconds)
    qtbot.waitUntil(lambda: len(viewer.layers) == 2, timeout=5000)

    assert viewer.layers[0].name == ARCOS_LAYERS["all_cells"]
    assert viewer.layers[1].name == ARCOS_LAYERS["active_cells"]


def test_add_all_layers_with_data(
    dock_arcos_widget_w_colnames_set: tuple[napari.viewer.Viewer, MainWindow, QtBot]
):
    viewer, mywidget, qtbot = dock_arcos_widget_w_colnames_set
    test_df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    arcos_df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_output.csv")
    mywidget.data.original_data.value = test_df
    mywidget.data.filtered_data.value = test_df[test_df["Position"] == 1]
    mywidget.data.arcos_binarization.value = test_df[test_df["Position"] == 1]
    mywidget.data.arcos_stats.value = calculate_arcos_stats(
        arcos_df,
        frame_col="t",
        collid_name="collid",
        object_id_name="id",
        posCols=["x", "y"],
    )
    mywidget.data.arcos_output.value = arcos_df

    mywidget._arcos_widget.widget.update_arcos.click()
    qtbot.waitSignal(mywidget._arcos_widget.worker.finished)
    qtbot.waitUntil(lambda: len(viewer.layers) == 4, timeout=5000)

    assert len(viewer.layers) == 4
    assert viewer.layers[0].name == ARCOS_LAYERS["all_cells"]
    assert viewer.layers[1].name == ARCOS_LAYERS["active_cells"]
    assert viewer.layers[2].name == ARCOS_LAYERS["collective_events_cells"]
    assert viewer.layers[3].name == ARCOS_LAYERS["event_hulls"]


def test_first_all_then_bin(
    dock_arcos_widget_w_colnames_set: tuple[napari.viewer.Viewer, MainWindow, QtBot]
):
    viewer, mywidget, qtbot = dock_arcos_widget_w_colnames_set
    test_df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    arcos_df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_output.csv")
    mywidget.data.original_data.value = test_df
    mywidget.data.filtered_data.value = test_df[test_df["Position"] == 1]
    mywidget.data.arcos_binarization.value = test_df[test_df["Position"] == 1]
    mywidget.data.arcos_stats.value = calculate_arcos_stats(
        arcos_df,
        frame_col="t",
        collid_name="collid",
        object_id_name="id",
        posCols=["x", "y"],
    )
    mywidget.data.arcos_output.value = arcos_df
    mywidget._arcos_widget.widget.update_arcos.click()
    qtbot.waitSignal(mywidget._arcos_widget.worker.finished)
    qtbot.waitUntil(lambda: len(viewer.layers) == 4, timeout=5000)

    assert len(viewer.layers) == 4
    assert viewer.layers[0].name == ARCOS_LAYERS["all_cells"]
    assert viewer.layers[1].name == ARCOS_LAYERS["active_cells"]
    assert viewer.layers[2].name == ARCOS_LAYERS["collective_events_cells"]
    assert viewer.layers[3].name == ARCOS_LAYERS["event_hulls"]

    mywidget._arcos_widget.widget.bin_threshold.setValue(0.5)
    mywidget._arcos_widget.widget.run_binarization_only.click()
    qtbot.waitSignal(mywidget._arcos_widget.worker.finished)
    qtbot.waitUntil(lambda: len(viewer.layers) == 2, timeout=5000)

    assert len(viewer.layers) == 2
    assert viewer.layers[0].name == ARCOS_LAYERS["all_cells"]
    assert viewer.layers[1].name == ARCOS_LAYERS["active_cells"]


def test_increase_points_size(
    dock_arcos_widget_w_colnames_set: tuple[napari.viewer.Viewer, MainWindow, QtBot]
):
    viewer, mywidget, qtbot = dock_arcos_widget_w_colnames_set
    test_df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    mywidget.data.original_data.value = test_df
    mywidget.data.filtered_data.value = test_df[test_df["Position"] == 1]

    mywidget._arcos_widget.widget.run_binarization_only.click()
    qtbot.waitSignal(mywidget._arcos_widget.worker.finished)
    qtbot.waitUntil(lambda: len(viewer.layers) == 2, timeout=5000)

    assert len(viewer.layers) == 2
    assert viewer.layers[0].name == ARCOS_LAYERS["all_cells"]
    assert viewer.layers[1].name == ARCOS_LAYERS["active_cells"]
    starting_pointsize = mywidget._layer_prop_controller.widget.point_size.value()
    assert viewer.layers[0].size.flatten()[0] == starting_pointsize
    mywidget._layer_prop_controller.widget.point_size.setValue(20)
    new_pointsize = mywidget._layer_prop_controller.widget.point_size.value()
    assert viewer.layers[0].size.flatten()[0] == new_pointsize
