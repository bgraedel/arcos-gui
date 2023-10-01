"""Module containing utility classes to make layers for napari."""

from __future__ import annotations

from typing import TYPE_CHECKING

from arcos_gui.tools import ARCOS_LAYERS
from napari.layers import Layer

from ._layer_data_tuple import (
    prepare_active_cells_layer,
    prepare_all_cells_layer,
    prepare_convex_hull_layer,
    prepare_events_layer,
)

if TYPE_CHECKING:
    from arcos_gui.processing import DataStorage
    from napari import viewer


class Layermaker:
    """Class to make layers for napari."""

    def __init__(self, viewer: viewer.Viewer, data_storage_instance: DataStorage):
        self.data_storage_instance = data_storage_instance
        self.viewer = viewer
        self.padd_time = True

    def _remove_old_layers(self):
        layers_names = [layer.name for layer in self.viewer.layers]
        for layer in ARCOS_LAYERS.values():
            if layer in layers_names:
                self.viewer.layers.remove(layer)

    def make_layers_bin(
        self, all_cells: bool | None = None, active_cells: bool | None = None
    ):
        """adds layers from self.layers_to_create,
        whitch itself is upated from run_arcos method"""
        if all_cells is None:
            all_cells = (
                self.data_storage_instance.arcos_parameters.value.add_all_cells.value
            )
        if active_cells is None:
            active_cells = (
                self.data_storage_instance.arcos_parameters.value.add_bin_cells.value
            )

        self._remove_old_layers()
        for result in self._layers_to_create_bin(
            all_cells=all_cells, active_cells=active_cells
        ):
            if result:
                self.viewer.add_layer(Layer.create(*result))
                if result[1]["name"] == ARCOS_LAYERS["all_cells"]:
                    self._connect_all_cells_point_select()

    def make_layers_all(
        self,
        convex_hull: bool | None = None,
        all_cells: bool | None = None,
        active_cells: bool | None = None,
    ):
        """adds layers from self.layers_to_create,
        whitch itself is upated from run_arcos method"""
        self._remove_old_layers()
        if convex_hull is None:
            convex_hull = (
                self.data_storage_instance.arcos_parameters.value.add_convex_hull.value
            )
        if all_cells is None:
            all_cells = (
                self.data_storage_instance.arcos_parameters.value.add_all_cells.value
            )
        if active_cells is None:
            active_cells = (
                self.data_storage_instance.arcos_parameters.value.add_bin_cells.value
            )

        for result in self._layers_to_create_all(convex_hull, all_cells, active_cells):
            if result:
                self.viewer.add_layer(Layer.create(*result))
                if result[1]["name"] == ARCOS_LAYERS["all_cells"]:
                    self._connect_all_cells_point_select()

    def _layers_to_create_all(
        self,
        convex_hull: bool = True,
        all_cells: bool = True,
        active_cells: bool = True,
    ):
        VcolsCore = self.data_storage_instance.columns.value.vcolscore
        layers: list = []
        layers = self._make_layers_bin(layers, VcolsCore, all_cells, active_cells)
        layers = self._make_layers_arcos(layers, VcolsCore, convex_hull)
        if len(VcolsCore) <= 3:
            self.viewer.dims.ndisplay = 2
        else:
            self.viewer.dims.ndisplay = 3
        return layers

    def _layers_to_create_bin(self, all_cells: bool = True, active_cells: bool = True):
        VcolsCore = self.data_storage_instance.columns.value.vcolscore
        layers: list = []
        layers = self._make_layers_bin(layers, VcolsCore, all_cells, active_cells)
        if len(VcolsCore) <= 3:
            self.viewer.dims.ndisplay = 2
        else:
            self.viewer.dims.ndisplay = 3
        return layers

    def _make_layers_bin(
        self,
        layers: list,
        VcolsCore: list,
        all_cells: bool = True,
        active_cells: bool = True,
    ):
        """returns a list of layers to be created"""
        VcolsCore = self.data_storage_instance.columns.value.vcolscore
        if self.data_storage_instance.arcos_binarization.value.empty:
            return layers
        if all_cells:
            layers.append(
                prepare_all_cells_layer(
                    self.data_storage_instance.filtered_data.value,
                    VcolsCore,
                    self.data_storage_instance.columns.value.object_id,
                    self.data_storage_instance.columns.value.measurement_column,
                    self.data_storage_instance.lut.value,
                    self.data_storage_instance.min_max_meas.value,
                    self.data_storage_instance.point_size.value,
                    self.data_storage_instance.output_order.value,
                )
            )
        if active_cells:
            layers.append(
                prepare_active_cells_layer(
                    self.data_storage_instance.arcos_binarization.value,
                    VcolsCore,
                    self.data_storage_instance.columns.value.measurement_bin,
                    self.data_storage_instance.point_size.value,
                    self.data_storage_instance.output_order.value,
                    self.padd_time,
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
                self.data_storage_instance.point_size.value,
                self.data_storage_instance.output_order.value,
                self.padd_time,
            )
        )

        if convex_hull:
            layers.append(
                prepare_convex_hull_layer(
                    self.data_storage_instance.filtered_data.value,
                    self.data_storage_instance.arcos_output.value,
                    self.data_storage_instance.columns.value.collid_name,
                    VcolsCore,
                    self.data_storage_instance.output_order.value,
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

        self.point_index = list(event.sources[0].selected_data)
        self.id = event.sources[0].properties["id"][self.point_index]
        self._prev_point_data = event.sources[0].data[self.point_index]
        self.data_storage_instance.selected_object_id.value = self.id.tolist()
