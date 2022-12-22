from __future__ import annotations

import pandas as pd
from arcos4py import ARCOS
from arcos_gui.processing import DataStorage
from arcos_gui.processing._arcos_wrapper import (
    arcos_wrapper,
    binarization,
    calculate_arcos_stats,
    detect_events,
    filtering_arcos_events,
    init_arcos_object,
)

# some tests that just validate that arcos4py in fact creates arcos objects and outputs data
# since this package relies on arcos4py for its main data processing the tests there are relevant and
# should be sufficient and are not repeated here
# maybe at a later point specific tests for the arcos functionallity should be added


def test_init_arcos_object():
    df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    arcos_object = init_arcos_object(df, ["x", "y"], "m", "t", "id")
    assert isinstance(arcos_object, ARCOS)


def test_binarization():
    df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    arcos_object = init_arcos_object(df, ["x", "y"], "m", "t", "id")
    arcos_object = binarization(
        arcos_object, True, False, 0.01, 0.99, 1, 3, 0.5, 0.5, 1, "none"
    )
    assert isinstance(arcos_object, ARCOS)
    assert not arcos_object.data.empty
    for i in arcos_object.data["m.bin"].unique():
        assert i in [0, 1]
    assert arcos_object.data["m.resc"].min() == 0
    assert arcos_object.data["m.resc"].max() == 1


def test_detect_events():
    df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    arcos_object = init_arcos_object(df, ["x", "y"], "m", "t", "id")
    arcos_object = binarization(
        arcos_object, True, False, 0.01, 0.99, 1, 3, 0.5, 0.5, 1, "none"
    )
    arcos_events = detect_events(
        arcos=arcos_object, neighbourhood_size=20, min_clustersize=4, nPrev_value=1
    )
    assert isinstance(arcos_events, pd.DataFrame)
    assert not arcos_events.empty


def test_filtering_arcos_events_high_values():
    df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    arcos_object = init_arcos_object(df, ["x", "y"], "m", "t", "id")
    arcos_object = binarization(
        arcos_object, True, False, 0.01, 0.99, 1, 3, 0.5, 0.5, 1, "none"
    )
    arcos_events = detect_events(
        arcos=arcos_object, neighbourhood_size=20, min_clustersize=4, nPrev_value=1
    )
    arcos_filtered = filtering_arcos_events(
        detected_events_df=arcos_events,
        frame_col_name="t",
        collid_name="collid",
        track_id_col_name="id",
        min_dur=1,
        total_event_size=1,
    )
    assert isinstance(arcos_filtered, pd.DataFrame)
    assert not arcos_filtered.empty
    pd.testing.assert_frame_equal(arcos_events, arcos_filtered, check_dtype=False)


def test_filtering_arcos_events_low_values():
    df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    arcos_object = init_arcos_object(df, ["x", "y"], "m", "t", "id")
    arcos_object = binarization(
        arcos_object, True, False, 0.01, 0.99, 1, 3, 0.5, 0.5, 1, "none"
    )
    arcos_events = detect_events(
        arcos=arcos_object, neighbourhood_size=20, min_clustersize=4, nPrev_value=1
    )
    arcos_filtered = filtering_arcos_events(
        detected_events_df=arcos_events,
        frame_col_name="t",
        collid_name="collid",
        track_id_col_name="id",
        min_dur=20,
        total_event_size=1,
    )
    assert isinstance(arcos_filtered, pd.DataFrame)
    assert arcos_filtered.empty


def test_calculate_arcos_stats():
    df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    arcos_object = init_arcos_object(df, ["x", "y"], "m", "t", "id")
    arcos_object = binarization(
        arcos_object, True, False, 0.01, 0.99, 1, 3, 0.5, 0.5, 1, "none"
    )
    arcos_events = detect_events(
        arcos=arcos_object, neighbourhood_size=20, min_clustersize=4, nPrev_value=1
    )
    arcos_filtered = filtering_arcos_events(
        detected_events_df=arcos_events,
        frame_col_name="t",
        collid_name="collid",
        track_id_col_name="id",
        min_dur=1,
        total_event_size=1,
    )
    arcos_stats = calculate_arcos_stats(
        df_arcos_filtered=arcos_filtered,
        frame_col="t",
        collid_name="collid",
        object_id_name="id",
        posCols=["x", "y"],
    )
    assert isinstance(arcos_stats, pd.DataFrame)
    assert not arcos_stats.empty
    assert arcos_stats["collid"].nunique() == 1


