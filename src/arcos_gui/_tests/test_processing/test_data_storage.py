from __future__ import annotations

import pandas as pd
import pytest
from arcos_gui.processing._data_storage import (
    DataStorage,
    arcos_parameters,
    columnnames,
    data_frame_storage,
    timestamp_parameters,
    value_callback,
)
from napari.utils.colormaps import AVAILABLE_COLORMAPS


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


def test_columnames_defaults():
    columnnames_instance = columnnames()
    assert columnnames_instance.object_id == "track_id"
    assert columnnames_instance.y_column == "y"
    assert columnnames_instance.x_column == "x"
    assert columnnames_instance.frame_column == "frame"
    assert columnnames_instance.measurement_column_1 == "measurement"
    assert columnnames_instance.measurement_column_2 == "measurement_2"
    assert columnnames_instance.position_id == "position_id"
    assert columnnames_instance.additional_filter_column == "additional_filter"
    assert columnnames_instance.measurement_math_operatoin == "None"
    assert columnnames_instance.measurement_bin is None
    assert columnnames_instance.measurement_resc is None
    assert columnnames_instance.collid_name == "collid"
    assert columnnames_instance.measurement_column == "measurement"


def test_columnames_setters():
    columnnames_instance = columnnames()
    columnnames_instance.object_id = "track_id_new"
    columnnames_instance.y_column = "y_new"
    columnnames_instance.x_column = "x_new"
    columnnames_instance.frame_column = "time_new"
    columnnames_instance.measurement_column_1 = "m_new"
    columnnames_instance.measurement_column_2 = "m2_new"
    columnnames_instance.position_id = "position_id_new"
    columnnames_instance.additional_filter_column = "additional_filter_new"
    columnnames_instance.measurement_math_operatoin = "None_new"
    columnnames_instance.measurement_bin = "not None"
    columnnames_instance.measurement_resc = "not None"
    columnnames_instance.collid_name = "collid_new"
    columnnames_instance.measurement_column = "measurement_new"

    assert columnnames_instance.object_id == "track_id_new"
    assert columnnames_instance.y_column == "y_new"
    assert columnnames_instance.x_column == "x_new"
    assert columnnames_instance.frame_column == "time_new"
    assert columnnames_instance.measurement_column_1 == "m_new"
    assert columnnames_instance.measurement_column_2 == "m2_new"
    assert columnnames_instance.position_id == "position_id_new"
    assert columnnames_instance.additional_filter_column == "additional_filter_new"
    assert columnnames_instance.measurement_math_operatoin == "None_new"
    assert columnnames_instance.measurement_bin == "not None"
    assert columnnames_instance.measurement_resc == "not None"
    assert columnnames_instance.collid_name == "collid_new"
    assert columnnames_instance.measurement_column == "measurement_new"


def test_columnames_properties():
    columnnames_instance = columnnames()
    pickable_values = columnnames_instance.pickablepickable_columns_names
    assert pickable_values == [
        "frame",
        "track_id",
        "x",
        "y",
        "z",
        "measurement",
        "measurement_2",
        "position_id",
        "additional_filter",
        "None",
    ]


def test_columnames_properties_2():
    columnnames_instance = columnnames()
    posCol = columnnames_instance.posCol
    assert posCol == ["x", "y", "z"]
    columnnames_instance.z_column = "None"
    posCol = columnnames_instance.posCol
    assert posCol == ["x", "y"]


def test_columnames_properties_3():
    columnnames_instance = columnnames()
    posCol = columnnames_instance.vcolscore
    assert posCol == ["frame", "y", "x", "z"]
    columnnames_instance.z_column = "None"
    posCol = columnnames_instance.vcolscore
    assert posCol == ["frame", "y", "x"]


def test_columnames_properties_4():
    df = pd.DataFrame(
        columns=["Column", "value"],
        data=[
            ["frame_column", "frame"],
            ["position_id", "position_id"],
            ["object_id", "track_id"],
            ["x_column", "x"],
            ["y_column", "y"],
            ["z_column", "z"],
            ["measurement_column_1", "measurement"],
            ["measurement_column_2", "measurement_2"],
            ["additional_filter_column", "additional_filter"],
            ["measurement_math_operatoin", "None"],
            ["measurement_bin", None],
            ["measurement_resc", None],
            ["collid_name", "collid"],
            ["measurement_column", "measurement"],
        ],
    )

    columnnames_instance = columnnames()
    df_test = columnnames_instance.as_dataframe
    pd.testing.assert_frame_equal(df, df_test)


