from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
import pytest
from arcos_gui.processing import DataStorage
from arcos_gui.widgets import LayerPropertiesWidget

if TYPE_CHECKING:
    from napari import viewer
    from pytestqt.qtbot import QtBot


@pytest.fixture()
def make_input_widget(
    qtbot, make_napari_viewer
) -> tuple[LayerPropertiesWidget, viewer.Viewer, QtBot]:
    ds = DataStorage()
    viewer = make_napari_viewer()
    widget = LayerPropertiesWidget(viewer, ds)
    qtbot.addWidget(widget)
    return widget, viewer, qtbot


@pytest.fixture()
def make_points_layer_data_tuple():
    """Returns a tuple of data, properties and layer type for a points layer."""
    df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    df.interpolate(method="linear", inplace=True)
    df.x *= 100
    df.y *= 100
    datAll = df[["t", "y", "x"]].to_numpy()

    # a dictionary with activities;
    # shown as a color code of all cells
    datAllProp = {"act": df["x"].to_numpy().astype(float) * 100}
    # tuple to return layer as layer.data.tuple
    all_cells = (
        datAll,
        {
            "properties": datAllProp,
            "edge_width": 0,
            "edge_color": "act",
            "face_color": "act",
            "face_colormap": "inferno",
            "face_contrast_limits": None,
            "size": 2,
            "edge_width": 0,
            "opacity": 1,
            "symbol": "disc",
            "name": "All Cells",
        },
        "points",
    )
    return all_cells


def test_open_widget(
    make_input_widget: tuple[LayerPropertiesWidget, viewer.Viewer, QtBot]
):
    input_data_widget, _, _ = make_input_widget
    assert input_data_widget


def test_ranged_slider_widget(
    make_input_widget: tuple[LayerPropertiesWidget, viewer.Viewer, QtBot]
):
    widget, _, _ = make_input_widget
    assert widget.lut_slider


def test_ranged_slider_connection_to_spinboxes(
    make_input_widget: tuple[LayerPropertiesWidget, viewer.Viewer, QtBot]
):
    widget, _, _ = make_input_widget
    widget._reset_contrast()

    widget.lut_slider.setValue((0, 0.5))
    assert widget.min_lut_spinbox.value() == 0
    assert widget.max_lut_spinbox.value() == 0.5

    widget.lut_slider.setValue((0.1, 0.4))
    assert widget.min_lut_spinbox.value() == 0.1
    assert widget.max_lut_spinbox.value() == 0.4

    widget.min_lut_spinbox.setValue(0.2)
    assert widget.lut_slider.value() == (0.2, 0.4)

    widget.max_lut_spinbox.setValue(0.3)
    assert widget.lut_slider.value() == (0.2, 0.3)


def test_reset_contrast(
    make_input_widget: tuple[LayerPropertiesWidget, viewer.Viewer, QtBot]
):
    widget, _, _ = make_input_widget
    assert widget.lut_slider.value() == (0, 10)
    widget._reset_contrast()
    assert widget.lut_slider.value() == (0, 0.5)
    widget.data_storage_instance.min_max_meas = (10, 50)
    widget._reset_contrast()
    assert widget.lut_slider.value() == (10, 50)
    widget.lut_slider.setValue((15.5, 20.5))
    widget._reset_contrast()
    assert widget.lut_slider.value() == (10, 50)


def test_ui_callbacks_settings(
    make_input_widget: tuple[LayerPropertiesWidget, viewer.Viewer, QtBot],
    make_points_layer_data_tuple,
):
    widget, viewer, _ = make_input_widget
    data, properties, layer_type = make_points_layer_data_tuple
    points_layer = viewer.add_points(data, **properties)
    assert points_layer.face_colormap.name == "inferno"
    assert points_layer.face_contrast_limits == (0, 0)  # that is weird....
    # assert points_layer.size == 2
    widget.LUT.setCurrentText("viridis")
    widget.point_size.setValue(5)
    widget.data_storage_instance.min_max_meas = (5, 50)
    widget._reset_contrast()  # to set the slider to the new min_max_meas
    assert points_layer.face_colormap.name == "viridis"
    assert points_layer.face_contrast_limits == (5, 50)
    assert points_layer.size.flatten()[0] == 5.0


def test_set_settings(
    make_input_widget: tuple[LayerPropertiesWidget, viewer.Viewer, QtBot],
    make_points_layer_data_tuple,
):
    widget, viewer, _ = make_input_widget
    data, properties, layer_type = make_points_layer_data_tuple

    widget.LUT.setCurrentText("viridis")
    widget.point_size.setValue(5)
    widget.data_storage_instance.min_max_meas = (5, 50)
    widget._reset_contrast()  # to set the slider to the new min_max_meas
    points_layer = viewer.add_points(data, **properties)

    assert points_layer.face_colormap.name == "viridis"
    assert points_layer.face_contrast_limits == (5, 50)
    assert points_layer.size.flatten()[0] == 5.0
