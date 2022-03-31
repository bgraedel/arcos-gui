import gc
from os import path, sep
from pathlib import Path

import pandas as pd
import pytest
from arcos_gui._arcos_widgets import (
    add_timestamp,
    columnpicker,
    export_data,
    output_csv_folder,
    output_movie_folder,
    show_output_csv_folder,
    show_output_movie_folder,
    stored_variables,
)
from pandas.testing import assert_frame_equal
from qtpy.QtCore import Qt
from qtpy.QtTest import QTest
from skimage import data


@pytest.fixture(scope="module")
def data_frame():
    col_2 = list(range(5, 10))
    col_2.extend(list(range(10, 5, -1)))
    d = {
        "time": [1 for i in range(0, 10)],
        "X": list(range(0, 10)),
        "Y": col_2,
        "collid": [1 for i in range(0, 10)],
    }
    df = pd.DataFrame(data=d)

    return df


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
def set_columnpicker():
    def method(col_names: list):
        columnpicker.frame.choices = col_names
        columnpicker.x_coordinates.choices = col_names
        columnpicker.y_coordinates.choices = col_names
        columnpicker.z_coordinates.choices = col_names
        columnpicker.track_id.choices = col_names
        columnpicker.measurment.choices = col_names
        columnpicker.field_of_view_id.choices = col_names
        columnpicker.field_of_view_id.set_choice("None", "None")
        columnpicker.z_coordinates.set_choice("None", "None")

        columnpicker.frame.set_value = col_names[0]
        columnpicker.x_coordinates.value = col_names[1]
        columnpicker.y_coordinates.value = col_names[2]
        columnpicker.z_coordinates.value = col_names[3]
        columnpicker.track_id.value = col_names[4]
        columnpicker.measurment.value = col_names[5]
        columnpicker.field_of_view_id.value = col_names[6]

    return method


def test_add_timestamp_no_layers(make_napari_viewer, capsys, qtbot):
    viewer = make_napari_viewer()
    mywidget = add_timestamp()
    viewer.window.add_dock_widget(mywidget)
    mywidget()
    catptured = capsys.readouterr()
    assert catptured.out == "INFO: No Layers to add Timestamp to\n"
    viewer.close()


def test_add_timestamp(make_napari_viewer, qtbot):
    viewer = make_napari_viewer()
    viewer.add_image(
        data.binary_blobs(length=10, blob_size_fraction=0.2, n_dim=3), name="Image"
    )
    mywidget = add_timestamp()
    viewer.window.add_dock_widget(mywidget)
    mywidget()
    mywidget()  # removes first timestamp and re adds new
    assert viewer.layers["Timestamp"]
    viewer.close()


def test_export_data_widget_csv_no_data(make_napari_viewer, capsys, qtbot):
    viewer = make_napari_viewer()
    mywidget = export_data()
    viewer.window.add_dock_widget(mywidget)
    show_output_csv_folder()
    output_csv_folder()
    catptured = capsys.readouterr()
    assert catptured.out == "INFO: No data to export, run arcos first\n"
    viewer.close()


def test_export_data_widget_csv_data(make_napari_viewer, tmp_path, data_frame, qtbot):
    arcos_dir = str(tmp_path)
    viewer = make_napari_viewer()
    mywidget = export_data()
    viewer.window.add_dock_widget(mywidget)
    show_output_csv_folder()
    output_csv_folder.filename.value = arcos_dir
    stored_variables.data_merged = data_frame
    output_csv_folder()
    file = arcos_dir + sep + "arcos_data.csv"
    df = pd.read_csv(file, index_col=0)
    assert_frame_equal(df, data_frame)
    viewer.close()


def test_export_data_widget_images_no_data(make_napari_viewer, capsys, qtbot):
    viewer = make_napari_viewer()
    mywidget = export_data()
    viewer.window.add_dock_widget(mywidget)
    show_output_movie_folder()
    output_movie_folder()
    catptured = capsys.readouterr()
    assert catptured.out == "INFO: No data to export, run arcos first\n"
    viewer.close()


