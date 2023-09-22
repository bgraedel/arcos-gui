from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
import pytest
from arcos_gui.processing import columnnames
from arcos_gui.processing._preprocessing_utils import (
    DataFrameMatcher,
    DataLoader,
    calculate_measurement,
    check_for_collid_column,
    filter_data,
    get_delimiter,
    get_tracklengths,
    match_dataframes,
    preprocess_data,
    process_input,
    read_data_header,
    subtract_timeoffset,
)
from arcos_gui.tools import OPERATOR_DICTIONARY
from arcos_gui.widgets import columnpicker
from qtpy.QtCore import QEventLoop, Qt

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


@pytest.fixture
def test_df():
    df = pd.DataFrame(
        {
            "track_id": [1, 1, 1, 2, 2, 2, 3, 3, 3],
            "x": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "y": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "time": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "m": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "m2": [2, 2, 2, 2, 2, 2, 2, 2, 2],
            "pos": [1, 1, 1, 1, 2, 2, 2, 3, 3],
            "well": [1, 2, 1, 2, 1, 2, 1, 2, 1],
        }
    )
    return df


@pytest.fixture
def process_input_fixture():
    df = pd.read_csv("src/arcos_gui/_tests/test_data/filter_test.csv")
    my_input = process_input(
        df=df,
        field_of_view_column="Position",
        frame_column="frame",
        pos_columns=["X", "Y"],
        track_id_column="track_id",
        measurement_column="Measurment",
    )
    return my_input


def test_subtract_timeoffset(test_df):
    """Test subtract_timeoffset."""
    # create dataframe
    df = test_df
    # subtract timeoffset
    df = subtract_timeoffset(df, "time")
    # check if timeoffset is subtracted
    assert df["time"].to_list() == [0, 1, 2, 3, 4, 5, 6, 7, 8]


def test_calculate_measurement_none(test_df):
    """Test calculate_measurement."""
    # create dataframe
    df = test_df
    # calculate measurement
    meas_name, df = calculate_measurement(df, "None", "m", "None", OPERATOR_DICTIONARY)
    # check if measurement is calculated
    assert df[meas_name].to_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_calculate_measurement_add(test_df):
    """Test calculate_measurement."""
    # create dataframe
    df = test_df
    # calculate measurement
    meas_name, df = calculate_measurement(df, "Add", "m", "m2", OPERATOR_DICTIONARY)
    # check if measurement is calculated
    assert df[meas_name].to_list() == [3, 4, 5, 6, 7, 8, 9, 10, 11]


def test_calculate_measurement_subtract(test_df):
    """Test calculate_measurement."""
    # create dataframe
    df = test_df
    # calculate measurement
    meas_name, df = calculate_measurement(
        df, "Subtract", "m", "m2", OPERATOR_DICTIONARY
    )
    # check if measurement is calculated
    assert df[meas_name].to_list() == [-1, 0, 1, 2, 3, 4, 5, 6, 7]


def test_calculate_measurement_multiply(test_df):
    """Test calculate_measurement."""
    # create dataframe
    df = test_df
    # calculate measurement
    meas_name, df = calculate_measurement(
        df, "Multiply", "m", "m2", OPERATOR_DICTIONARY
    )
    # check if measurement is calculated
    assert df[meas_name].to_list() == [2, 4, 6, 8, 10, 12, 14, 16, 18]


def test_calculate_measurement_divide(test_df):
    """Test calculate_measurement."""
    # create dataframe
    df = test_df
    # calculate measurement
    meas_name, df = calculate_measurement(df, "Divide", "m", "m2", OPERATOR_DICTIONARY)
    # check if measurement is calculated
    assert df[meas_name].to_list() == [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5]


def test_get_tracklengths(test_df):
    """Test get_tracklengths."""
    # create dataframe
    df = test_df
    # get tracklengths
    tracklengths = get_tracklengths(df, None, "track_id", None)
    # check if tracklengths are calculated
    assert tracklengths == (3, 3)


