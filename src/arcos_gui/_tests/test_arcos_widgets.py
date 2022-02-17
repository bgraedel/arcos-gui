from os import path, sep
from pathlib import Path

import pandas as pd
import pytest
from arcos_gui._arcos_widgets import (
    add_timestamp,
    arcos_widget,
    columnpicker,
    export_data,
    filepicker,
    filter_widget,
    output_csv_folder,
    output_movie_folder,
    show_output_csv_folder,
    show_output_movie_folder,
    stored_variables,
)
from pandas.testing import assert_frame_equal
from skimage import data


@pytest.fixture
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


def test_add_timestamp(make_napari_viewer):
    viewer = make_napari_viewer(strict_qt=True)
    viewer.add_image(
        data.binary_blobs(length=10, blob_size_fraction=0.2, n_dim=3), name="Image"
    )
    mywidget = add_timestamp()
    viewer.window.add_dock_widget(mywidget)
    mywidget()
    assert viewer.layers["Timestamp"]


def test_export_data_widget_csv_no_data(make_napari_viewer, capsys):
    viewer = make_napari_viewer(strict_qt=True)
    mywidget = export_data()
    viewer.window.add_dock_widget(mywidget)
    show_output_csv_folder()
    output_csv_folder()
    catptured = capsys.readouterr()
    assert catptured.out == "INFO: No data to export, run arcos first\n"


def test_export_data_widget_csv_data(make_napari_viewer, tmp_path, data_frame):
    arcos_dir = str(tmp_path)
    viewer = make_napari_viewer(strict_qt=True)
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
    viewer = make_napari_viewer(strict_qt=True)
    mywidget = export_data()
    viewer.window.add_dock_widget(mywidget)
    show_output_movie_folder()
    output_movie_folder()
    catptured = capsys.readouterr()
    assert catptured.out == "INFO: No data to export, run arcos first\n"


def test_export_data_widget_images_data(make_napari_viewer, tmp_path):
    viewer = make_napari_viewer(strict_qt=True)
    viewer.add_image(data.binary_blobs(length=1, blob_size_fraction=0.2, n_dim=3))
    arcos_dir = str(tmp_path)
    mywidget = export_data()
    viewer.window.add_dock_widget(mywidget)
    show_output_movie_folder()
    output_movie_folder.filename.value = arcos_dir
    output_movie_folder()
    file = arcos_dir + sep + "arcos_000.png"
    assert path.isfile(file)


def test_filepicker(make_napari_viewer):
    viewer = make_napari_viewer(strict_qt=True)
    mywidget = filepicker()
    viewer.window.add_dock_widget(mywidget)
    mywidget.filename.value = Path("src/arcos_gui/_tests/fixtures/arcos_test.csv")
    mywidget()
    test_data = stored_variables.data
    direct_test_data = pd.read_csv("src/arcos_gui/_tests/fixtures/arcos_test.csv")
    columnpicker.close()
    assert columnpicker.frame.value == "track_id"
    assert columnpicker.track_id.value == "track_id"
    assert columnpicker.x_coordinates.value == "track_id"
    assert columnpicker.y_coordinates.value == "track_id"
    assert columnpicker.measurment.value == "track_id"
    assert columnpicker.field_of_view_id.value == "track_id"
    assert_frame_equal(test_data, direct_test_data)


def test_filterwidget_no_data(make_napari_viewer, capsys):
    stored_variables.data = pd.DataFrame()
    viewer = make_napari_viewer(strict_qt=True)
    mywidget = filter_widget()
    viewer.window.add_dock_widget(mywidget)
    mywidget()
    catptured = capsys.readouterr()
    assert catptured.out == "INFO: No Data Loaded, Use filepicker to open data first\n"


def test_filterwidget_data(make_napari_viewer, capsys):
    viewer = make_napari_viewer(strict_qt=True)
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
    mywidget = filter_widget()
    viewer.window.add_dock_widget(mywidget)
    mywidget.position.set_choice("1", 1)
    mywidget.position.value = 1
    mywidget()
    df = stored_variables.dataframe
    # capture output
    catptured = capsys.readouterr()
    # assert output
    assert catptured.out == "INFO: Data Filtered!\n"
    assert_frame_equal(df, df_1)


def test_arcos_widget_no_data(make_napari_viewer, capsys):
    stored_variables.dataframe = pd.DataFrame()
    viewer = make_napari_viewer(strict_qt=True)
    mywidget = arcos_widget()
    viewer.window.add_dock_widget(mywidget)
    mywidget()
    # capture output
    catptured = capsys.readouterr()
    # assert output
    assert catptured.out == "INFO: No Data Loaded, Use filepicker to load data first\n"


def test_arcos_widget_data_active_cells(make_napari_viewer, capsys):
    stored_variables.dataframe = pd.read_csv(
        "src/arcos_gui/_tests/fixtures/arcos_test.csv"
    )
    viewer = make_napari_viewer(strict_qt=True)
    mywidget = arcos_widget()
    viewer.window.add_dock_widget(mywidget)
    mywidget()
    # capture output
    catptured = capsys.readouterr()
    # assert output
    assert (
        catptured.out
        == "INFO: No collective events detected, consider adjusting parameters\n"
    )
    assert viewer.layers["all_cells", "active cells"]


def test_arcos_widget_data_all(make_napari_viewer, capsys):
    stored_variables.dataframe = pd.read_csv(
        "src/arcos_gui/_tests/fixtures/arcos_data.csv"
    )
    viewer = make_napari_viewer(strict_qt=True)
    mywidget = arcos_widget()
    # set paramete5rs
    viewer.window.add_dock_widget(mywidget)
    mywidget.bin_peak_threshold.value = 0.015
    mywidget.bin_threshold.value = 0.015
    mywidget.min_clustersize.value = 1
    mywidget.min_duration.value = 1
    mywidget.total_event_size.value = 3
    mywidget()
    # # capture output
    # catptured = capsys.readouterr()
    # assert output
    assert viewer.layers["all_cells", "active cells", "coll cells", "coll events"]