def test_export_data_widget_images_data(make_napari_viewer, tmp_path, qtbot):
    viewer = make_napari_viewer()
    viewer.add_image(data.binary_blobs(length=1, blob_size_fraction=0.2, n_dim=3))
    arcos_dir = str(tmp_path)
    mywidget = export_data()
    viewer.window.add_dock_widget(mywidget)
    show_output_movie_folder()
    output_movie_folder.filename.value = arcos_dir
    output_movie_folder()
    file = arcos_dir + sep + "arcos_000.png"
    assert path.isfile(file)
    viewer.close()


def test_arcos_widget_choose_file(dock_arcos_widget, qtbot):
    viewer, mywidget = dock_arcos_widget
    stored_variables.filename_for_sample_data = str(
        Path("src/arcos_gui/_tests/test_data/arcos_data.csv")
    )
    test_data = stored_variables.data
    direct_test_data = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    direct_test_data["t"] -= 1
    # manually trigger button press
    QTest.mouseClick(columnpicker.Ok.native, Qt.LeftButton)
    assert columnpicker.frame.value == "t"
    assert columnpicker.track_id.value == "id"
    assert columnpicker.x_coordinates.value == "x"
    assert columnpicker.y_coordinates.value == "y"
    assert columnpicker.measurment.value == "m"
    assert columnpicker.field_of_view_id.value == "Position"
    assert_frame_equal(test_data, direct_test_data)
    viewer.close()


def test_filter_no_data(dock_arcos_widget, capsys, qtbot):
    viewer, mywidget = dock_arcos_widget
    stored_variables.data = pd.DataFrame()
    QTest.mouseClick(mywidget.filter_input_data, Qt.LeftButton)
    catptured = capsys.readouterr()
    assert catptured.out == "INFO: No data loaded, or not loaded correctly\n"
    viewer.close()


def test_filterwidget_data(dock_arcos_widget, capsys, qtbot, set_columnpicker):
    cols = ["Frame", "X", "Y", "None", "track_id", "Measurment", "Position"]
    # set choices needed for test
    set_columnpicker(cols)
    df_1 = pd.read_csv("src/arcos_gui/_tests/test_data/filter_test.csv")
    stored_variables.data = df_1
    df_1 = df_1[df_1["Position"] == 1]
    viewer, mywidget = dock_arcos_widget
    mywidget.position.addItem("1", 1)
    mywidget.position.setCurrentText("1")
    QTest.mouseClick(mywidget.filter_input_data, Qt.LeftButton)
    df = stored_variables.dataframe
    # capture output
    catptured = capsys.readouterr()
    # assert output
    assert catptured.out == "INFO: Data Filtered!\n"
    assert_frame_equal(df, df_1)
    viewer.close()


def test_arcos_widget_no_data(dock_arcos_widget, capsys, qtbot):
    stored_variables.dataframe = pd.DataFrame()
    viewer, mywidget = dock_arcos_widget
    QTest.mouseClick(mywidget.update_arcos, Qt.LeftButton)
    # capture output
    catptured = capsys.readouterr()
    # assert output
    assert (
        catptured.out
        == "INFO: No Data Loaded, Use arcos_widget to load and filter data first\n"
    )
    viewer.close()