def test_tracklengths_with_pos(test_df):
    """Test get_tracklengths."""
    # create dataframe
    df = test_df
    # get tracklengths
    tracklengths = get_tracklengths(df, "pos", "track_id", None)
    # check if tracklengths are calculated
    assert tracklengths == (1, 3)


def test_filter_data(test_df):
    """Test filter_data."""
    # create dataframe
    df = test_df
    df_val = pd.DataFrame(
        {
            "track_id": [1, 1, 1, 2],
            "x": [1, 2, 3, 4],
            "y": [1, 2, 3, 4],
            "time": [0, 1, 2, 3],
            "m": [1, 2, 3, 4],
            "m2": [2, 2, 2, 2],
            "pos": [1, 1, 1, 1],
            "well": [1, 2, 1, 2],
        }
    )
    # filter data
    df_filtered, max_meas, min_meas = filter_data(
        df_in=df,
        field_of_view_id_name="pos",
        frame_name="time",
        track_id_name="track_id",
        measurement_name="m",
        additional_filter_column_name=None,
        posCols=["x", "y"],
        fov_val=1,
        additional_filter_value=None,
        min_tracklength_value=1,
        max_tracklength_value=5,
        frame_interval=1,
        st_out=print,
    )
    pd.testing.assert_frame_equal(df_filtered, df_val, check_dtype=False)
    assert max_meas == 4
    assert min_meas == 1


def test_filter_data_with_additional_filter(test_df):
    """Test filter_data."""
    # create dataframe
    df = test_df
    df_val = pd.DataFrame(
        {
            "track_id": [1, 1],
            "x": [1, 3],
            "y": [1, 3],
            "time": [0, 2],
            "m": [1, 3],
            "m2": [2, 2],
            "pos": [1, 1],
            "well": [1, 1],
        }
    )
    # filter data
    df_filtered, max_meas, min_meas = filter_data(
        df_in=df,
        field_of_view_id_name="pos",
        frame_name="time",
        track_id_name="track_id",
        measurement_name="m",
        additional_filter_column_name="well",
        posCols=["x", "y"],
        fov_val=1,
        additional_filter_value=1,
        min_tracklength_value=1,
        max_tracklength_value=5,
        frame_interval=1,
        st_out=print,
    )
    pd.testing.assert_frame_equal(df_filtered, df_val, check_dtype=False)
    assert max_meas == 3
    assert min_meas == 1


def test_filter_data_with_min_tracklength(test_df):
    """Test filter_data."""
    # create dataframe
    df = test_df
    df_val = pd.DataFrame(
        {
            "track_id": [2],
            "x": [4],
            "y": [4],
            "time": [0],
            "m": [4],
            "m2": [2],
            "pos": [1],
            "well": [2],
        }
    )
    # filter data
    df_filtered, max_meas, min_meas = filter_data(
        df_in=df,
        field_of_view_id_name="pos",
        frame_name="time",
        track_id_name="track_id",
        measurement_name="m",
        additional_filter_column_name=None,
        posCols=["x", "y"],
        fov_val=1,
        additional_filter_value=None,
        min_tracklength_value=0,
        max_tracklength_value=1,
        frame_interval=1,
        st_out=print,
    )
    pd.testing.assert_frame_equal(df_filtered, df_val, check_dtype=False)
    assert max_meas == 4
    assert min_meas == 4


def test_check_for_collid_column():
    """Test check_for_collid_column."""
    # create dataframe
    df = pd.DataFrame(
        {
            "track_id": [1, 1, 1, 2],
            "x": [1, 2, 3, 4],
            "y": [1, 2, 3, 4],
            "time": [0, 1, 2, 3],
            "m": [1, 2, 3, 4],
            "m2": [2, 2, 2, 2],
            "pos": [1, 1, 1, 1],
            "well": [1, 2, 1, 2],
            "collid": [0, 0, 0, 0],
        }
    )
    # check for collid column
    df = check_for_collid_column(df, "collid", "old")
    # check if collid column is added
    assert "collid_old" in df.columns


