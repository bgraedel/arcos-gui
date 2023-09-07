from __future__ import annotations

import os
import tempfile
from datetime import datetime
from typing import TYPE_CHECKING
from unittest.mock import patch

import pandas as pd
import pytest
from arcos_gui.processing import DataStorage
from arcos_gui.widgets import ExportController
from qtpy.QtCore import Qt
from skimage.data import brain

if TYPE_CHECKING:
    from napari import viewer
    from pytestqt.qtbot import QtBot


@pytest.fixture()
def make_input_widget(
    qtbot, make_napari_viewer
) -> tuple[ExportController, viewer.Viewer, QtBot]:
    ds = DataStorage()
    viewer = make_napari_viewer()
    controller = ExportController(viewer, ds)
    qtbot.addWidget(controller.widget)
    return controller, viewer, qtbot


def test_open_widget(make_input_widget: tuple[ExportController, viewer.Viewer, QtBot]):
    input_data_widget, _, _ = make_input_widget
    assert input_data_widget


def test_get_current_date(
    make_input_widget: tuple[ExportController, viewer.Viewer, QtBot]
):
    controller, _, _ = make_input_widget
    assert controller._get_current_date() == datetime.now().strftime("%Y%m%d")


def test_export_arcos_data(
    make_input_widget: tuple[ExportController, viewer.Viewer, QtBot]
):
    with tempfile.TemporaryDirectory() as tmpdir:
        controller, _, _ = make_input_widget

        # make a test dataframe with 3 columns
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
        file_path = tmpdir
        base_name = "test"
        current_date = datetime.now().strftime("%Y%m%d")
        output_name = f"{current_date}_{base_name}_arcos_output.csv"
        out_path = os.path.join(file_path, output_name)

        controller._data_storage_instance.arcos_output._value = df
        controller.widget.file_LineEdit_data.setText(file_path)
        controller.widget.base_name_LineEdit_data.setText(base_name)

        controller._export_arcos_data()

        assert os.path.exists(out_path)
        df_loaded = pd.read_csv(out_path)
        pd.testing.assert_frame_equal(df_loaded, df)


def test_export_arcos_data_button(
    make_input_widget: tuple[ExportController, viewer.Viewer, QtBot]
):
    with tempfile.TemporaryDirectory() as tmpdir:
        controller, _, qtbot = make_input_widget

        # make a test dataframe with 3 columns
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
        file_path = tmpdir
        base_name = "test"
        current_date = datetime.now().strftime("%Y%m%d")
        output_name = f"{current_date}_{base_name}_arcos_output.csv"
        out_path = os.path.join(file_path, output_name)

        controller._data_storage_instance.arcos_output._value = df
        controller.widget.file_LineEdit_data.setText(file_path)
        controller.widget.base_name_LineEdit_data.setText(base_name)

        qtbot.mouseClick(controller.widget.data_export_button, Qt.LeftButton)

        assert os.path.exists(out_path)
        df_loaded = pd.read_csv(out_path)
        pd.testing.assert_frame_equal(df_loaded, df)


def test_export_arcos_data_button_no_data(
    make_input_widget: tuple[ExportController, viewer.Viewer, QtBot], capsys
):
    controller, _, qtbot = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = tmpdir
        base_name = "test"

        controller.widget.file_LineEdit_data.setText(file_path)
        controller.widget.base_name_LineEdit_data.setText(base_name)

        qtbot.mouseClick(controller.widget.data_export_button, Qt.LeftButton)

        captured = capsys.readouterr()
        assert "No data to export" in captured.out


def test_export_arcos_stats(
    make_input_widget: tuple[ExportController, viewer.Viewer, QtBot]
):
    controller, _, _ = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        # make a test dataframe with 3 columns
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
        file_path = tmpdir
        base_name = "test"
        current_date = datetime.now().strftime("%Y%m%d")
        output_name = f"{current_date}_{base_name}_arcos_stats.csv"
        out_path = os.path.join(file_path, output_name)

        controller._data_storage_instance.arcos_stats._value = df
        controller.widget.file_LineEdit_data.setText(file_path)
        controller.widget.base_name_LineEdit_data.setText(base_name)

        controller._export_arcos_stats()

        assert os.path.exists(out_path)
        df_loaded = pd.read_csv(out_path)
        pd.testing.assert_frame_equal(df_loaded, df)


def test_export_arcos_stats_button(
    make_input_widget: tuple[ExportController, viewer.Viewer, QtBot]
):
    controller, _, qtbot = make_input_widget

    with tempfile.TemporaryDirectory() as tmpdir:
        # make a test dataframe with 3 columns
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
        file_path = tmpdir
        base_name = "test"
        current_date = datetime.now().strftime("%Y%m%d")
        output_name = f"{current_date}_{base_name}_arcos_stats.csv"
        out_path = os.path.join(file_path, output_name)

        controller._data_storage_instance.arcos_stats._value = df
        controller.widget.file_LineEdit_data.setText(file_path)
        controller.widget.base_name_LineEdit_data.setText(base_name)

        qtbot.mouseClick(controller.widget.stats_export_button, Qt.LeftButton)

        assert os.path.exists(out_path)
        df_loaded = pd.read_csv(out_path)
        pd.testing.assert_frame_equal(df_loaded, df)


def test_export_arcos_stats_button_no_data(
    make_input_widget: tuple[ExportController, viewer.Viewer, QtBot], capsys
):
    controller, _, qtbot = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = tmpdir
        base_name = "test"

        controller.widget.file_LineEdit_data.setText(file_path)
        controller.widget.base_name_LineEdit_data.setText(base_name)

        qtbot.mouseClick(controller.widget.stats_export_button, Qt.LeftButton)

        captured = capsys.readouterr()
        assert "No data to export" in captured.out