def test_arcos_parameters_default_values():
    params = arcos_parameters()

    assert params.interpolate_meas == False  # noqa E712
    assert params.clip_meas == False  # noqa E712
    assert params.clip_low == 0.0
    assert params.clip_high == 0.0
    assert params.smooth_k == 0
    assert params.bias_k == 0
    assert params.bias_method == "none"
    assert params.polyDeg == 0
    assert params.bin_threshold == 0.0
    assert params.bin_peak_threshold == 0.0
    assert params.neighbourhood_size == 0.0
    assert params.min_clustersize == 0.0
    assert params.nprev_spinbox == 0
    assert params.min_dur == 0
    assert params.total_event_size == 0


def test_arcos_parameters_callback(mocker, capsys):
    params = arcos_parameters()

    test_func = mocker.Mock()
    params_stuff = [
        params.interpolate_meas,
        params.clip_meas,
        params.clip_low,
        params.clip_high,
        params.smooth_k,
        params.bias_k,
        params.bias_method,
        params.polyDeg,
        params.bin_threshold,
        params.bin_peak_threshold,
        params.eps_method,
        params.neighbourhood_size,
        params.epsPrev,
        params.min_clustersize,
        params.nprev_spinbox,
        params.min_dur,
        params.total_event_size,
        params.add_convex_hull,
    ]
    for i in params_stuff:
        i.value_changed_connect(test_func)

    params.interpolate_meas.value = True
    params.clip_meas.value = True
    params.clip_low.value = 1.0
    params.clip_high.value = 1.0
    params.smooth_k.value = 1
    params.bias_k.value = 1
    params.bias_method.value = "none"
    params.polyDeg.value = 1
    params.bin_threshold.value = 1.0
    params.bin_peak_threshold.value = 1.0
    params.eps_method.value = "none"
    params.neighbourhood_size.value = 1.0
    params.epsPrev.value = 1.0
    params.min_clustersize.value = 1.0
    params.nprev_spinbox.value = 1
    params.min_dur.value = 1
    params.total_event_size.value = 1
    params.add_convex_hull.value = True

    assert test_func.call_count == 18

    for i in params_stuff:
        i.unregister_callback(test_func)

    params.interpolate_meas.value = True
    params.clip_meas.value = True
    params.clip_low.value = 1.0
    params.clip_high.value = 1.0
    params.smooth_k.value = 1
    params.bias_k.value = 1
    params.bias_method.value = "none"
    params.polyDeg.value = 1
    params.bin_threshold.value = 1.0
    params.bin_peak_threshold.value = 1.0
    params.eps_method.value = "none"
    params.neighbourhood_size.value = 1.0
    params.epsPrev.value = 1.0
    params.min_clustersize.value = 1.0
    params.nprev_spinbox.value = 1
    params.min_dur.value = 1
    params.total_event_size.value = 1
    params.add_convex_hull.value = True

    assert test_func.call_count == 18


def test_arcos_parameters_as_dataframe():
    params = arcos_parameters()

    df = params.as_dataframe
    expected_df = pd.DataFrame(
        columns=["parameter", "value"],
        data=[
            ["interpolate_meas", "False"],
            ["clip_meas", "False"],
            ["clip_low", "0.0"],
            ["clip_high", "0.0"],
            ["smooth_k", "0"],
            ["bias_k", "0"],
            ["bias_method", "none"],
            ["polyDeg", "0"],
            ["bin_threshold", "0.0"],
            ["bin_peak_threshold", "0.0"],
            ["eps_method", "manual"],
            ["neighbourhood_size", "0.0"],
            ["epsPrev", "0.0"],
            ["min_clustersize", "0"],
            ["nprev_spinbox", "0"],
            ["min_dur", "0"],
            ["total_event_size", "0"],
        ],
    ).astype(str)

    pd.testing.assert_frame_equal(df, expected_df)


