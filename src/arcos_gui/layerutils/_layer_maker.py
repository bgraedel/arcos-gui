from __future__ import annotations

from typing import TYPE_CHECKING

from arcos_gui.tools import ARCOS_LAYERS
from napari.layers import Layer

from ._layer_data_tuple import (
    prepare_active_cells_layer,
    prepare_all_cells_layer,
    prepare_convex_hull_layer,
    prepare_events_layer,
    prepare_timestamp_layer,
)

if TYPE_CHECKING:
    from arcos_gui.processing import DataStorage
    from napari import viewer


class Layermaker:
    """Class to make layers for napari."""

    def __init__(self, viewer: viewer.Viewer, data_storage_instance: DataStorage):
        self.data_storage_instance = data_storage_instance
        self.viewer = viewer

    def _remove_old_layers(self):
        layers_names = [layer.name for layer in self.viewer.layers]
        for layer in ARCOS_LAYERS.values():
            if layer in layers_names:
                self.viewer.layers.remove(layer)

    def make_layers_bin(self):
        """adds layers from self.layers_to_create,
        whitch itself is upated from run_arcos method"""
        self._remove_old_layers()
        for result in self._layers_to_create_bin():
            if result:
                self.viewer.add_layer(Layer.create(*result))
                if result[1]["name"] == ARCOS_LAYERS["all_cells"]:
                    self._connect_all_cells_point_select()

    def make_layers_all(self, convex_hull: bool | None = None):
        """adds layers from self.layers_to_create,
        whitch itself is upated from run_arcos method"""
        self._remove_old_layers()
        if convex_hull is None:
            convex_hull = (
                self.data_storage_instance.arcos_parameters.add_convex_hull.value
            )
        for result in self._layers_to_create_all(convex_hull):
            if result:
                self.viewer.add_layer(Layer.create(*result))
                if result[1]["name"] == ARCOS_LAYERS["all_cells"]:
                    self._connect_all_cells_point_select()

    def _layers_to_create_all(self, convex_hull: bool = True):
        VcolsCore = self.data_storage_instance.columns.vcolscore
        layers: list = []
        layers = self._make_layers_bin(layers, VcolsCore)
        layers = self._make_layers_arcos(layers, VcolsCore, convex_hull)
        if len(VcolsCore) <= 3:
            self.viewer.dims.ndisplay = 2
        else:
            self.viewer.dims.ndisplay = 3
        return layers

    def _layers_to_create_bin(self):
        VcolsCore = self.data_storage_instance.columns.vcolscore
        layers: list = []
        layers = self._make_layers_bin(layers, VcolsCore)
        if len(VcolsCore) <= 3:
            self.viewer.dims.ndisplay = 2
        else:
            self.viewer.dims.ndisplay = 3
        return layers

    def _make_layers_bin(self, layers: list, VcolsCore: list):
        """returns a list of layers to be created"""
        VcolsCore = self.data_storage_instance.columns.vcolscore
        if self.data_storage_instance.arcos_binarization.value.empty:
            return layers
        layers.append(
            prepare_all_cells_layer(
                self.data_storage_instance.filtered_data.value,
                VcolsCore,
                self.data_storage_instance.columns.object_id,
                self.data_storage_instance.columns.measurement_column,
                self.data_storage_instance.lut,
                self.data_storage_instance.min_max_meas,
                self.data_storage_instance.point_size,
            )
        )

        layers.append(
            prepare_active_cells_layer(
                self.data_storage_instance.arcos_binarization.value,
                VcolsCore,
                self.data_storage_instance.columns.measurement_bin,
                self.data_storage_instance.point_size,
            )
        )
        return layers

    def _make_layers_arcos(
        self, layers: list, VcolsCore: list, convex_hull: bool = True
    ):
        if self.data_storage_instance.arcos_output.value.empty:
            return layers
        layers.append(
            prepare_events_layer(
                self.data_storage_instance.arcos_output.value,
                VcolsCore,
                self.data_storage_instance.point_size,
            )
        )

        if convex_hull:
            layers.append(
                prepare_convex_hull_layer(
                    self.data_storage_instance.filtered_data.value,
                    self.data_storage_instance.arcos_output.value,
                    self.data_storage_instance.columns.collid_name,
                    VcolsCore,
                )
            )

        return layers

    def _connect_all_cells_point_select(self):
        self.viewer.layers["All Cells"].events.current_properties.connect(
            self._pick_event
        )
        self._prev_point_data = None
        self.point_index = None

    def _pick_event(self, event):
        if self._prev_point_data is not None:
            event.sources[0].data[self.point_index] = self._prev_point_data
            self.viewer.layers["All Cells"].refresh()

        self.point_index = [i for i in event.sources[0].selected_data]
        self.id = event.sources[0].properties["id"][self.point_index]
        self._prev_point_data = event.sources[0].data[self.point_index]
        self.data_storage_instance.selected_object_id.value = self.id

    def make_timestamp_layer(self):
        """adds a timestamp layer to the viewer"""
        if list(self.viewer.layers) and self.viewer.layers.ndim < 2:
            return

        start_time = self.data_storage_instance.timestamp_parameters.value.start_time
        step_time = self.data_storage_instance.timestamp_parameters.value.step_time
        prefix = self.data_storage_instance.timestamp_parameters.value.prefix
        suffix = self.data_storage_instance.timestamp_parameters.value.suffix
        positoin = self.data_storage_instance.timestamp_parameters.value.position
        size = self.data_storage_instance.timestamp_parameters.value.size
        x_shift = self.data_storage_instance.timestamp_parameters.value.x_shift
        y_shift = self.data_storage_instance.timestamp_parameters.value.y_shift

        layer_list = [layer.name for layer in self.viewer.layers]
        if "Timestamp" in layer_list:
            self.viewer.layers.remove("Timestamp")

        ts_layer_data = prepare_timestamp_layer(
            self.viewer,
            start_time,
            step_time,
            positoin,
            prefix,
            suffix,
            size,
            x_shift,
            y_shift,
        )
        self.viewer.add_layer(Layer.create(*ts_layer_data))