def test_export_arcos_params(
    make_input_widget: tuple[ExportController, viewer.Viewer, QtBot]
):
    controller, _, _ = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        # make a test dataframe with 3 columns
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
        file_path = tmpdir
        base_name = "test"
        current_date = datetime.now().strftime("%Y%m%d")
        output_name = f"{current_date}_{base_name}_arcos_params.csv"
        out_path = os.path.join(file_path, output_name)

        # has to be set otherwise parameters are not exported
        controller._data_storage_instance.arcos_output._value = df

        df_param = controller._data_storage_instance.arcos_parameters.value.as_dataframe
        controller.widget.file_LineEdit_data.setText(file_path)
        controller.widget.base_name_LineEdit_data.setText(base_name)

        controller._export_arcos_params()

        assert os.path.exists(out_path)
        df_loaded = pd.read_csv(out_path)
        pd.testing.assert_frame_equal(df_loaded, df_param)


def test_export_arcos_params_button(
    make_input_widget: tuple[ExportController, viewer.Viewer, QtBot]
):
    controller, _, qtbot = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        # make a test dataframe with 3 columns
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
        file_path = tmpdir
        base_name = "test"
        current_date = datetime.now().strftime("%Y%m%d")
        output_name = f"{current_date}_{base_name}_arcos_params.csv"
        out_path = os.path.join(file_path, output_name)

        # has to be set otherwise parameters are not exported
        controller._data_storage_instance.arcos_output._value = df

        df_param = controller._data_storage_instance.arcos_parameters.value.as_dataframe
        controller.widget.file_LineEdit_data.setText(file_path)
        controller.widget.base_name_LineEdit_data.setText(base_name)

        qtbot.mouseClick(controller.widget.param_export_button, Qt.LeftButton)

        assert os.path.exists(out_path)
        df_loaded = pd.read_csv(out_path)
        pd.testing.assert_frame_equal(df_loaded, df_param)


def test_export_arcos_params_button_no_data(
    make_input_widget: tuple[ExportController, viewer.Viewer, QtBot], capsys
):
    controller, _, qtbot = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = tmpdir
        base_name = "test"

        controller.widget.file_LineEdit_data.setText(file_path)
        controller.widget.base_name_LineEdit_data.setText(base_name)

        qtbot.mouseClick(controller.widget.param_export_button, Qt.LeftButton)

        captured = capsys.readouterr()
        assert "No data to export" in captured.out


def test_export_image_series(
    make_input_widget: tuple[ExportController, viewer.Viewer, QtBot]
):
    controller, viewer, _ = make_input_widget
    viewer.add_image(brain())
    with tempfile.TemporaryDirectory() as tmpdir:
        # make a test dataframe with 3 columns
        file_path = tmpdir
        base_name = "test"

        controller.widget.file_LineEdit_img.setText(file_path)
        controller.widget.base_name_LineEdit_img.setText(base_name)

        controller._export_image_series()
        filelist = os.listdir(file_path)
        for f in filelist[:]:
            if not (f.endswith(".png")):
                filelist.remove(f)
        assert filelist[0].endswith(".png")


def test_export_image_series_button(
    make_input_widget: tuple[ExportController, viewer.Viewer, QtBot]
):
    controller, viewer, qtbot = make_input_widget
    viewer.add_image(brain())
    with tempfile.TemporaryDirectory() as tmpdir:
        # make a test dataframe with 3 columns
        file_path = tmpdir
        base_name = "test"

        controller.widget.file_LineEdit_img.setText(file_path)
        controller.widget.base_name_LineEdit_img.setText(base_name)

        qtbot.mouseClick(controller.widget.img_seq_export_button, Qt.LeftButton)
        filelist = os.listdir(file_path)
        for f in filelist[:]:
            if not (f.endswith(".png")):
                filelist.remove(f)
        assert filelist[0].endswith(".png")


def test_export_image_series_button_no_data(
    make_input_widget: tuple[ExportController, viewer.Viewer, QtBot], capsys
):
    controller, _, qtbot = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = tmpdir
        base_name = "test"

        controller.widget.file_LineEdit_img.setText(file_path)
        controller.widget.base_name_LineEdit_img.setText(base_name)

        qtbot.mouseClick(controller.widget.img_seq_export_button, Qt.LeftButton)

        captured = capsys.readouterr()
        assert "No layers to export" in captured.out


@patch("qtpy.QtWidgets.QFileDialog.getExistingDirectory")
def test_browse_files(
    mock_get_open_file_name,
    make_input_widget: tuple[ExportController, viewer.Viewer, QtBot],
):
    controller, _, qtbot = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = tmpdir
        mock_get_open_file_name.return_value = file_path
        qtbot.mouseClick(controller.widget.browse_file_data, Qt.LeftButton)
        assert controller.widget.file_LineEdit_data.text() == file_path


@patch("qtpy.QtWidgets.QFileDialog.getExistingDirectory")
def test_browse_files_img(
    mock_get_open_file_name,
    make_input_widget: tuple[ExportController, viewer.Viewer, QtBot],
):
    controller, _, qtbot = make_input_widget
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = tmpdir
        mock_get_open_file_name.return_value = file_path
        qtbot.mouseClick(controller.widget.browse_file_img, Qt.LeftButton)
        assert controller.widget.file_LineEdit_img.text() == file_path
