from __future__ import annotations

import gc
from typing import TYPE_CHECKING
from unittest.mock import patch

import pandas as pd
import pytest
from arcos_gui.tools._config import ARCOS_LAYERS
from qtpy.QtCore import QEventLoop

if TYPE_CHECKING:
    import napari.viewer
    from arcos_gui._main_widget import MainWindow


@pytest.fixture()
def dock_arcos_widget(make_napari_viewer, qtbot):
    viewer = make_napari_viewer()
    mywidget = viewer.window.add_plugin_dock_widget(
        plugin_name="arcos-gui", widget_name="ARCOS Main Widget"
    )
    yield viewer, mywidget[1]
    viewer.close()
    gc.collect()


@pytest.fixture()
def dock_arcos_widget_w_colnames_set(
    dock_arcos_widget: tuple[napari.viewer.Viewer, MainWindow]
):
    viewer, mywidget = dock_arcos_widget
    mywidget.data_storage_instance.columns.frame_column = "t"
    mywidget.data_storage_instance.columns.object_id = "id"
    mywidget.data_storage_instance.columns.x_column = "x"
    mywidget.data_storage_instance.columns.y_column = "y"
    mywidget.data_storage_instance.columns.z_column = "None"
    mywidget.data_storage_instance.columns.measurement_column = "m"
    mywidget.data_storage_instance.columns.measurement_column_1 = "m"
    mywidget.data_storage_instance.columns.measurement_column_2 = "None"
    mywidget.data_storage_instance.columns.position_id = "Position"
    mywidget.data_storage_instance.columns.additional_filter_column = "None"
    mywidget.data_storage_instance.columns.measurement_math_operatoin = "None"
    mywidget.data_storage_instance.columns.measurement_bin = "m"
    mywidget.data_storage_instance.columns.measurement_resc = "m"
    return viewer, mywidget


def test_init(dock_arcos_widget):
    viewer, mywidget = dock_arcos_widget
    assert "ARCOS Main Widget (arcos-gui)" in [i for i in viewer.window._dock_widgets]


