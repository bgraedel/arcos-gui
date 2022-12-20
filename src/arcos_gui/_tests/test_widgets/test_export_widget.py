from __future__ import annotations

import os
import tempfile
from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import patch

import pandas as pd
import pytest
from arcos_gui.processing import DataStorage
from arcos_gui.widgets import ExportWidget
from qtpy.QtCore import Qt
from skimage.data import brain

if TYPE_CHECKING:
    from napari import viewer
    from pytestqt.qtbot import QtBot


@pytest.fixture()
def make_input_widget(
    qtbot, make_napari_viewer
) -> tuple[ExportWidget, viewer.Viewer, QtBot]:
    ds = DataStorage()
    viewer = make_napari_viewer()
    widget = ExportWidget(viewer, ds)
    qtbot.addWidget(widget)
    return widget, viewer, qtbot


def test_open_widget(make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot]):
    input_data_widget, _, _ = make_input_widget
    assert input_data_widget


def test_get_current_date(make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot]):
    widget, _, _ = make_input_widget
    assert widget._get_current_date() == datetime.now().strftime("%Y%m%d")


def test_export_arcos_data(
    make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot]
):
    with tempfile.TemporaryDirectory() as tmpdir:
        widget, _, _ = make_input_widget

        # make a test dataframe with 3 columns
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
        file_path = tmpdir
        base_name = "test"
        current_date = datetime.now().strftime("%Y%m%d")
        output_name = f"{current_date}_{base_name}_arcos_output.csv"
        out_path = os.path.join(file_path, output_name)

        widget._data_storage_instance.arcos_output._value = df
        widget.file_LineEdit_data.setText(file_path)
        widget.base_name_LineEdit_data.setText(base_name)

        widget._export_arcos_data()

        assert os.path.exists(out_path)
        df_loaded = pd.read_csv(out_path)
        assert pd.testing.assert_frame_equal(df_loaded, df) is None


def test_export_arcos_data_button(
    make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot]
):
    with tempfile.TemporaryDirectory() as tmpdir:
        widget, _, qtbot = make_input_widget

        # make a test dataframe with 3 columns
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
        file_path = tmpdir
        base_name = "test"
        current_date = datetime.now().strftime("%Y%m%d")
        output_name = f"{current_date}_{base_name}_arcos_output.csv"
        out_path = os.path.join(file_path, output_name)

        widget._data_storage_instance.arcos_output._value = df
        widget.file_LineEdit_data.setText(file_path)
        widget.base_name_LineEdit_data.setText(base_name)

        qtbot.mouseClick(widget.data_export_button, Qt.LeftButton)

        assert os.path.exists(out_path)
        df_loaded = pd.read_csv(out_path)
        assert pd.testing.assert_frame_equal(df_loaded, df) is None


def test_export_arcos_data_button_no_data(
    make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot], capsys
):
    widget, _, qtbot = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = tmpdir
        base_name = "test"

        widget.file_LineEdit_data.setText(file_path)
        widget.base_name_LineEdit_data.setText(base_name)

        qtbot.mouseClick(widget.data_export_button, Qt.LeftButton)

        captured = capsys.readouterr()
        assert "No data to export" in captured.out


def test_export_arcos_stats(
    make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot]
):
    widget, _, _ = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        # make a test dataframe with 3 columns
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
        file_path = tmpdir
        base_name = "test"
        current_date = datetime.now().strftime("%Y%m%d")
        output_name = f"{current_date}_{base_name}_arcos_stats.csv"
        out_path = os.path.join(file_path, output_name)

        widget._data_storage_instance.arcos_stats._value = df
        widget.file_LineEdit_data.setText(file_path)
        widget.base_name_LineEdit_data.setText(base_name)

        widget._export_arcos_stats()

        assert os.path.exists(out_path)
        df_loaded = pd.read_csv(out_path)
        assert pd.testing.assert_frame_equal(df_loaded, df) is None


def test_export_arcos_stats_button(
    make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot]
):
    widget, _, qtbot = make_input_widget

    with tempfile.TemporaryDirectory() as tmpdir:
        # make a test dataframe with 3 columns
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
        file_path = tmpdir
        base_name = "test"
        current_date = datetime.now().strftime("%Y%m%d")
        output_name = f"{current_date}_{base_name}_arcos_stats.csv"
        out_path = os.path.join(file_path, output_name)

        widget._data_storage_instance.arcos_stats._value = df
        widget.file_LineEdit_data.setText(file_path)
        widget.base_name_LineEdit_data.setText(base_name)

        qtbot.mouseClick(widget.stats_export_button, Qt.LeftButton)

        assert os.path.exists(out_path)
        df_loaded = pd.read_csv(out_path)
        assert pd.testing.assert_frame_equal(df_loaded, df) is None


def test_export_arcos_stats_button_no_data(
    make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot], capsys
):
    widget, _, qtbot = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = tmpdir
        base_name = "test"

        widget.file_LineEdit_data.setText(file_path)
        widget.base_name_LineEdit_data.setText(base_name)

        qtbot.mouseClick(widget.stats_export_button, Qt.LeftButton)

        captured = capsys.readouterr()
        assert "No data to export" in captured.out


def test_export_arcos_params(
    make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot]
):
    widget, _, _ = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        # make a test dataframe with 3 columns
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
        file_path = tmpdir
        base_name = "test"
        current_date = datetime.now().strftime("%Y%m%d")
        output_name = f"{current_date}_{base_name}_arcos_params.csv"
        out_path = os.path.join(file_path, output_name)

        # has to be set otherwise parameters are not exported
        widget._data_storage_instance.arcos_output._value = df

        df_param = widget._data_storage_instance.arcos_parameters.as_dataframe
        widget.file_LineEdit_data.setText(file_path)
        widget.base_name_LineEdit_data.setText(base_name)

        widget._export_arcos_params()

        assert os.path.exists(out_path)
        df_loaded = pd.read_csv(out_path)
        pd.testing.assert_frame_equal(df_loaded, df_param)