def test_arcos_parameters_with_custom_values():
    params = arcos_parameters()
    params.interpolate_meas.value = True
    params.clip_meas.value = True
    params.clip_low.value = 1.0
    params.clip_high.value = 2.0
    params.smooth_k.value = 3
    params.bias_k.value = 4
    params.bias_method.value = "Method"
    params.polyDeg.value = 5
    params.bin_threshold.value = 6.0
    params.bin_peak_threshold.value = 7.0
    params.neighbourhood_size.value = 8.0
    params.min_clustersize.value = 9.0
    params.nprev_spinbox.value = 10
    params.min_dur.value = 11
    params.total_event_size.value = 12

    assert params.interpolate_meas == True  # noqa E712
    assert params.clip_meas == True  # noqa E712
    assert params.clip_low == 1.0
    assert params.clip_high == 2.0
    assert params.smooth_k == 3
    assert params.bias_k == 4
    assert params.bias_method == "Method"
    assert params.polyDeg == 5
    assert params.bin_threshold == 6.0
    assert params.bin_peak_threshold == 7.0
    assert params.neighbourhood_size == 8.0
    assert params.min_clustersize == 9.0
    assert params.nprev_spinbox == 10
    assert params.min_dur == 11
    assert params.total_event_size == 12


def test_timestamp_parameters_default_values():
    params = timestamp_parameters()

    assert params.start_time == 0
    assert params.step_time == 1
    assert params.prefix == "t"
    assert params.suffix == ""
    assert params.position == "upper_left"
    assert params.size == 1
    assert params.x_shift == 0
    assert params.y_shift == 0


def test_timestamp_parameters_as_dataframe():
    params = timestamp_parameters()

    df = params.as_dataframe

    assert df.shape == (7, 2)
    assert df.columns.tolist() == ["parameter", "value"]
    assert df["parameter"].tolist() == [
        "start_time",
        "step_time",
        "prefix",
        "suffix",
        "size",
        "x_shift",
        "y_shift",
    ]
    assert df["value"].tolist() == [0, 1, "t", "", 1, 0, 0]


def test_timestamp_parameters_with_custom_values():
    params = timestamp_parameters(
        start_time=1,
        step_time=2,
        prefix="prefix",
        suffix="suffix",
        position="upper_right",
        size=2,
        x_shift=3,
        y_shift=4,
    )

    assert params.start_time == 1
    assert params.step_time == 2
    assert params.prefix == "prefix"
    assert params.suffix == "suffix"
    assert params.position == "upper_right"
    assert params.size == 2
    assert params.x_shift == 3
    assert params.y_shift == 4


def test_data_frame_storage_callback(mocker):
    # create a mock function to use as the callback
    mock_callback = mocker.Mock()

    # create an instance of the data_frame_storage class
    df_storage = data_frame_storage()

    # register the mock callback function
    df_storage.value_changed_connect(mock_callback)

    # set the value of the data_frame_storage instance
    df_storage.value = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})

    # assert that the mock callback function was called
    mock_callback.assert_called_once()


def test_value_callback_callback(mocker):
    # create a mock function to use as the callback
    mock_callback = mocker.Mock()

    # create an instance of the value_callback class
    value_cb = value_callback(10)

    # register the mock callback function
    value_cb.value_changed_connect(mock_callback)

    # set the value of the value_callback instance
    value_cb.value = 20

    # assert that the mock callback function was called
    mock_callback.assert_called_once()


def test_data_frame_storage_init():
    # test that the default value of the _value field is an empty dataframe
    df_storage = data_frame_storage()
    assert df_storage.value.empty

    # test that the default value of the _callbacks field is an empty list
    assert df_storage._callbacks == []


def test_data_frame_storage_value_setter():
    df_storage = data_frame_storage()
    df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})

    # test that setting the value of the data_frame_storage instance updates the _value field
    df_storage.value = df
    assert df_storage.value.equals(df)


def test_data_frame_storage_unregister_callback(mocker):
    # create a mock function to use as the callback
    mock_callback = mocker.Mock()

    # create an instance of the data_frame_storage class
    df_storage = data_frame_storage()

    # register the mock callback function
    df_storage.value_changed_connect(mock_callback)

    # unregister the callback function
    df_storage.unregister_callback(mock_callback)

    # set the value of the data_frame_storage instance
    df_storage.value = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})

    # assert that the mock callback function was not called
    mock_callback.assert_not_called()


