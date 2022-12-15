from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import napari.viewer
    from qtpy import QtWidgets
    from superqt import QRangeSlider


def remove_layers_after_columnpicker(viewer: napari.viewer.Viewer, arcos_layers: list):
    """Remove existing arcos layers before loading new data"""
    layer_list = get_layer_list(viewer)
    for layer in arcos_layers:
        if layer in layer_list:
            viewer.layers.remove(layer)


def get_layer_list(viewer: napari.viewer.Viewer):
    """Get list of open layers."""
    layer_list = [layer.name for layer in viewer.layers]
    return layer_list


def set_track_lenths(
    track_lenths_minmax: tuple,
    tracklenght_slider: QRangeSlider,
    min_tracklength_spinbox: QtWidgets.QDoubleSpinBox,
    max_tracklength_spinbox: QtWidgets.QDoubleSpinBox,
):
    if track_lenths_minmax[1] - track_lenths_minmax[0] > 1:
        tracklenght_slider.setMinimum(track_lenths_minmax[0])
        tracklenght_slider.setMaximum(track_lenths_minmax[1])

    min_tracklength_spinbox.setMinimum(track_lenths_minmax[0])
    max_tracklength_spinbox.setMinimum(track_lenths_minmax[0])

    min_tracklength_spinbox.setMaximum(track_lenths_minmax[1])
    max_tracklength_spinbox.setMaximum(track_lenths_minmax[1])

    min_tracklength_spinbox.setValue(track_lenths_minmax[0])
    max_tracklength_spinbox.setValue(track_lenths_minmax[1])
