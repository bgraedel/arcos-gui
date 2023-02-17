from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from arcos_gui.processing import DataStorage
from arcos_gui.widgets import collevPlotWidget, tsPlotWidget
from qtpy.QtCore import Qt

if TYPE_CHECKING:
    from napari import viewer
    from pytestqt.qtbot import QtBot


@pytest.fixture()
def make_ts_widget(
    qtbot, make_napari_viewer
) -> tuple[tsPlotWidget, viewer.Viewer, QtBot]:
    ds = DataStorage()
    viewer = make_napari_viewer()
    widget = tsPlotWidget(viewer, ds)
    qtbot.addWidget(widget)
    return widget, viewer, qtbot


@pytest.fixture()
def make_collev_widget(
    qtbot, make_napari_viewer
) -> tuple[collevPlotWidget, viewer.Viewer, QtBot]:
    ds = DataStorage()
    viewer = make_napari_viewer()
    widget = collevPlotWidget(viewer, ds)
    qtbot.addWidget(widget)
    return widget, viewer, qtbot


def test_open_widget_tsPlot(make_ts_widget: tuple[tsPlotWidget, viewer.Viewer, QtBot]):
    input_data_widget, _, _ = make_ts_widget
    assert input_data_widget


@patch("arcos_gui.tools.TimeSeriesPlots.update_plot")
def test_ts_on_data_update(
    mock_update_plot, make_ts_widget: tuple[tsPlotWidget, viewer.Viewer, QtBot]
):
    widget, _, _ = make_ts_widget
    mock_update_plot.return_value = "updated"
    widget._on_data_update()
    assert mock_update_plot.called


@patch("arcos_gui.tools.TimeSeriesPlots.update_plot")
def test_ts_original_data_changed(
    mock_update_plot, make_ts_widget: tuple[tsPlotWidget, viewer.Viewer, QtBot]
):
    widget, _, _ = make_ts_widget
    mock_update_plot.return_value = "updated"
    widget._data_storage_instance.load_data(
        "src/arcos_gui/_tests/test_data/arcos_data.csv", trigger_callback=True
    )
    assert mock_update_plot.called


@patch("arcos_gui.tools.TimeSeriesPlots.update_plot")
def test_ts_bin_data_changed(
    mock_update_plot, make_ts_widget: tuple[tsPlotWidget, viewer.Viewer, QtBot]
):
    widget, _, _ = make_ts_widget
    mock_update_plot.return_value = "updated"
    widget._data_storage_instance.load_data(
        "src/arcos_gui/_tests/test_data/arcos_data.csv", trigger_callback=False
    )
    widget._data_storage_instance.arcos_binarization = (
        widget._data_storage_instance.original_data._value.copy()
    )
    assert mock_update_plot.called


@patch("arcos_gui.tools.TimeSeriesPlots.update_plot")
def test_ts_selected_oid_changed(
    mock_update_plot, make_ts_widget: tuple[tsPlotWidget, viewer.Viewer, QtBot]
):
    widget, _, _ = make_ts_widget
    mock_update_plot.return_value = "updated"
    widget._data_storage_instance.selected_object_id = 1
    assert mock_update_plot.called


def test_on_data_update_no_data(
    make_ts_widget: tuple[tsPlotWidget, viewer.Viewer, QtBot], capsys
):
    widget, _, _ = make_ts_widget
    widget._on_data_update()
    captured = capsys.readouterr()
    assert "No Data to plot" in captured.out


def test_on_data_update_data(
    make_ts_widget: tuple[tsPlotWidget, viewer.Viewer, QtBot], capsys
):
    widget, _, _ = make_ts_widget
    widget._data_storage_instance.columns.position_id = "Position"
    widget._data_storage_instance.columns.additional_filter_column = "None"
    widget._data_storage_instance.columns.x_column = "x"
    widget._data_storage_instance.columns.y_column = "y"
    widget._data_storage_instance.columns.object_id = "id"
    widget._data_storage_instance.columns.frame_column = "t"
    widget._data_storage_instance.columns.measurement_column = "m"
    widget._data_storage_instance.columns.measurement_resc = "m"
    widget._data_storage_instance.load_data(
        "src/arcos_gui/_tests/test_data/arcos_data.csv", trigger_callback=False
    )
    widget._data_storage_instance.arcos_binarization._value = (
        widget._data_storage_instance.original_data._value.copy()
    )
    widget.timeseriesplot.combo_box.setCurrentText("measurment density plot")
    widget._on_data_update()
    assert widget.timeseriesplot.ax.lines


@patch("arcos_gui.tools.TimeSeriesPlots.data_clear")
def test_ts_on_data_clear(
    mock_data_clear, make_ts_widget: tuple[tsPlotWidget, viewer.Viewer, QtBot]
):
    widget, _, _ = make_ts_widget
    mock_data_clear.return_value = "cleared"
    widget._on_data_update()
    assert mock_data_clear.called


