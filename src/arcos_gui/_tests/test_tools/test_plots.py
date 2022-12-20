from __future__ import annotations

from unittest.mock import patch

import pandas as pd
from arcos_gui.tools import ARCOS_LAYERS, CollevPlotter, NoodlePlot, TimeSeriesPlots
from matplotlib.backend_bases import MouseEvent, PickEvent
from pytestqt.qtbot import QtBot


def test_collev_plotter_no_data(make_napari_viewer):
    viewer = make_napari_viewer()
    widget = CollevPlotter(viewer=viewer)
    assert not widget.ax.has_data()


def test_collev_plotter_with_data(make_napari_viewer):
    viewer = make_napari_viewer()
    widget = CollevPlotter(viewer=viewer)
    df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_output.csv")
    widget.update_plot(
        frame_col="t",
        trackid_col="id",
        posx="x",
        posy="y",
        posz="None",
        arcos_data=df,
        point_size=10,
    )
    assert widget.ax.has_data()


def test_pick_event(make_napari_viewer):
    viewer = make_napari_viewer()
    widget = CollevPlotter(viewer=viewer)
    df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_output.csv")
    widget.update_plot(
        frame_col="t",
        trackid_col="id",
        posx="x",
        posy="y",
        posz="None",
        arcos_data=df,
        point_size=10,
    )

    # somehow this works... it seems a bit fishy but i spent so much time
    # trying to figure out how to do this that i will just leave it for now
    x_val = widget.stats[["total_size"]].to_numpy()[0][0]
    y_val = widget.stats[["duration"]].to_numpy()[0][0]
    index = widget.stats.index.to_numpy()[:1]

    event = MouseEvent("button_press_event", widget.canvas, x_val, y_val, button=1)
    pick_event_event = PickEvent(
        "pick_event", widget.canvas, event, widget.ax.collections[0], ind=index
    )
    widget.canvas.callbacks.process("pick_event", pick_event_event)
    # Simulate a pick event at the location (x, y)
    # widget.canvas.pick_event(event, widget.ax.collections[0], ind=index)
    assert viewer.layers[0].name == ARCOS_LAYERS["event_boundingbox"]


def test_collev_noodles_no_data(make_napari_viewer):
    viewer = make_napari_viewer()
    widget = NoodlePlot(viewer=viewer)
    assert not widget.ax.has_data()


def test_noodles_with_data(make_napari_viewer):
    viewer = make_napari_viewer()
    widget = NoodlePlot(viewer=viewer)
    df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_output.csv")
    widget.update_plot(
        frame_col="t",
        trackid_col="id",
        posx="x",
        posy="y",
        posz="None",
        arcos_data=df,
        point_size=10,
    )
    assert widget.ax.has_data()


def test_pick_event_noodles(make_napari_viewer):
    viewer = make_napari_viewer()
    widget = NoodlePlot(viewer=viewer)
    df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_output.csv")
    widget.update_plot(
        frame_col="t",
        trackid_col="id",
        posx="x",
        posy="y",
        posz="None",
        arcos_data=df,
        point_size=10,
    )

    # yey, this works too
    x_val = widget.dat_grpd[0][:, 2][0]
    y_val = widget.dat_grpd[0][:, widget.projection_index][0]

    event = MouseEvent("button_press_event", widget.canvas, x_val, y_val, button=1)

    # Simulate a pick event at the location (x, y)
    pick_event_event = PickEvent("pick_event", widget.canvas, event, widget.ax.lines[0])
    widget.canvas.callbacks.process("pick_event", pick_event_event)
    # widget.canvas.pick_event(event, widget.ax.lines[0])
    assert viewer.layers[0].name == ARCOS_LAYERS["event_boundingbox"]


def test_time_series_plots_no_data(qtbot: QtBot):
    widget = TimeSeriesPlots()
    qtbot.addWidget(widget)
    assert not widget.ax.has_data()


def test_time_series_plots_with_data(qtbot: QtBot):
    widget = TimeSeriesPlots()
    qtbot.addWidget(widget)
    df_arcos = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_output.csv")
    df_input = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    widget.update_plot(
        dataframe=df_input,
        dataframe_resc=df_arcos,
        frame_col="t",
        track_id_col="id",
        x_coord_col="x",
        y_coord_col="y",
        measurement_col="m",
        measurement_resc_col="m.resc",
        object_id_number=None,
    )
    assert widget.ax.has_data()


def test_all_plottypes_ts_plot(qtbot: QtBot):
    widget = TimeSeriesPlots()
    qtbot.addWidget(widget)
    df_arcos = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_output.csv")
    df_input = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    widget.update_plot(
        dataframe=df_input,
        dataframe_resc=df_arcos,
        frame_col="t",
        track_id_col="id",
        x_coord_col="x",
        y_coord_col="y",
        measurement_col="m",
        measurement_resc_col="m.resc",
        object_id_number=None,
    )
    for i in range(widget.combo_box.count()):
        widget.combo_box.setCurrentIndex(i)
        assert widget.ax.has_data()


@patch("arcos_gui.tools.TimeSeriesPlots._update")
def test_update_data_button_ts_plot(mock_update, qtbot: QtBot):
    mock_update.return_value = "updated"
    widget = TimeSeriesPlots()
    qtbot.addWidget(widget)
    widget.combo_box.setCurrentText("original vs detreded")
    assert mock_update.assert_called_once
    widget.button.click()
    # check if the update function was called a second time
    assert mock_update.call_count == 2