def test_preprocess_data_func(test_df):
    df = test_df
    col_names = columnnames(
        measurement_column_1="m",
        measurement_column_2="m2",
        measurement_math_operation="Multiply",
    )
    meas_name, df = preprocess_data(df, col_names)
    assert df[meas_name].to_list() == [2, 4, 6, 8, 10, 12, 14, 16, 18]


def test_preprocess_data_func_err(test_df):
    df = pd.DataFrame(
        {
            "track_id": [1, 1, 1, 2, 2, 2, 3, 3, 3],
            "x": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "y": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "time": [1, 2, 3, 4, 5, 6, 7, 8, 9],
            "m": ["hello", "this", "is", "a", "string", "and", "not", "a", "number"],
            "m2": ["hello", "this", "is", "also", "a", "string", "yes", "yes", "yes"],
            "pos": [1, 1, 1, 1, 2, 2, 2, 3, 3],
            "well": [1, 2, 1, 2, 1, 2, 1, 2, 1],
        }
    )
    with pytest.raises(TypeError):
        meas_name, df = preprocess_data(df, "Multiply", "m", "m2", OPERATOR_DICTIONARY)


def test_get_delimiter_comma():
    delimiter = get_delimiter("src/arcos_gui/_tests/test_data/comma_separated.csv")
    assert delimiter == ","


def test_get_delimiter_comma_gz():
    delimiter = get_delimiter("src/arcos_gui/_tests/test_data/comma_separated.csv.gz")
    assert delimiter == ","


def test_get_delimiter_semicolon():
    delimiter = get_delimiter("src/arcos_gui/_tests/test_data/semicolon_separated.csv")
    assert delimiter == ";"


def test_get_delimiter_tab():
    delimiter = get_delimiter("src/arcos_gui/_tests/test_data/tab_separated.csv")
    assert delimiter == "\t"


def test_get_header_gz():
    df = pd.read_csv("src/arcos_gui/_tests/test_data/comma_separated.csv.gz")
    cols = df.columns
    test, delimiter = read_data_header(
        "src/arcos_gui/_tests/test_data/comma_separated.csv.gz"
    )
    assert sorted(cols) == sorted(test)


def test_get_header():
    df = pd.read_csv("src/arcos_gui/_tests/test_data/comma_separated.csv")
    cols = df.columns
    test, delimiter = read_data_header(
        "src/arcos_gui/_tests/test_data/comma_separated.csv"
    )
    assert sorted(cols) == sorted(test)


def test_filter_input(process_input_fixture: process_input):
    out = process_input_fixture.filter_position(2, True).reset_index(drop=True)
    data = [["2_1", 239.842, 161.539, 0, 0.861779, 2]]
    cols = [
        "track_id",
        "X",
        "Y",
        "Frame",
        "Measurment",
        "Position",
    ]
    test_df = pd.DataFrame(data=data, columns=cols)
    pd.testing.assert_frame_equal(out, test_df, check_index_type=False)


def test_filter_tracklength(process_input_fixture: process_input):
    out = process_input_fixture.filter_tracklength(
        1, 1, return_dataframe=True
    ).reset_index(drop=True)
    data = [["2_1", 239.842, 161.539, 0, 0.861779, 2]]
    cols = [
        "track_id",
        "X",
        "Y",
        "Frame",
        "Measurment",
        "Position",
    ]
    test_df = pd.DataFrame(data=data, columns=cols)
    pd.testing.assert_frame_equal(out, test_df)


def test_rescale_measurment(process_input_fixture: process_input):
    process_input_fixture.filter_position(2, True)
    out = process_input_fixture.rescale_measurment(
        10, return_dataframe=True
    ).reset_index(drop=True)
    data = [["2_1", 239.842, 161.539, 0, 8.61779, 2]]
    cols = [
        "track_id",
        "X",
        "Y",
        "Frame",
        "Measurment",
        "Position",
    ]
    test_df = pd.DataFrame(data=data, columns=cols)
    pd.testing.assert_frame_equal(out, test_df)


