from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from arcos_gui import (
    filter_data,
    get_arcos_output,
    get_current_arcos_plugin,
    load_dataframe,
    load_dataframe_with_columnpicker,
    load_sample_data,
    open_plugin,
    run_arcos,
    run_binarization_only,
)
from arcos_gui._main_widget import MainWindow
from qtpy.QtCore import QEventLoop


def test_open_plugin(make_napari_viewer):
    viewer = make_napari_viewer()

    plugin = open_plugin(viewer)

    assert isinstance(plugin, MainWindow)


@pytest.mark.parametrize("sample_data", ["synthetic", "real"])
def test_load_sample_data_valid_data(sample_data, make_napari_viewer):
    viewer = make_napari_viewer()

    with patch(
        "arcos_gui._helper_functions.load_synthetic_dataset", MagicMock()
    ) as mock_synthetic, patch(
        "arcos_gui._helper_functions.load_real_dataset", MagicMock()
    ) as mock_real:
        load_sample_data(sample_data=sample_data, plugin=viewer)

        if sample_data == "synthetic":
            mock_synthetic.assert_called_once_with(plugin=viewer)
            mock_real.assert_not_called()
        else:
            mock_real.assert_called_once_with(plugin=viewer)
            mock_synthetic.assert_not_called()


def test_load_sample_data_invalid_data(make_napari_viewer):
    viewer = make_napari_viewer()

    with pytest.raises(ValueError):
        load_sample_data(sample_data="invalid", plugin=viewer)

    with pytest.raises(ValueError):
        load_sample_data(sample_data=None, plugin=viewer)


# Sample dataframe for testing
sample_df = pd.DataFrame(
    {
        "frame": [1, 2, 3],
        "x": [10, 20, 30],
        "y": [5, 15, 25],
        "measurement": [100, 200, 300],
    }
)


def test_load_dataframe(make_napari_viewer):
    viewer = make_napari_viewer()
    plugin = open_plugin(viewer)
    load_dataframe(
        df=sample_df,
        frame_column="frame",
        track_id_column=None,
        x_column="x",
        y_column="y",
        z_column=None,
        measurement_column="measurement",
        measurement_column_2=None,
        fov_column=None,
        additional_filter_column=None,
        measurement_math_operation=None,
        plugin=plugin,
    )
    assert plugin.data.original_data.value.empty is False


def test_load_dataframe_with_columnpicker(make_napari_viewer):
    viewer = make_napari_viewer()
    plugin = open_plugin(viewer)
    load_dataframe_with_columnpicker(df=sample_df, plugin=plugin)
    assert plugin._input_controller.picker.isVisibleTo(plugin)
    plugin._input_controller.picker.close()


def test_filter_data(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    plugin = open_plugin(viewer)
    plugin.data.columns.value.frame_column = "t"
    plugin.data.columns.value.x_column = "x"
    plugin.data.columns.value.y_column = "y"
    plugin.data.columns.value.z_column = None
    plugin.data.columns.value.measurement_column = "m"
    plugin.data.columns.value.object_id = "id"
    plugin.data.columns.value.position_id = "Position"
    plugin.data.columns.value.additional_filter_column = None
    plugin.data.columns.value.measurement_math_operation = None
    plugin.data.load_data("src/arcos_gui/_tests/test_data/arcos_data.csv")

    filter_data(track_length=(1, 3), fov_id=None, additional_filter=None, plugin=plugin)
    captured = capsys.readouterr()
    assert "Filtered" in captured.out


def test_run_binarization_only(make_napari_viewer):
    viewer = make_napari_viewer()
    plugin = open_plugin(viewer)
    plugin.data.columns.value.frame_column = "t"
    plugin.data.columns.value.x_column = "x"
    plugin.data.columns.value.y_column = "y"
    plugin.data.columns.value.z_column = None
    plugin.data.columns.value.measurement_column = "m"
    plugin.data.columns.value.object_id = "id"
    plugin.data.columns.value.position_id = "Position"
    plugin.data.columns.value.additional_filter_column = None
    plugin.data.columns.value.measurement_math_operation = None

    loop = QEventLoop()

    plugin.data.load_data("src/arcos_gui/_tests/test_data/arcos_data.csv")

    run_binarization_only(
        bias_method="none",
        smooth_k=5,
        bias_k=3,
        polyDeg=2,
        bin_peak_threshold=0.5,
        bin_threshold=0.5,
        plugin=plugin,
    )
    plugin._arcos_widget.worker.finished.connect(loop.quit)
    loop.exec_()

    assert len(viewer.layers) == 2


def test_run_arcos(make_napari_viewer):
    viewer = make_napari_viewer()
    plugin = open_plugin(viewer)
    plugin.data.columns.value.frame_column = "t"
    plugin.data.columns.value.x_column = "x"
    plugin.data.columns.value.y_column = "y"
    plugin.data.columns.value.z_column = None
    plugin.data.columns.value.measurement_column = "m"
    plugin.data.columns.value.object_id = "id"
    plugin.data.columns.value.position_id = "Position"
    plugin.data.columns.value.additional_filter_column = None
    plugin.data.columns.value.measurement_math_operation = None
    loop = QEventLoop()

    plugin.data.load_data("src/arcos_gui/_tests/test_data/arcos_data.csv")

    run_arcos(
        bias_method="none",
        smooth_k=5,
        bias_k=3,
        polyDeg=2,
        bin_peak_threshold=0.5,
        bin_threshold=0.5,
        eps=3,
        min_clustersize=1,
        plugin=plugin,
    )

    plugin._arcos_widget.worker.finished.connect(loop.quit)
    loop.exec_()

    assert len(viewer.layers) == 4


def test_get_arcos_output(make_napari_viewer):
    viewer = make_napari_viewer()
    plugin = open_plugin(viewer)
    # Mocking output and stats for the plugin. Replace with suitable mock data.
    mock_output = MagicMock(spec=pd.DataFrame)
    mock_stats = MagicMock(spec=pd.DataFrame)
    plugin.data.arcos_output.value = mock_output
    plugin.data.arcos_stats.value = mock_stats

    output, stats = get_arcos_output(plugin=plugin)
    assert output == mock_output
    assert stats == mock_stats


def test_get_current_arcos_plugin(make_napari_viewer):
    viewer = make_napari_viewer()
    plugin = open_plugin(viewer)
    retrieved_plugin = get_current_arcos_plugin()
    assert retrieved_plugin == plugin