def test_value_callback_init():
    # test that the default value of the _callbacks field is an empty list
    value_cb = value_callback(10)
    assert value_cb._callbacks == []


def test_value_callback_value_setter():
    value_cb = value_callback(10)

    # test that setting the value of the value_callback instance updates the _value field
    value_cb.value = 20
    assert value_cb.value == 20


def test_value_callback_unregister_callback(mocker):
    # create a mock function to use as the callback
    mock_callback = mocker.Mock()

    # create an instance of the value_callback class
    value_cb = value_callback(10)

    # register the mock callback function
    value_cb.value_changed_connect(mock_callback)

    # unregister the callback function
    value_cb.unregister_callback(mock_callback)

    # set the value of the value_callback instance
    value_cb.value = 20

    # assert that the mock callback function was not called
    mock_callback.assert_not_called()


def test_data_storage_init():
    data_storage = DataStorage()
    # test that the _original_data field is initialized correctly
    assert isinstance(data_storage._original_data, data_frame_storage)
    assert data_storage._original_data.value.empty

    # test that the _filtered_data field is initialized correctly
    assert isinstance(data_storage._filtered_data, data_frame_storage)
    assert data_storage._filtered_data.value.empty

    # test that the _arcos_binarization field is initialized correctly
    assert isinstance(data_storage._arcos_binarization, data_frame_storage)
    assert data_storage._arcos_binarization.value.empty

    # test that the _arcos_output field is initialized correctly
    assert isinstance(data_storage._arcos_output, data_frame_storage)
    assert data_storage._arcos_output.value.empty

    # test that the _arcos_stats field is initialized correctly
    assert isinstance(data_storage._arcos_stats, data_frame_storage)
    assert data_storage._arcos_stats.value.empty

    # test that the _columns field is initialized correctly
    assert isinstance(data_storage._columns, columnnames)

    # test that the _arcos_parameters field is initialized correctly
    assert isinstance(data_storage._arcos_parameters, arcos_parameters)

    # test that the min_max_meas field is initialized correctly
    assert data_storage.min_max_meas == (0, 0.5)

    # test that the colormaps field is initialized correctly
    assert data_storage.colormaps == list(AVAILABLE_COLORMAPS)

    # test that the point_size field is initialized correctly
    assert data_storage.point_size == 10

    # test that the _selected_object_id field is initialized correctly
    assert isinstance(data_storage._selected_object_id, value_callback)
    assert data_storage._selected_object_id.value is None

    # test that the lut field is initialized correctly
    assert data_storage.lut == "inferno"

    # test that the _filename_for_sample_data field is initialized correctly
    assert isinstance(data_storage._file_name, value_callback)
    assert data_storage._file_name.value is None

    # test that the _timestamp_parameters field is initialized correctly
    assert isinstance(data_storage._timestamp_parameters, value_callback)
    assert isinstance(data_storage._timestamp_parameters.value, timestamp_parameters)

    # test that the verbous field is initialized correctly
    assert data_storage.verbous is False


def test_data_storage_callbacks(mocker):
    data_storage = DataStorage()
    # create mock functions to use as callbacks for the data_frame_storage and value_callback instances
    mock_df_callback = mocker.Mock()
    mock_value_callback = mocker.Mock()

    # register the mock callbacks
    data_storage._original_data.value_changed_connect(mock_df_callback)
    data_storage._filtered_data.value_changed_connect(mock_df_callback)
    data_storage._arcos_binarization.value_changed_connect(mock_df_callback)
    data_storage._arcos_output.value_changed_connect(mock_df_callback)
    data_storage._arcos_stats.value_changed_connect(mock_df_callback)
    data_storage._selected_object_id.value_changed_connect(mock_value_callback)
    data_storage._file_name.value_changed_connect(mock_value_callback)
    data_storage._timestamp_parameters.value_changed_connect(mock_value_callback)

    # set the values of the data_frame_storage and value_callback instances
    data_storage._original_data.value = pd.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    )
    data_storage._filtered_data.value = pd.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    )
    data_storage._arcos_binarization.value = pd.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    )
    data_storage._arcos_output.value = pd.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    )
    data_storage._arcos_stats.value = pd.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    )
    data_storage._selected_object_id.value = 10
    data_storage._file_name.value = "test_filename"
    data_storage._timestamp_parameters.value = timestamp_parameters()

    # assert that the mock callbacks were called the correct number of times
    assert mock_df_callback.call_count == 5
    assert mock_value_callback.call_count == 3


