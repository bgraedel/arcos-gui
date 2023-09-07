from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pandas as pd
from arcos_gui.layerutils._layer_data_tuple import (
    prepare_active_cells_layer,
    prepare_all_cells_layer,
    prepare_convex_hull_layer,
    prepare_events_layer,
)
from arcos_gui.tools import ARCOS_LAYERS, COLOR_CYCLE
from napari.layers import Layer, Shapes, points
from numpy.testing import assert_array_equal

if TYPE_CHECKING:
    import napari.viewer


def test_prepare_all_cells_layer(make_napari_viewer: napari.viewer.Viewer):
    df_test = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    act_values = df_test.m.to_numpy()
    id_values = df_test.id.to_numpy()
    viewer = make_napari_viewer()
    layer = prepare_all_cells_layer(
        df_all=df_test,
        vColsCore=["t", "y", "x"],
        track_id_col="id",
        measurement_name="m",
        lut="inferno",
        min_max=(0, 1),
        size=1,
    )
    viewer.add_layer(Layer.create(*layer))
    assert viewer.layers[0].name == ARCOS_LAYERS["all_cells"]
    assert isinstance(viewer.layers[0], points.points.Points)
    assert_array_equal(viewer.layers[0].properties["act"], act_values)
    assert_array_equal(viewer.layers[0].properties["id"], id_values)
    assert_array_equal(viewer.layers[0].data[:, 0], df_test[["t"]].to_numpy().flatten())
    assert viewer.layers[0].face_contrast_limits == (0.0, 1.0)
    assert viewer.layers[0].face_colormap.name == "inferno"
    assert viewer.layers[0].size.all() == 1


def test_prepare_active_cells_layer(make_napari_viewer):
    df_test = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    df_test["m.bin"] = df_test["m"].apply(lambda x: 1 if x > 0 else 0)
    df_active = df_test[df_test["m.bin"] > 0]
    viewer = make_napari_viewer()
    layer = prepare_active_cells_layer(
        df_bin=df_test, vColsCore=["t", "y", "x"], measbin_col="m.bin", size=1
    )
    viewer.add_layer(Layer.create(*layer))
    assert viewer.layers[0].name == ARCOS_LAYERS["active_cells"]
    assert isinstance(viewer.layers[0], points.points.Points)
    assert_array_equal(
        viewer.layers[0].data[:, 0], df_active[["t"]].to_numpy().flatten()
    )
    assert viewer.layers[0].size.all() == 1


def test_prepare_events_layer(make_napari_viewer):
    df_test = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_output.csv")
    viewer = make_napari_viewer()
    layer = prepare_events_layer(df_coll=df_test, vColsCore=["t", "y", "x"], size=1)
    viewer.add_layer(Layer.create(*layer))
    assert viewer.layers[0].name == ARCOS_LAYERS["collective_events_cells"]
    assert isinstance(viewer.layers[0], points.points.Points)
    assert_array_equal(viewer.layers[0].data[:, 0], df_test[["t"]].to_numpy().flatten())
    assert viewer.layers[0].size.all() == 1
    assert all([i in COLOR_CYCLE for i in layer[1]["face_color"]])


@patch("arcos_gui.layerutils._layer_data_tuple.reshape_by_input_string")
@patch("arcos_gui.layerutils._layer_data_tuple.fix_3d_convex_hull")
@patch("arcos_gui.layerutils._layer_data_tuple.make_surface_3d")
@patch("arcos_gui.layerutils._layer_data_tuple.get_verticesHull")
def test_prepare_convex_hull_layer_mock2d(
    mock_2dhull, mock_3dhull, mock_fix3d, mock_reshape
):
    df_test_filtered = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_output.csv")
    df_test = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_output.csv")
    mock_2dhull.return_value = "hull_data2d", "color_ids2d"
    mock_3dhull.return_value = "hull_data3d"
    mock_fix3d.return_value = "hull_data3d_fixed"
    mock_reshape.return_value = "hull_data2d_reshaped"
    layer = prepare_convex_hull_layer(
        df_filtered=df_test_filtered,
        df_coll=df_test,
        collid_name="collid",
        vColsCore=["t", "y", "x"],
    )
    assert set(layer[0]) == {"hull_data2d_reshaped"}
    assert layer[1]["face_color"] == "color_ids2d"
    assert mock_3dhull.called is False
    assert mock_fix3d.called is False
    assert mock_2dhull.called


@patch("arcos_gui.layerutils._layer_data_tuple.fix_3d_convex_hull")
@patch("arcos_gui.layerutils._layer_data_tuple.make_surface_3d")
@patch("arcos_gui.layerutils._layer_data_tuple.get_verticesHull")
def test_prepare_convex_hull_layer_mock3d(mock_2dhull, mock_3dhull, mock_fix3d):
    # that source data is in fact 2d but by passing a random column (here x a second time)
    # was an additional argument to the
    # function, the function will assume that the data is 3d and the mock 3d functions should be called
    # with the appropriate corresponding arguments
    df_test_filtered = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_output.csv")
    df_test = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_output.csv")
    mock_2dhull.return_value = "hull_data2d", "color_ids2d"
    mock_3dhull.return_value = "hull_data3d"
    mock_fix3d.return_value = "hull_data3d_fixed"
    layer = prepare_convex_hull_layer(
        df_filtered=df_test_filtered,
        df_coll=df_test,
        collid_name="collid",
        vColsCore=["t", "y", "x", "x"],
    )
    assert layer[0] == "hull_data3d_fixed"
    assert mock_3dhull.called
    assert mock_fix3d.called
    assert mock_2dhull.called is False


def test_prepare_convex_hull_layer_with2d_data(make_napari_viewer):
    df_test_filtered = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_output.csv")
    df_test = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_output.csv")
    viewer = make_napari_viewer()
    layer = prepare_convex_hull_layer(
        df_filtered=df_test_filtered,
        df_coll=df_test,
        collid_name="collid",
        vColsCore=["t", "y", "x"],
    )
    viewer.add_layer(Layer.create(*layer))
    assert viewer.layers[0].name == ARCOS_LAYERS["event_hulls"]
    assert isinstance(viewer.layers[0], Shapes)
    assert all([i in COLOR_CYCLE for i in layer[1]["face_color"]])
