from __future__ import annotations

from unittest.mock import patch

from arcos_gui.tools import (
    get_layer_list,
    remove_layers_after_columnpicker,
    set_track_lenths,
)


def test_remove_layers_after_columnpicker(make_napari_viewer):
    viewer = make_napari_viewer()
    viewer.add_points(name="test")
    viewer.add_points(name="test2")
    viewer.add_points(name="test3")
    viewer.add_points(name="test4")
    remove_layers_after_columnpicker(viewer, ["test", "test2"])
    assert get_layer_list(viewer) == ["test3", "test4"]


def test_get_layer_list(make_napari_viewer):
    viewer = make_napari_viewer()
    viewer.add_points(name="test")
    viewer.add_points(name="test2")
    viewer.add_points(name="test3")
    viewer.add_points(name="test4")
    assert get_layer_list(viewer) == ["test", "test2", "test3", "test4"]


def test_set_track_lenths(make_napari_viewer):
    viewer = make_napari_viewer()
    viewer.add_points(name="test")
    viewer.add_points(name="test2")
    viewer.add_points(name="test3")
    viewer.add_points(name="test4")
    with patch("superqt.QRangeSlider") as mock_slider:
        with patch("qtpy.QtWidgets.QDoubleSpinBox") as mock_max_spinbox:
            with patch("qtpy.QtWidgets.QDoubleSpinBox") as mock_min_spinbox:
                set_track_lenths(
                    (1, 10), mock_slider, mock_min_spinbox, mock_max_spinbox
                )
                mock_slider.setMinimum.assert_called_once_with(1)
                mock_slider.setMaximum.assert_called_once_with(10)
                mock_min_spinbox.setMinimum.assert_called_once_with(1)
                mock_max_spinbox.setMaximum.assert_called_once_with(10)
                mock_min_spinbox.setValue.assert_called_once_with(1)
                mock_max_spinbox.setValue.assert_called_once_with(10)