def test_data_storage_reset_all_attributes_callback(mocker):
    data_storage = DataStorage()
    # create mock functions to use as callbacks for the data_frame_storage and value_callback instances
    mock_df_callback = mocker.Mock()
    mock_value_callback = mocker.Mock()

    # register the mock callbacks
    data_storage._original_data.value_changed_connect(mock_df_callback)
    data_storage._filtered_data.value_changed_connect(mock_df_callback)
    data_storage._arcos_binarization.value_changed_connect(mock_df_callback)
    data_storage._arcos_output.value_changed_connect(mock_df_callback)
    data_storage._arcos_stats.value_changed_connect(mock_df_callback)
    data_storage._selected_object_id.value_changed_connect(mock_value_callback)
    data_storage._file_name.value_changed_connect(mock_value_callback)
    data_storage._timestamp_parameters.value_changed_connect(mock_value_callback)

    # reset all attributes with trigger_callback set to True
    data_storage.reset_all_attributes(trigger_callback=True)

    # assert that the mock callbacks were called the correct number of times
    assert mock_df_callback.call_count == 5
    assert mock_value_callback.call_count == 3


def test_data_storage_reset_all_attributes_no_callback(mocker):
    data_storage = DataStorage()
    # create mock functions to use as callbacks for the data_frame_storage and value_callback instances
    mock_df_callback = mocker.Mock()
    mock_value_callback = mocker.Mock()

    # register the mock callbacks
    data_storage._original_data.value_changed_connect(mock_df_callback)
    data_storage._filtered_data.value_changed_connect(mock_df_callback)
    data_storage._arcos_binarization.value_changed_connect(mock_df_callback)
    data_storage._arcos_output.value_changed_connect(mock_df_callback)
    data_storage._arcos_stats.value_changed_connect(mock_df_callback)
    data_storage._selected_object_id.value_changed_connect(mock_value_callback)
    data_storage._file_name.value_changed_connect(mock_value_callback)
    data_storage._timestamp_parameters.value_changed_connect(mock_value_callback)

    # reset all attributes with trigger_callback set to False
    data_storage.reset_all_attributes(trigger_callback=False)

    # assert that the mock callbacks were not called
    mock_df_callback.assert_not_called()
    mock_value_callback.assert_not_called()


def test_reset_all_attributes_method():
    data_storage = DataStorage()
    # set the values of the data_frame_storage and value_callback instances
    data_storage._original_data.value = pd.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    )
    data_storage._filtered_data.value = pd.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    )
    data_storage._arcos_binarization.value = pd.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    )
    data_storage._arcos_output.value = pd.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    )
    data_storage._arcos_stats.value = pd.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    )
    data_storage._columns = columnnames(frame_column="time")
    data_storage._arcos_parameters.interpolate_meas.value = True
    data_storage.min_max_meas = (0, 1)
    data_storage.colormaps = ["viridis", "plasma", "inferno", "magma", "cividis"]
    data_storage.point_size = 12
    data_storage._selected_object_id.value = 10
    data_storage.lut = "viridis"
    data_storage._file_name.value = "test_filename"
    data_storage.timestamp_parameters.value = timestamp_parameters(start_time=50)

    assert not data_storage == DataStorage()
    # reset all attributes
    data_storage.reset_all_attributes()

    # assert that the values of the data_frame_storage and value_callback instances are None
    assert data_storage == DataStorage()


def test_reset_relevant_attributes():
    data_storage = DataStorage()
    # set the values of the data_frame_storage and value_callback instances
    data_storage._filtered_data.value = pd.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    )
    data_storage._arcos_binarization.value = pd.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    )
    data_storage._arcos_output.value = pd.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    )
    data_storage._arcos_stats.value = pd.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    )
    data_storage._selected_object_id.value = 10
    data_storage.lut = "viridis"  # not reset in reset_relevant_attributes

    assert not data_storage == DataStorage()
    # reset all attributes
    data_storage.reset_relevant_attributes()

    # assert that the values of the data_frame_storage and value_callback instances are None
    assert data_storage != DataStorage()  # not equal since lut is not reset

    data_storage.lut = "inferno"  # reset lut to what default value since it is not reset in reset_relevant_attributes

    assert data_storage == DataStorage()  # now equal since lut is reset