def test_ts_plot_popup(make_ts_widget: tuple[tsPlotWidget, viewer.Viewer, QtBot]):
    widget, _, qtbot = make_ts_widget
    assert widget.plot_dialog_data.isVisibleTo(widget) is False
    assert widget.plot_dialog_data.tsplot_layout.count() == 0
    assert widget.tsplot_layout.count() == 2
    qtbot.mouseClick(widget.expand_plot, Qt.LeftButton)
    assert widget.plot_dialog_data.isVisibleTo(widget)
    assert widget.plot_dialog_data.tsplot_layout.count() == 1
    assert widget.tsplot_layout.count() == 1
    widget.plot_dialog_data.close()
    assert widget.plot_dialog_data.isVisibleTo(widget) is False
    assert widget.plot_dialog_data.tsplot_layout.count() == 0
    assert widget.tsplot_layout.count() == 2


def test_open_widget_collevPlot(
    make_collev_widget: tuple[collevPlotWidget, viewer.Viewer, QtBot]
):
    input_data_widget, _, _ = make_collev_widget
    assert input_data_widget


@patch("arcos_gui.tools.CollevPlotter.update_plot")
@patch("arcos_gui.tools.NoodlePlot.update_plot")
def test_collev_on_data_update(
    mock_update_CollevPlotter,
    mock_update_NoodlePlot,
    make_collev_widget: tuple[collevPlotWidget, viewer.Viewer, QtBot],
):
    widget, _, _ = make_collev_widget
    mock_update_CollevPlotter.return_value = "updated"
    mock_update_NoodlePlot.return_value = "updated"
    widget._on_data_update()
    assert mock_update_CollevPlotter.called
    assert mock_update_NoodlePlot.called


@patch("arcos_gui.tools.CollevPlotter.clear_plot")
@patch("arcos_gui.tools.NoodlePlot.clear_plot")
def test_collev_original_data_changed(
    mock_clear_CollevPlotter,
    mock_clear_NoodlePlot,
    make_collev_widget: tuple[collevPlotWidget, viewer.Viewer, QtBot],
):
    widget, _, _ = make_collev_widget
    mock_clear_CollevPlotter.return_value = "updated"
    mock_clear_NoodlePlot.return_value = "updated"
    widget._data_storage_instance.load_data(
        "src/arcos_gui/_tests/test_data/arcos_data.csv", trigger_callback=True
    )
    assert mock_clear_CollevPlotter.called
    assert mock_clear_NoodlePlot.called


@patch("arcos_gui.tools.CollevPlotter.clear_plot")
@patch("arcos_gui.tools.NoodlePlot.clear_plot")
def test_collev_bin_data_changed(
    mock_clear_CollevPlotter,
    mock_clear_NoodlePlot,
    make_collev_widget: tuple[collevPlotWidget, viewer.Viewer, QtBot],
):
    widget, _, _ = make_collev_widget
    mock_clear_CollevPlotter.return_value = "updated"
    mock_clear_NoodlePlot.return_value = "updated"
    widget._data_storage_instance.load_data(
        "src/arcos_gui/_tests/test_data/arcos_data.csv", trigger_callback=False
    )
    widget._data_storage_instance.arcos_binarization = (
        widget._data_storage_instance.original_data._value.copy()
    )

    assert mock_clear_CollevPlotter.called
    assert mock_clear_NoodlePlot.called


@patch("arcos_gui.tools.CollevPlotter.update_plot")
@patch("arcos_gui.tools.NoodlePlot.update_plot")
def test_collev_arcos_data_changed(
    mock_update_CollevPlotter,
    mock_update_NoodlePlot,
    make_collev_widget: tuple[collevPlotWidget, viewer.Viewer, QtBot],
):
    widget, _, _ = make_collev_widget
    mock_update_CollevPlotter.return_value = "updated"
    mock_update_NoodlePlot.return_value = "updated"
    widget._data_storage_instance.load_data(
        "src/arcos_gui/_tests/test_data/arcos_data.csv", trigger_callback=False
    )
    widget._data_storage_instance.arcos_output = (
        widget._data_storage_instance.original_data._value.copy()
    )

    assert mock_update_CollevPlotter.called
    assert mock_update_NoodlePlot.called


def test_collev_plot_popup(
    make_collev_widget: tuple[collevPlotWidget, viewer.Viewer, QtBot]
):
    widget, _, qtbot = make_collev_widget
    assert widget.plot_dialog_collev.isVisibleTo(widget) is False
    assert widget.plot_dialog_collev.tsplot_layout.count() == 0
    assert widget.collevplot_goupbox.layout().count() == 2
    qtbot.mouseClick(widget.expand_plot, Qt.LeftButton)
    assert widget.plot_dialog_collev.isVisibleTo(widget)
    assert widget.plot_dialog_collev.tsplot_layout.count() == 1
    assert widget.collevplot_goupbox.layout().count() == 1
    widget.plot_dialog_collev.close()
    assert widget.plot_dialog_collev.isVisibleTo(widget) is False
    assert widget.plot_dialog_collev.tsplot_layout.count() == 0
    assert widget.collevplot_goupbox.layout().count() == 2