def test_export_arcos_params_button(
    make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot]
):
    widget, _, qtbot = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        # make a test dataframe with 3 columns
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
        file_path = tmpdir
        base_name = "test"
        current_date = datetime.now().strftime("%Y%m%d")
        output_name = f"{current_date}_{base_name}_arcos_params.csv"
        out_path = os.path.join(file_path, output_name)

        # has to be set otherwise parameters are not exported
        widget._data_storage_instance.arcos_output._value = df

        df_param = widget._data_storage_instance.arcos_parameters.as_dataframe
        widget.file_LineEdit_data.setText(file_path)
        widget.base_name_LineEdit_data.setText(base_name)

        qtbot.mouseClick(widget.param_export_button, Qt.LeftButton)

        assert os.path.exists(out_path)
        df_loaded = pd.read_csv(out_path)
        pd.testing.assert_frame_equal(df_loaded, df_param)


def test_export_arcos_params_button_no_data(
    make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot], capsys
):
    widget, _, qtbot = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = tmpdir
        base_name = "test"

        widget.file_LineEdit_data.setText(file_path)
        widget.base_name_LineEdit_data.setText(base_name)

        qtbot.mouseClick(widget.param_export_button, Qt.LeftButton)

        captured = capsys.readouterr()
        assert "No data to export" in captured.out


def test_export_image_series(
    make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot]
):
    widget, viewer, _ = make_input_widget
    viewer.add_image(brain())
    with tempfile.TemporaryDirectory() as tmpdir:
        # make a test dataframe with 3 columns
        file_path = tmpdir
        base_name = "test"
        current_date = datetime.now().strftime("%Y%m%d")
        output_name = f"{current_date}_{base_name}_arcos_output"

        widget.file_LineEdit_img.setText(file_path)
        widget.base_name_LineEdit_img.setText(base_name)

        widget._export_image_series()
        filelist = os.listdir(file_path)
        for f in filelist[:]:
            if not (f.endswith(".png")):
                filelist.remove(f)
        assert filelist[0] == f"{output_name}_000.png"


def test_export_image_series_button(
    make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot]
):
    widget, viewer, qtbot = make_input_widget
    viewer.add_image(brain())
    with tempfile.TemporaryDirectory() as tmpdir:
        # make a test dataframe with 3 columns
        file_path = tmpdir
        base_name = "test"
        current_date = datetime.now().strftime("%Y%m%d")
        output_name = f"{current_date}_{base_name}_arcos_output"

        widget.file_LineEdit_img.setText(file_path)
        widget.base_name_LineEdit_img.setText(base_name)

        qtbot.mouseClick(widget.img_seq_export_button, Qt.LeftButton)
        filelist = os.listdir(file_path)
        for f in filelist[:]:
            if not (f.endswith(".png")):
                filelist.remove(f)
        assert filelist[0] == f"{output_name}_000.png"


def test_export_image_series_button_no_data(
    make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot], capsys
):
    widget, _, qtbot = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = tmpdir
        base_name = "test"

        widget.file_LineEdit_img.setText(file_path)
        widget.base_name_LineEdit_img.setText(base_name)

        qtbot.mouseClick(widget.img_seq_export_button, Qt.LeftButton)

        captured = capsys.readouterr()
        assert "No layers to export" in captured.out


@patch("qtpy.QtWidgets.QFileDialog.getExistingDirectory")
def test_browse_files(
    mock_get_open_file_name,
    make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot],
):
    widget, _, qtbot = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = tmpdir
        mock_get_open_file_name.return_value = file_path
        qtbot.mouseClick(widget.browse_file_data, Qt.LeftButton)
        assert widget.file_LineEdit_data.text() == file_path


@patch("qtpy.QtWidgets.QFileDialog.getExistingDirectory")
def test_browse_files_img(
    mock_get_open_file_name,
    make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot],
):
    widget, _, qtbot = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = tmpdir
        mock_get_open_file_name.return_value = file_path
        qtbot.mouseClick(widget.browse_file_img, Qt.LeftButton)
        assert widget.file_LineEdit_img.text() == file_path


def test_add_timestamp(make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot]):
    widget, viewer, qtbot = make_input_widget
    df_default = pd.DataFrame(
        columns=["parameter", "value"],
        data=[
            ["start_time", 0],
            ["step_time", 1],
            ["prefix", "T ="],
            ["suffix", "frame"],
            ["size", 12],
            ["x_shift", 12],
            ["y_shift", 0],
        ],
    )

    widget._add_timestamp()
    qtbot.mouseClick(widget.ts_dialog.set_options, Qt.LeftButton)
    df_ts = widget._data_storage_instance.timestamp_parameters.value.as_dataframe
    pd.testing.assert_frame_equal(df_default, df_ts)


def test_add_timestamp_button(
    make_input_widget: tuple[ExportWidget, viewer.Viewer, QtBot]
):
    widget, viewer, qtbot = make_input_widget
    df_default = pd.DataFrame(
        columns=["parameter", "value"],
        data=[
            ["start_time", 0],
            ["step_time", 1],
            ["prefix", "T ="],
            ["suffix", "frame"],
            ["size", 12],
            ["x_shift", 12],
            ["y_shift", 0],
        ],
    )

    qtbot.mouseClick(widget.add_timestamp_button, Qt.LeftButton)
    qtbot.mouseClick(widget.ts_dialog.set_options, Qt.LeftButton)
    df_ts = widget._data_storage_instance.timestamp_parameters.value.as_dataframe
    pd.testing.assert_frame_equal(df_default, df_ts)