@patch("qtpy.QtWidgets.QFileDialog.getOpenFileName")
def test_load_data(
    mock_browse_data, dock_arcos_widget: tuple[napari.viewer.Viewer, MainWindow]
):
    viewer, mywidget = dock_arcos_widget
    mock_browse_data.return_value = (
        "src/arcos_gui/_tests/test_data/arcos_data.csv",
        "csv (*.csv)",
    )
    mywidget.input_data_widget.browse_file.click()
    assert (
        mywidget.input_data_widget.file_LineEdit.text()
        == "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )

    # asser that there indeed is no data loaded for now
    assert mywidget.data_storage_instance.original_data.value.empty
    # check if data was filtered / filtered_data was updated
    assert mywidget.data_storage_instance.filtered_data.value.empty

    # user sets columnames
    mywidget.input_data_widget.open_file_button.click()
    mywidget.input_data_widget.picker.frame.setCurrentText("t")
    mywidget.input_data_widget.picker.track_id.setCurrentText("id")
    mywidget.input_data_widget.picker.x_coordinates.setCurrentText("x")
    mywidget.input_data_widget.picker.y_coordinates.setCurrentText("y")
    mywidget.input_data_widget.picker.z_coordinates.setCurrentText("None")
    mywidget.input_data_widget.picker.measurement.setCurrentText("m")
    mywidget.input_data_widget.picker.second_measurement.setCurrentText("None")
    mywidget.input_data_widget.picker.field_of_view_id.setCurrentText("None")
    mywidget.input_data_widget.picker.additional_filter.setCurrentText("None")
    mywidget.input_data_widget.picker.measurement_math.setCurrentText("None")
    # user clicks ok
    mywidget.input_data_widget.picker.Ok.click()

    # need this event loop thingy to wait for the creation of the preprocessing worker
    loop = QEventLoop()
    mywidget.input_data_widget.loading_worker.finished.connect(loop.quit)
    loop.exec_()
    columnames_list = (
        mywidget.data_storage_instance.columns.pickablepickable_columns_names
    )
    assert columnames_list == [
        "t",
        "id",
        "x",
        "y",
        "None",
        "m",
        "None",
        "None",
        "None",
        "None",
    ]
    # check if data is loaded
    assert mywidget.data_storage_instance.original_data.value.empty is False
    # check if data was filtered / filtered_data was updated
    assert mywidget.data_storage_instance.filtered_data.value.empty is False


@patch("qtpy.QtWidgets.QFileDialog.getOpenFileName")
def test_load_data_with_additional_filter(
    mock_browse_data, dock_arcos_widget: tuple[napari.viewer.Viewer, MainWindow]
):
    viewer, mywidget = dock_arcos_widget
    mock_browse_data.return_value = (
        "src/arcos_gui/_tests/test_data/arcos_data.csv",
        "csv (*.csv)",
    )
    mywidget.input_data_widget.browse_file.click()
    assert (
        mywidget.input_data_widget.file_LineEdit.text()
        == "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )

    # asser that there indeed is no data loaded for now
    assert mywidget.data_storage_instance.original_data.value.empty
    # check if data was filtered / filtered_data was updated
    assert mywidget.data_storage_instance.filtered_data.value.empty

    # user sets columnames
    mywidget.input_data_widget.open_file_button.click()
    mywidget.input_data_widget.picker.frame.setCurrentText("t")
    mywidget.input_data_widget.picker.track_id.setCurrentText("id")
    mywidget.input_data_widget.picker.x_coordinates.setCurrentText("x")
    mywidget.input_data_widget.picker.y_coordinates.setCurrentText("y")
    mywidget.input_data_widget.picker.z_coordinates.setCurrentText("None")
    mywidget.input_data_widget.picker.measurement.setCurrentText("m")
    mywidget.input_data_widget.picker.second_measurement.setCurrentText("None")
    mywidget.input_data_widget.picker.field_of_view_id.setCurrentText("None")
    mywidget.input_data_widget.picker.additional_filter.setCurrentText("id")
    mywidget.input_data_widget.picker.measurement_math.setCurrentText("None")
    # user clicks ok
    mywidget.input_data_widget.picker.Ok.click()

    # need this event loop thingy to wait for the creation of the preprocessing worker
    loop = QEventLoop()
    mywidget.input_data_widget.loading_worker.finished.connect(loop.quit)
    loop.exec_()
    columnames_list = (
        mywidget.data_storage_instance.columns.pickablepickable_columns_names
    )
    assert columnames_list == [
        "t",
        "id",
        "x",
        "y",
        "None",
        "m",
        "None",
        "None",
        "id",
        "None",
    ]
    # check if data is loaded
    assert mywidget.data_storage_instance.original_data.value.empty is False
    # check if data was filtered / filtered_data was updated
    assert mywidget.data_storage_instance.filtered_data.value.empty is False


@patch("qtpy.QtWidgets.QFileDialog.getOpenFileName")
def test_load_data_with_measurement_math(
    mock_browse_data, dock_arcos_widget: tuple[napari.viewer.Viewer, MainWindow]
):
    viewer, mywidget = dock_arcos_widget
    test_df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    mock_browse_data.return_value = (
        "src/arcos_gui/_tests/test_data/arcos_data.csv",
        "csv (*.csv)",
    )
    mywidget.input_data_widget.browse_file.click()
    assert (
        mywidget.input_data_widget.file_LineEdit.text()
        == "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )

    # asser that there indeed is no data loaded for now
    assert mywidget.data_storage_instance.original_data.value.empty
    # check if data was filtered / filtered_data was updated
    assert mywidget.data_storage_instance.filtered_data.value.empty

    # user sets columnames
    mywidget.input_data_widget.open_file_button.click()
    mywidget.input_data_widget.picker.frame.setCurrentText("t")
    mywidget.input_data_widget.picker.track_id.setCurrentText("id")
    mywidget.input_data_widget.picker.x_coordinates.setCurrentText("x")
    mywidget.input_data_widget.picker.y_coordinates.setCurrentText("y")
    mywidget.input_data_widget.picker.z_coordinates.setCurrentText("None")
    mywidget.input_data_widget.picker.measurement.setCurrentText("m")
    mywidget.input_data_widget.picker.second_measurement.setCurrentText("m")
    mywidget.input_data_widget.picker.field_of_view_id.setCurrentText("None")
    mywidget.input_data_widget.picker.additional_filter.setCurrentText("None")
    mywidget.input_data_widget.picker.measurement_math.setCurrentText("Add")
    # user clicks ok
    mywidget.input_data_widget.picker.Ok.click()

    # need this event loop thingy to wait for the creation of the preprocessing worker
    loop = QEventLoop()
    mywidget.input_data_widget.loading_worker.finished.connect(loop.quit)
    loop.exec_()
    columnames_list = (
        mywidget.data_storage_instance.columns.pickablepickable_columns_names
    )
    assert columnames_list == [
        "t",
        "id",
        "x",
        "y",
        "None",
        "m",
        "m",
        "None",
        "None",
        "Add",
    ]
    # check if data is loaded
    assert mywidget.data_storage_instance.original_data.value.empty is False
    # check if data was filtered / filtered_data was updated
    assert mywidget.data_storage_instance.filtered_data.value.empty is False
    assert (
        mywidget.data_storage_instance.original_data.value["Measurement_Sum"].sum() / 2
        == test_df["m"].sum()
    )


def test_add_binarization_layers_with_data(
    dock_arcos_widget_w_colnames_set: tuple[napari.viewer.Viewer, MainWindow]
):
    viewer, mywidget = dock_arcos_widget_w_colnames_set
    test_df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    mywidget.data_storage_instance.original_data.value = test_df
    mywidget.data_storage_instance.filtered_data.value = test_df[
        test_df["Position"] == 1
    ]
    mywidget.arcos_widget.run_binarization_only.click()
    assert len(viewer.layers) == 2
    assert viewer.layers[0].name == ARCOS_LAYERS["all_cells"]
    assert viewer.layers[1].name == ARCOS_LAYERS["active_cells"]


def test_add_all_layers_with_data(
    dock_arcos_widget_w_colnames_set: tuple[napari.viewer.Viewer, MainWindow]
):
    viewer, mywidget = dock_arcos_widget_w_colnames_set
    test_df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    arcos_df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_output.csv")
    mywidget.data_storage_instance.original_data.value = test_df
    mywidget.data_storage_instance.filtered_data.value = test_df[
        test_df["Position"] == 1
    ]
    mywidget.data_storage_instance.arcos_binarization.value = test_df[
        test_df["Position"] == 1
    ]
    mywidget.data_storage_instance.arcos_output.value = arcos_df
    mywidget.arcos_widget.update_arcos.click()
    assert len(viewer.layers) == 4
    assert viewer.layers[0].name == ARCOS_LAYERS["all_cells"]
    assert viewer.layers[1].name == ARCOS_LAYERS["active_cells"]
    assert viewer.layers[2].name == ARCOS_LAYERS["collective_events_cells"]
    assert viewer.layers[3].name == ARCOS_LAYERS["event_hulls"]


def test_first_all_then_bin(
    dock_arcos_widget_w_colnames_set: tuple[napari.viewer.Viewer, MainWindow]
):
    viewer, mywidget = dock_arcos_widget_w_colnames_set
    test_df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    arcos_df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_output.csv")
    mywidget.data_storage_instance.original_data.value = test_df
    mywidget.data_storage_instance.filtered_data.value = test_df[
        test_df["Position"] == 1
    ]
    mywidget.data_storage_instance.arcos_binarization.value = test_df[
        test_df["Position"] == 1
    ]
    mywidget.data_storage_instance.arcos_output.value = arcos_df
    mywidget.arcos_widget.update_arcos.click()
    assert len(viewer.layers) == 4
    assert viewer.layers[0].name == ARCOS_LAYERS["all_cells"]
    assert viewer.layers[1].name == ARCOS_LAYERS["active_cells"]
    assert viewer.layers[2].name == ARCOS_LAYERS["collective_events_cells"]
    assert viewer.layers[3].name == ARCOS_LAYERS["event_hulls"]
    mywidget.arcos_widget.bin_threshold.setValue(0.5)
    mywidget.arcos_widget.run_binarization_only.click()
    assert len(viewer.layers) == 2
    assert viewer.layers[0].name == ARCOS_LAYERS["all_cells"]
    assert viewer.layers[1].name == ARCOS_LAYERS["active_cells"]


def test_increase_points_size(
    dock_arcos_widget_w_colnames_set: tuple[napari.viewer.Viewer, MainWindow]
):
    viewer, mywidget = dock_arcos_widget_w_colnames_set
    test_df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    mywidget.data_storage_instance.original_data.value = test_df
    mywidget.data_storage_instance.filtered_data.value = test_df[
        test_df["Position"] == 1
    ]
    mywidget.arcos_widget.run_binarization_only.click()
    assert len(viewer.layers) == 2
    assert viewer.layers[0].name == ARCOS_LAYERS["all_cells"]
    assert viewer.layers[1].name == ARCOS_LAYERS["active_cells"]
    starting_pointsize = mywidget.layer_prop_widget.point_size.value()
    assert viewer.layers[0].size.flatten()[0] == starting_pointsize
    mywidget.layer_prop_widget.point_size.setValue(20)
    new_pointsize = mywidget.layer_prop_widget.point_size.value()
    assert viewer.layers[0].size.flatten()[0] == new_pointsize


# needs some more here for overall functionallity