def test_data_storage_make_verbose(mocker, capsys):
    data_storage = DataStorage()
    # create mock functions to use as callbacks for the data_frame_storage and value_callback instances
    mock_df_callback = mocker.Mock()
    mock_value_callback = mocker.Mock()

    # register the mock callbacks
    data_storage._original_data.value_changed_connect(mock_df_callback)
    data_storage._timestamp_parameters.value_changed_connect(mock_value_callback)

    # make the data storage verbose
    data_storage.make_verbose()

    # set the values of the data_frame_storage and value_callback instances
    data_storage._original_data.value = pd.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    )
    data_storage._timestamp_parameters.value = timestamp_parameters(start_time=50)

    # assert that the mock callbacks were called the correct number of times
    assert mock_df_callback.call_count == 1
    assert mock_value_callback.call_count == 1

    # assert that the values of the data_frame_storage and value_callback instances are printed
    captured = capsys.readouterr()
    assert (
        f"value_calback: value changed, executing {mock_value_callback}" in captured.out
    )
    assert (
        f"data_frame_storage: value changed executing {mock_df_callback}"
        in captured.out
    )


def test_data_storage_make_quiet(mocker, capsys):
    data_storage = DataStorage()
    # create mock functions to use as callbacks for the data_frame_storage and value_callback instances
    mock_df_callback = mocker.Mock()
    mock_value_callback = mocker.Mock()

    # register the mock callbacks
    data_storage._original_data.value_changed_connect(mock_df_callback)
    data_storage._timestamp_parameters.value_changed_connect(mock_value_callback)

    # make the data storage verbose and the quiet again to test make_quiet
    data_storage.make_verbose()
    data_storage.make_quiet()

    # set the values of the data_frame_storage and value_callback instances
    data_storage._original_data.value = pd.DataFrame(
        {"col1": [1, 2, 3], "col2": [4, 5, 6]}
    )
    data_storage._timestamp_parameters.value = timestamp_parameters(start_time=50)

    # assert that the mock callbacks were called the correct number of times
    assert mock_df_callback.call_count == 1
    assert mock_value_callback.call_count == 1

    # assert that the values of the data_frame_storage and value_callback instances are printed
    captured = capsys.readouterr()
    assert (
        f"value_calback: value changed, executing {mock_value_callback}"
        not in captured.out
    )
    assert (
        f"data_frame_storage: value changed executing {mock_df_callback}"
        not in captured.out
    )


def test_setter_errors():
    data_storage = DataStorage()
    with pytest.raises(ValueError):
        data_storage.columns = 1
    with pytest.raises(ValueError):
        data_storage.arcos_parameters = 1
    with pytest.raises(ValueError):
        data_storage.timestamp_parameters = 1


def test_setter_no_errors():
    data_storage = DataStorage()
    data_storage.columns = columnnames(frame_column="time")
    assert data_storage.columns == columnnames(frame_column="time")
    data_storage.arcos_parameters = arcos_parameters()
    assert data_storage.arcos_parameters == arcos_parameters()
    data_storage.timestamp_parameters = timestamp_parameters(start_time=50)
    assert data_storage.timestamp_parameters.value == timestamp_parameters(
        start_time=50
    )


def test_load_data_data_storage(mocker):
    data_storage = DataStorage()
    # create mock functions to use as callbacks for the data_frame_storage and value_callback instances
    mock_df_callback = mocker.Mock()

    # register the mock callbacks
    data_storage.original_data.value_changed_connect(mock_df_callback)

    # load the data no trigger callback
    data_storage.load_data(
        "src/arcos_gui/_tests/test_data/arcos_data.csv", trigger_callback=False
    )

    # assert that the mock callbacks were called the correct number of times
    assert data_storage.original_data.value.empty is False
    assert mock_df_callback.call_count == 0

    # load the data and trigger callback
    data_storage.load_data(
        "src/arcos_gui/_tests/test_data/arcos_data.csv", trigger_callback=True
    )

    # assert that the mock callbacks were called the correct number of times
    assert data_storage.original_data.value.empty is False
    assert mock_df_callback.call_count == 1