def test_data_loader_thread(qtbot):
    loop = QEventLoop()
    data_loader = DataLoader(
        "src/arcos_gui/_tests/test_data/comma_separated.csv.gz", ","
    )

    def assert_data(df):
        assert isinstance(df, pd.DataFrame)

    data_loader.finished.connect(loop.quit)

    # connect the assert function to the data signal
    data_loader.new_data.connect(assert_data)
    # start the thread and the event loop
    data_loader.start()
    loop.exec_()


def test_data_loader_thread_wait_columpicker(qtbot: QtBot):
    def assert_data(df):
        assert isinstance(df, pd.DataFrame)

    def set_loading_worker_columns(self):
        data_loader.wait_for_columnpicker = False

    # create event loop so the test function does not end
    # before the thread can finish
    loop = QEventLoop()
    # now with option True to make sure that the data loader waits for the colosing of columnpicker
    data_loader = DataLoader(
        "src/arcos_gui/_tests/test_data/comma_separated.csv.gz", ",", True
    )
    picker_widget = columnpicker()
    qtbot.addWidget(picker_widget)

    # set columnnames for the columnpicker
    picker_widget.set_column_names(["m"])

    # connect callback to set wait_for_picker to False
    # Quite important otherwise the test will not end
    picker_widget.ok_button.clicked.connect(set_loading_worker_columns)

    data_loader.finished.connect(loop.quit)

    data_loader.new_data.connect(assert_data)

    # start the thread and the event loop
    data_loader.start()

    # set the columnpicker to the correct values needed for the test
    picker_widget.measurement_math.setCurrentText("None")
    picker_widget.measurement.setCurrentText("m")
    picker_widget.second_measurement.setCurrentText("None")
    qtbot.mouseClick(picker_widget.ok_button, Qt.LeftButton)

    loop.exec_()


def test_match_dataframes():
    # Sample data
    df1 = pd.DataFrame(
        {"frame": [1, 2, 3], "centroid-0": [1, 2, 3], "centroid-1": [1, 2, 3]}
    )
    df2 = pd.DataFrame(
        {
            "frame": [1, 2, 3],
            "centroid-0": [1, 2, 3],
            "centroid-1": [1, 2, 3],
            "track_id": [10, 11, 12],
        }
    )

    # Test direct merge
    result = match_dataframes(df1, df2)
    assert len(result) == 3
    assert "track_id" in result.columns

    # Test mismatched data
    df1["centroid-0"] = [10, 20, 30]
    with pytest.raises(ValueError):
        match_dataframes(df1, df2)


def test_dataframe_matcher():
    df1 = pd.DataFrame(
        {"frame": [1, 2, 3], "centroid-0": [1, 2, 3], "centroid-1": [1, 2, 3]}
    )
    df2 = pd.DataFrame(
        {
            "frame": [1, 2, 3],
            "centroid-0": [1, 2, 3],
            "centroid-1": [1, 2, 3],
            "track_id": [10, 11, 12],
        }
    )

    matcher = DataFrameMatcher(df1, df2)

    result_df = None

    def on_matched(df):
        nonlocal result_df
        result_df = df

    error = None

    def on_aborted(e):
        nonlocal error
        error = e

    matcher.matched.connect(on_matched)
    matcher.aborted.connect(on_aborted)
    matcher.run()

    assert error is None
    assert len(result_df) == 3
    assert "track_id" in result_df.columns

    # Test mismatched data
    df1["centroid-0"] = [10, 20, 30]
    matcher = DataFrameMatcher(df1, df2)
    matcher.matched.connect(on_matched)
    matcher.aborted.connect(on_aborted)
    matcher.run()
    assert isinstance(error, ValueError)
