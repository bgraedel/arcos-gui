import pandas as pd
import pytest
from arcos_gui.data_module import get_delimiter, process_input, read_data_header
from pandas.testing import assert_frame_equal


@pytest.fixture
def fixture_columns():
    columns = {
        "frame": "Frame",
        "x_coordinates": "X",
        "y_coordinates": "Y",
        "track_id": "track_id",
        "measurment": "Measurment",
        "field_of_view_id": "Position",
    }
    return columns


@pytest.fixture
def import_data(fixture_columns):
    my_input = process_input(
        csv_file="src/arcos_gui/_tests/test_data/filter_test.csv",
        frame_column="frame",
        pos_columns=["X", "Y"],
        track_id_column="track_id",
        measurement_column="Measurment",
        field_of_view_column="Position",
    )
    my_input.read_csv()
    return my_input


def is_unique(s):
    a = s.to_numpy()
    return (a[0] == a).all()


def test_filter_input(import_data):
    out = import_data.filter_position(2, True).reset_index(drop=True)
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
    assert_frame_equal(out, test_df, check_index_type=False)


def test_filter_tracklength(import_data):
    out = import_data.filter_tracklength(1, 1, return_dataframe=True).reset_index(
        drop=True
    )
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
    assert_frame_equal(out, test_df)


def test_rescale_measurment(import_data):
    import_data.filter_position(2, True)
    out = import_data.rescale_measurment(10, return_dataframe=True).reset_index(
        drop=True
    )
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
    assert_frame_equal(out, test_df)


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