def test_arcos_widget_data_active_cells(dock_arcos_widget, capsys, qtbot):
    columnpicker.frame.choices = "t"
    columnpicker.track_id.choices = "id"
    columnpicker.x_coordinates.choices = "x"
    columnpicker.y_coordinates.choices = "y"
    columnpicker.z_coordinates.choices = "None"
    columnpicker.measurment.choices = "m"
    columnpicker.field_of_view_id.choices = "Position"
    columnpicker.field_of_view_id.set_choice("None", "None")
    columnpicker.z_coordinates.set_choice("None", "None")

    columnpicker.frame.set_value = "t"
    columnpicker.x_coordinates.value = "x"
    columnpicker.y_coordinates.value = "y"
    columnpicker.track_id.value = "id"
    columnpicker.measurment.value = "m"
    columnpicker.field_of_view_id.value = "Position"

    stored_variables.dataframe = pd.read_csv(
        "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )
    viewer, mywidget = dock_arcos_widget
    stored_variables.positions = [0, 1]
    stored_variables.current_position = 0
    mywidget.total_event_size.setValue(50)
    mywidget.update_what_to_run_variable()
    QTest.mouseClick(mywidget.update_arcos, Qt.LeftButton)
    # capture output
    catptured = capsys.readouterr()
    # assert output
    assert (
        catptured.out
        == "INFO: No collective events detected, consider adjusting parameters\n"
    )
    assert viewer.layers["all_cells"]
    assert viewer.layers["active cells"]
    viewer.close()


def test_arcos_widget_data_all(dock_arcos_widget, capsys, qtbot):
    columnpicker.dicCols.value = {
        "frame": "t",
        "x_coordinates": "x",
        "y_coordinates": "y",
        "track_id": "id",
        "measurment": "m",
        "field_of_view_id": "Position",
    }
    stored_variables.dataframe = pd.read_csv(
        "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )
    viewer, mywidget = dock_arcos_widget
    stored_variables.positions = [0, 1]
    stored_variables.current_position = 0
    mywidget.total_event_size.setValue(5)
    mywidget.update_what_to_run_variable()
    QTest.mouseClick(mywidget.update_arcos, Qt.LeftButton)
    assert viewer.layers["all_cells"]
    assert viewer.layers["active cells"]
    assert viewer.layers["coll cells"]
    assert viewer.layers["coll events"]
    viewer.close()


def test_toggle_biasmethod_visibility(dock_arcos_widget, qtbot):
    viewer, mywidget = dock_arcos_widget
    mywidget.bias_method.setCurrentText("runmed")
    mywidget.bias_method.setCurrentText("lm")
    mywidget.bias_method.setCurrentText("none")
    viewer.close()


def test_collev_plot_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    num_dw = len(viewer.window._dock_widgets)
    viewer.window.add_plugin_dock_widget(
        plugin_name="arcos-gui", widget_name="Collective Events Plot"
    )
    assert len(viewer.window._dock_widgets) == num_dw + 1
    viewer.close()


def test_TimeSeriesPlots_widget(dock_arcos_widget, qtbot):
    # dock arcos
    viewer, mywidget = dock_arcos_widget
    num_dw = len(viewer.window._dock_widgets)
    # dock TimeSeriesPlots plot
    widget_info = viewer.window.add_plugin_dock_widget(
        plugin_name="arcos-gui", widget_name="Timeseries plots"
    )
    plot = widget_info[1]
    columnpicker.dicCols.value = {
        "frame": "t",
        "x_coordinates": "x",
        "y_coordinates": "y",
        "track_id": "id",
        "measurment": "m",
        "field_of_view_id": "Position",
    }
    stored_variables.dataframe = pd.read_csv(
        "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )

    stored_variables.positions = [0, 1]
    stored_variables.current_position = 0
    mywidget.total_event_size.setValue(5)
    mywidget.update_what_to_run_variable()
    QTest.mouseClick(mywidget.update_arcos, Qt.LeftButton)
    plot.update_plot()
    plot.combo_box.setCurrentText("tracklength histogram")
    plot.update_plot()
    plot.combo_box.setCurrentText("measurment density plot")
    plot.update_plot()
    plot.combo_box.setCurrentText("x/t-plot")
    plot.update_plot()
    plot.combo_box.setCurrentText("y/t-plot")

    assert len(viewer.window._dock_widgets) == num_dw + 1
    viewer.close()
