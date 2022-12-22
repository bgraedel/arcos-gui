from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pandas as pd
from arcos_gui.tools import ARCOS_LAYERS

if TYPE_CHECKING:
    pass

import numpy as np
import pytest
from arcos_gui.layerutils import Layermaker
from arcos_gui.processing import DataStorage
from napari import viewer


@pytest.fixture
def data_storage():
    data_storage = DataStorage()
    data_storage.load_data("src/arcos_gui/_tests/test_data/arcos_data.csv")
    data_storage.filtered_data = data_storage.original_data.value.copy()
    data_storage.columns.frame_column = "t"
    data_storage.columns.position_id = "None"
    data_storage.columns.measurement_column_2 = "None"
    data_storage.columns.additional_filter_column = "None"
    data_storage.columns.measurement_resc = "m"
    data_storage.columns.x_column = "x"
    data_storage.columns.y_column = "y"
    data_storage.columns.z_column = "None"
    data_storage.columns.measurement_bin = "m.bin"
    data_storage.columns.measurement_column = "m"
    data_storage.columns.object_id = "id"
    return data_storage


@pytest.fixture
def layermaker(data_storage, make_napari_viewer):
    viewer = make_napari_viewer()
    layermaker = Layermaker(viewer, data_storage)
    return layermaker


def test_init(layermaker):
    assert isinstance(layermaker, Layermaker)
    assert isinstance(layermaker.data_storage_instance, DataStorage)
    assert isinstance(layermaker.viewer, viewer.Viewer)


def test_remove_old_layers(layermaker):
    for i in ARCOS_LAYERS.values():
        layermaker.viewer.add_image(np.random.random((10, 10)), name=i)
    layermaker.viewer.add_image(np.random.random((10, 10)), name="not_arcos_layer")
    assert len(layermaker.viewer.layers) == len(ARCOS_LAYERS) + 1
    layermaker._remove_old_layers()
    assert len(layermaker.viewer.layers) == 1


def test_make_layers_bin_empty_data(layermaker):
    layermaker.make_layers_bin()
    assert len(layermaker.viewer.layers) == 0


def test_make_layers_all_empty_data(layermaker):
    layermaker.make_layers_all()
    assert len(layermaker.viewer.layers) == 0


def test_make_layers_bin(layermaker: Layermaker):
    df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    df["m.bin"] = df["m"].apply(lambda x: 1 if x > 0 else 0)
    layermaker.data_storage_instance.arcos_binarization.value = df
    layermaker.make_layers_bin()
    assert len(layermaker.viewer.layers) == 2
    assert layermaker.viewer.layers[0].name == ARCOS_LAYERS["all_cells"]
    assert layermaker.viewer.layers[1].name == ARCOS_LAYERS["active_cells"]


def test_make_layers_all_no_arcos_data(layermaker: Layermaker):
    df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    df["m.bin"] = df["m"].apply(lambda x: 1 if x > 0 else 0)
    layermaker.data_storage_instance.arcos_binarization.value = df
    layermaker.make_layers_all()
    assert len(layermaker.viewer.layers) == 2
    assert layermaker.viewer.layers[0].name == ARCOS_LAYERS["all_cells"]
    assert layermaker.viewer.layers[1].name == ARCOS_LAYERS["active_cells"]


def test_make_layers_events_only(layermaker: Layermaker):
    layermaker.data_storage_instance.arcos_output = pd.read_csv(
        "src/arcos_gui/_tests/test_data/arcos_output.csv"
    )
    layermaker.make_layers_all()
    assert len(layermaker.viewer.layers) == 2
    assert layermaker.viewer.layers[0].name == ARCOS_LAYERS["collective_events_cells"]
    assert layermaker.viewer.layers[1].name == ARCOS_LAYERS["event_hulls"]


def test_make_layers_all(layermaker: Layermaker):
    df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    df["m.bin"] = df["m"].apply(lambda x: 1 if x > 0 else 0)
    layermaker.data_storage_instance.arcos_binarization.value = df
    layermaker.data_storage_instance.arcos_output = pd.read_csv(
        "src/arcos_gui/_tests/test_data/arcos_output.csv"
    )
    layermaker.make_layers_all()
    assert len(layermaker.viewer.layers) == 4
    assert layermaker.viewer.layers[0].name == ARCOS_LAYERS["all_cells"]
    assert layermaker.viewer.layers[1].name == ARCOS_LAYERS["active_cells"]
    assert layermaker.viewer.layers[2].name == ARCOS_LAYERS["collective_events_cells"]
    assert layermaker.viewer.layers[3].name == ARCOS_LAYERS["event_hulls"]


def test_all_cells_no_convex_hull(layermaker: Layermaker):
    layermaker.data_storage_instance.arcos_output = pd.read_csv(
        "src/arcos_gui/_tests/test_data/arcos_output.csv"
    )
    layermaker.make_layers_all(convex_hull=False)
    assert len(layermaker.viewer.layers) == 1
    assert layermaker.viewer.layers[0].name == ARCOS_LAYERS["collective_events_cells"]


@patch("arcos_gui.layerutils._layer_maker.Layermaker._pick_event", autospec=True)
def test_all_cells_pick_event(mock_pick, layermaker: Layermaker):
    df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    df["m.bin"] = df["m"].apply(lambda x: 1 if x > 0 else 0)
    layermaker.data_storage_instance.arcos_binarization.value = df
    layermaker.make_layers_bin()
    assert len(layermaker.viewer.layers) == 2
    assert layermaker.viewer.layers[0].name == ARCOS_LAYERS["all_cells"]
    assert layermaker.viewer.layers[1].name == ARCOS_LAYERS["active_cells"]
    assert not mock_pick.called  # no pick event triggered yet
    layermaker.viewer.layers[0].events.current_properties()  # trigger pick event
    assert mock_pick.called  # pick event triggered


def test_make_timestamp_layer(layermaker: Layermaker):
    layermaker.viewer.add_image(np.random.random((10, 10, 10)), name="not_arcos_layer")
    layermaker.make_timestamp_layer()
    assert len(layermaker.viewer.layers) == 2
    assert ARCOS_LAYERS["timestamp"] in [i.name for i in layermaker.viewer.layers]
    layermaker.make_timestamp_layer()
    assert len(layermaker.viewer.layers) == 2
    assert ARCOS_LAYERS["timestamp"] in [i.name for i in layermaker.viewer.layers]