def test_arcos_wrapper_run_all():
    what_to_run = {"binarization", "filtering", "tracking"}
    ds = DataStorage()
    ds.filtered_data.value = pd.read_csv(
        "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )
    ds.columns.frame_column = "t"
    ds.columns.object_id = "id"
    ds.columns.x_column = "x"
    ds.columns.y_column = "y"
    ds.columns.z_column = "None"
    ds.columns.measurement_column = "m"
    ds.columns.position_id = "None"
    ds.columns.additional_filter_column = "None"
    ds.columns.measurement_math_operatoin = "None"
    ds.columns.measurement_bin = "m.bin"
    ds.columns.measurement_resc = "m.resc"
    assert not ds.filtered_data.value.empty
    assert ds.arcos_binarization.value.empty
    assert ds.arcos_output.value.empty
    assert ds.arcos_stats.value.empty
    arcos_wrapper(ds, what_to_run, print).run_arcos(
        interpolate_meas=True,
        clip_meas=False,
        clip_low=0.01,
        clip_high=0.99,
        bias_method="none",
        smooth_k=1,
        bias_k=3,
        polyDeg=1,
        bin_threshold=0.5,
        bin_peak_threshold=0.5,
        neighbourhood_size=20,
        min_clustersize=4,
        nprev=1,
        min_dur=1,
        total_event_size=1,
    )
    assert not ds.arcos_binarization.value.empty
    assert not ds.arcos_output.value.empty
    assert not ds.arcos_stats.value.empty


def test_arcos_wrapper_run_no_data(capsys):
    what_to_run = {"binarization", "filtering", "tracking"}
    ds = DataStorage()
    ds.columns.frame_column = "t"
    ds.columns.object_id = "id"
    ds.columns.x_column = "x"
    ds.columns.y_column = "y"
    ds.columns.z_column = "None"
    ds.columns.measurement_column = "m"
    ds.columns.position_id = "None"
    ds.columns.additional_filter_column = "None"
    ds.columns.measurement_math_operatoin = "None"
    ds.columns.measurement_bin = "m.bin"
    ds.columns.measurement_resc = "m.resc"
    arcos_wrapper(ds, what_to_run, print).run_arcos(
        interpolate_meas=True,
        clip_meas=False,
        clip_low=0.01,
        clip_high=0.99,
        bias_method="none",
        smooth_k=1,
        bias_k=3,
        polyDeg=1,
        bin_threshold=0.5,
        bin_peak_threshold=0.5,
        neighbourhood_size=20,
        min_clustersize=4,
        nprev=1,
        min_dur=1,
        total_event_size=1,
    )
    captured_data = capsys.readouterr()
    assert ds.filtered_data.value.empty
    assert ds.arcos_binarization.value.empty
    assert ds.arcos_output.value.empty
    assert ds.arcos_stats.value.empty
    assert "No data loaded. Load first using the import data tab." in captured_data.out


def test_arcos_wrapper_run_no_bin_data(capsys):
    what_to_run = {"binarization", "filtering", "tracking"}
    ds = DataStorage()
    ds.filtered_data.value = pd.read_csv(
        "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )

    ds.columns.frame_column = "t"
    ds.columns.object_id = "id"
    ds.columns.x_column = "x"
    ds.columns.y_column = "y"
    ds.columns.z_column = "None"
    ds.columns.measurement_column = "m"
    ds.columns.position_id = "None"
    ds.columns.additional_filter_column = "None"
    ds.columns.measurement_math_operatoin = "None"
    ds.columns.measurement_bin = "m.bin"
    ds.columns.measurement_resc = "m.resc"
    arcos_wrapper(ds, what_to_run, print).run_arcos(
        interpolate_meas=True,
        clip_meas=False,
        clip_low=0.01,
        clip_high=0.99,
        bias_method="none",
        smooth_k=1,
        bias_k=3,
        polyDeg=1,
        bin_threshold=10,
        bin_peak_threshold=10,
        neighbourhood_size=20,
        min_clustersize=4,
        nprev=1,
        min_dur=1,
        total_event_size=1,
    )
    captured_data = capsys.readouterr()
    assert not ds.filtered_data.value.empty
    assert not ds.arcos_binarization.value.empty
    assert ds.arcos_output.value.empty
    assert ds.arcos_stats.value.empty
    assert "No Binarized Data. Adjust Binazation Parameters." in captured_data.out


def test_arcos_wrapper_run_no_detected_events_data(capsys):
    what_to_run = {"binarization", "filtering", "tracking"}
    ds = DataStorage()
    ds.filtered_data.value = pd.read_csv(
        "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )

    ds.columns.frame_column = "t"
    ds.columns.object_id = "id"
    ds.columns.x_column = "x"
    ds.columns.y_column = "y"
    ds.columns.z_column = "None"
    ds.columns.measurement_column = "m"
    ds.columns.position_id = "None"
    ds.columns.additional_filter_column = "None"
    ds.columns.measurement_math_operatoin = "None"
    ds.columns.measurement_bin = "m.bin"
    ds.columns.measurement_resc = "m.resc"
    arcos_wrapper(ds, what_to_run, print).run_arcos(
        interpolate_meas=True,
        clip_meas=False,
        clip_low=0.01,
        clip_high=0.99,
        bias_method="none",
        smooth_k=1,
        bias_k=3,
        polyDeg=1,
        bin_threshold=0.5,
        bin_peak_threshold=0.5,
        neighbourhood_size=0.001,
        min_clustersize=4,
        nprev=1,
        min_dur=50,
        total_event_size=1,
    )
    captured_data = capsys.readouterr()
    assert not ds.filtered_data.value.empty
    assert not ds.arcos_binarization.value.empty
    assert ds.arcos_output.value.empty
    assert ds.arcos_stats.value.empty
    assert (
        "No Collective Events detected. Adjust Event Detection Parameters."
        in captured_data.out
    )


def test_arcos_wrapper_run_no_filtered_data(capsys):
    what_to_run = {"binarization", "filtering", "tracking"}
    ds = DataStorage()
    ds.filtered_data.value = pd.read_csv(
        "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )

    ds.columns.frame_column = "t"
    ds.columns.object_id = "id"
    ds.columns.x_column = "x"
    ds.columns.y_column = "y"
    ds.columns.z_column = "None"
    ds.columns.measurement_column = "m"
    ds.columns.position_id = "None"
    ds.columns.additional_filter_column = "None"
    ds.columns.measurement_math_operatoin = "None"
    ds.columns.measurement_bin = "m.bin"
    ds.columns.measurement_resc = "m.resc"
    arcos_wrapper(ds, what_to_run, print).run_arcos(
        interpolate_meas=True,
        clip_meas=False,
        clip_low=0.01,
        clip_high=0.99,
        bias_method="none",
        smooth_k=1,
        bias_k=3,
        polyDeg=1,
        bin_threshold=0.5,
        bin_peak_threshold=0.5,
        neighbourhood_size=20,
        min_clustersize=4,
        nprev=1,
        min_dur=50,
        total_event_size=1,
    )
    captured_data = capsys.readouterr()
    assert not ds.filtered_data.value.empty
    assert not ds.arcos_binarization.value.empty
    assert ds.arcos_output.value.empty
    assert ds.arcos_stats.value.empty
    assert (
        "No Collective Events detected.Adjust Filtering parameters."
        in captured_data.out
    )


def test_arcos_wrapper_run_specific_parts():
    what_to_run = {"binarization"}
    ds = DataStorage()
    ds.filtered_data.value = pd.read_csv(
        "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )

    ds.columns.frame_column = "t"
    ds.columns.object_id = "id"
    ds.columns.x_column = "x"
    ds.columns.y_column = "y"
    ds.columns.z_column = "None"
    ds.columns.measurement_column = "m"
    ds.columns.position_id = "None"
    ds.columns.additional_filter_column = "None"
    ds.columns.measurement_math_operatoin = "None"
    ds.columns.measurement_bin = "m.bin"
    ds.columns.measurement_resc = "m.resc"
    wrapper_class = arcos_wrapper(ds, what_to_run, print)
    wrapper_class.run_arcos(
        interpolate_meas=True,
        clip_meas=False,
        clip_low=0.01,
        clip_high=0.99,
        bias_method="none",
        smooth_k=1,
        bias_k=3,
        polyDeg=1,
        bin_threshold=0.5,
        bin_peak_threshold=0.5,
        neighbourhood_size=20,
        min_clustersize=4,
        nprev=1,
        min_dur=1,
        total_event_size=1,
    )
    assert not ds.filtered_data.value.empty
    assert not ds.arcos_binarization.value.empty
    assert wrapper_class.arcos_raw_output.empty
    assert ds.arcos_output.value.empty
    assert ds.arcos_stats.value.empty

    what_to_run.clear()
    what_to_run.add("tracking")
    wrapper_class.run_arcos(
        interpolate_meas=True,
        clip_meas=False,
        clip_low=0.01,
        clip_high=0.99,
        bias_method="none",
        smooth_k=1,
        bias_k=3,
        polyDeg=1,
        bin_threshold=0.5,
        bin_peak_threshold=0.5,
        neighbourhood_size=20,
        min_clustersize=4,
        nprev=1,
        min_dur=1,
        total_event_size=1,
    )

    assert not wrapper_class.arcos_raw_output.empty
    assert ds.arcos_output.value.empty
    assert ds.arcos_stats.value.empty

    what_to_run.clear()
    what_to_run.add("filtering")
    wrapper_class.run_arcos(
        interpolate_meas=True,
        clip_meas=False,
        clip_low=0.01,
        clip_high=0.99,
        bias_method="none",
        smooth_k=1,
        bias_k=3,
        polyDeg=1,
        bin_threshold=0.5,
        bin_peak_threshold=0.5,
        neighbourhood_size=20,
        min_clustersize=4,
        nprev=1,
        min_dur=1,
        total_event_size=1,
    )

    assert not ds.filtered_data.value.empty
    assert not ds.arcos_binarization.value.empty
    assert not ds.arcos_output.value.empty
    assert not ds.arcos_stats.value.empty
