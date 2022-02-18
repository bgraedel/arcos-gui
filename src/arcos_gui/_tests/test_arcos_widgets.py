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
def dock_arcos_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    mywidget = viewer.window.add_plugin_dock_widget(
        plugin_name="arcos-gui", widget_name="ARCOS Main Widget"
    )
    return viewer, mywidget[1]


def test_add_timestamp_no_layers(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    mywidget = add_timestamp()
    viewer.window.add_dock_widget(mywidget)
    mywidget()
    catptured = capsys.readouterr()
    assert catptured.out == "INFO: No Layers to add Timestamp to\n"


def test_add_timestamp(make_napari_viewer):
    viewer = make_napari_viewer()
    viewer.add_image(
        data.binary_blobs(length=10, blob_size_fraction=0.2, n_dim=3), name="Image"
    )
    mywidget = add_timestamp()
    viewer.window.add_dock_widget(mywidget)
    mywidget()
    mywidget()  # removes first timestamp and re adds new
    assert viewer.layers["Timestamp"]


def test_export_data_widget_csv_no_data(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    mywidget = export_data()
    viewer.window.add_dock_widget(mywidget)
    show_output_csv_folder()
    output_csv_folder()
    catptured = capsys.readouterr()
    assert catptured.out == "INFO: No data to export, run arcos first\n"


def test_export_data_widget_csv_data(make_napari_viewer, tmp_path, data_frame):
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


def test_export_data_widget_images_no_data(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    mywidget = export_data()
    viewer.window.add_dock_widget(mywidget)
    show_output_movie_folder()
    output_movie_folder()
    catptured = capsys.readouterr()
    assert catptured.out == "INFO: No data to export, run arcos first\n"


def test_export_data_widget_images_data(make_napari_viewer, tmp_path):
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


def test_arcos_widget_choose_file(dock_arcos_widget):
    viewer, mywidget = dock_arcos_widget
    mywidget.filename.value = Path("src/arcos_gui/_tests/fixtures/arcos_test.csv")
    test_data = stored_variables.data
    direct_test_data = pd.read_csv("src/arcos_gui/_tests/fixtures/arcos_test.csv")
    # manually trigger button press
    columnpicker.Ok.changed.__call__()
    assert columnpicker.frame.value == "track_id"
    assert columnpicker.track_id.value == "track_id"
    assert columnpicker.x_coordinates.value == "track_id"
    assert columnpicker.y_coordinates.value == "track_id"
    assert columnpicker.measurment.value == "track_id"
    assert columnpicker.field_of_view_id.value == "track_id"
    assert_frame_equal(test_data, direct_test_data)


def test_filter_no_data(dock_arcos_widget, capsys):
    viewer, mywidget = dock_arcos_widget
    stored_variables.data = pd.DataFrame()
    mywidget.filter_input_data.changed.__call__()
    catptured = capsys.readouterr()
    assert catptured.out == "INFO: No data loaded, or not loaded correctly\n"


def test_filterwidget_data(dock_arcos_widget, capsys):
    # set choices needed for test
    columnpicker.dicCols.value = {
        "frame": "Frame",
        "x_coordinates": "X",
        "y_coordinates": "Y",
        "track_id": "track_id",
        "measurment": "Measurment",
        "field_of_view_id": "Position",
    }
    df_1 = pd.read_csv("src/arcos_gui/_tests/fixtures/filter_test.csv")
    stored_variables.data = df_1
    df_1 = df_1[df_1["Position"] == 1]
    viewer, mywidget = dock_arcos_widget
    mywidget.position.set_choice("1", 1)
    mywidget.position.value = 1
    mywidget.filter_input_data.changed.__call__()
    df = stored_variables.dataframe
    # capture output
    catptured = capsys.readouterr()
    # assert output
    assert catptured.out == "INFO: Data Filtered!\n"
    assert_frame_equal(df, df_1)


def test_arcos_widget_no_data(dock_arcos_widget, capsys):
    stored_variables.dataframe = pd.DataFrame()
    viewer, mywidget = dock_arcos_widget
    mywidget()
    # capture output
    catptured = capsys.readouterr()
    # assert output
    assert (
        catptured.out
        == "INFO: No Data Loaded, Use arcos_widget to load and filter data first\n"
    )


def test_arcos_widget_data_active_cells(dock_arcos_widget, capsys):
    columnpicker.dicCols.value = {
        "frame": "t",
        "x_coordinates": "x",
        "y_coordinates": "y",
        "track_id": "id",
        "measurment": "m",
        "field_of_view_id": "Position",
    }
    stored_variables.dataframe = pd.read_csv(
        "src/arcos_gui/_tests/fixtures/arcos_data.csv"
    )
    viewer, mywidget = dock_arcos_widget
    stored_variables.positions = [0, 1]
    stored_variables.current_position = 0
    mywidget()
    # capture output
    catptured = capsys.readouterr()
    # assert output
    assert (
        catptured.out
        == "INFO: No collective events detected, consider adjusting parameters\n"
    )
    assert viewer.layers["all_cells"]
    assert viewer.layers["active cells"]


def test_arcos_widget_data_all(dock_arcos_widget, capsys):
    columnpicker.dicCols.value = {
        "frame": "t",
        "x_coordinates": "x",
        "y_coordinates": "y",
        "track_id": "id",
        "measurment": "m",
        "field_of_view_id": "Position",
    }
    stored_variables.dataframe = pd.read_csv(
        "src/arcos_gui/_tests/fixtures/arcos_data.csv"
    )
    viewer, mywidget = dock_arcos_widget
    stored_variables.positions = [0, 1]
    stored_variables.current_position = 0
    mywidget.total_event_size.value = 10
    mywidget()
    assert viewer.layers["all_cells"]
    assert viewer.layers["active cells"]
    assert viewer.layers["coll cells"]
    assert viewer.layers["coll events"]


def test_toggle_biasmethod_visibility_lm(dock_arcos_widget):
    viewer, mywidget = dock_arcos_widget
    mywidget.bias_method.value = "lm"
    mywidget.bias_method.value = "none"
    mywidget.bias_method.value = "runmed"


def test_collev_plot_widget(dock_arcos_widget):
    # dock arcos
    viewer, mywidget = dock_arcos_widget
    # dock collev plot
    num_dw = len(viewer.window._dock_widgets)

    viewer.window.add_plugin_dock_widget(
        plugin_name="arcos-gui", widget_name="Collective Events Plot"
    )

    columnpicker.dicCols.value = {
        "frame": "t",
        "x_coordinates": "x",
        "y_coordinates": "y",
        "track_id": "id",
        "measurment": "m",
        "field_of_view_id": "Position",
    }
    stored_variables.dataframe = pd.read_csv(
        "src/arcos_gui/_tests/fixtures/arcos_data.csv"
    )

    stored_variables.positions = [0, 1]
    stored_variables.current_position = 0
    mywidget.total_event_size.value = 10
    mywidget()
    assert len(viewer.window._dock_widgets) == num_dw + 1


def test_TimeSeriesPlots_widget(dock_arcos_widget):
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
        "src/arcos_gui/_tests/fixtures/arcos_data.csv"
    )

    stored_variables.positions = [0, 1]
    stored_variables.current_position = 0
    mywidget.total_event_size.value = 10
    mywidget()
    plot.update_plot()
    plot.combo_box.setCurrentText("tracklength histogram")
    plot.update_plot()
    plot.combo_box.setCurrentText("measurment density plot")
    plot.update_plot()
    plot.combo_box.setCurrentText("x/t-plot")
    plot.update_plot()
    plot.combo_box.setCurrentText("y/t-plot")

    assert len(viewer.window._dock_widgets) == num_dw + 1
