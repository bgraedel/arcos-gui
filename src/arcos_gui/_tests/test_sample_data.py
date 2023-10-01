from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from arcos_gui.sample_data._sample_data import (
    download,
    load_real_dataset,
    load_synthetic_dataset,
)

if TYPE_CHECKING:
    from arcos_gui._main_widget import MainWindow


@pytest.fixture()
def dock_arcos_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    mywidget = viewer.window.add_plugin_dock_widget(
        plugin_name="arcos-gui", widget_name="ARCOS Main Widget"
    )
    yield viewer, mywidget[1]
    viewer.close()


def test_download(tmpdir):
    temp_path = tmpdir
    file_path = "https://macdobry.net/ARCOS/data/MDCK_example_event.tif"
    file_name = os.path.join(temp_path, "MDCK_example_event.tif")
    download(file_path, file_name)
    assert os.path.exists(file_name)


def test_load_sample_data(dock_arcos_widget, qtbot):
    widget: MainWindow
    _, widget = dock_arcos_widget
    load_synthetic_dataset()
    with qtbot.waitSignal(widget._input_controller.loading_worker.finished):
        widget._input_controller.picker.ok_button.click()
    assert not widget.data.filtered_data.value.empty
    assert widget._input_controller.picker.frame.currentText() == "t"
    assert widget._input_controller.picker.track_id.currentText() == "id"
    assert widget._input_controller.picker.x_coordinates.currentText() == "x"
    assert widget._input_controller.picker.y_coordinates.currentText() == "y"
    assert widget._input_controller.picker.measurement.currentText() == "m"


def test_load_real_data(dock_arcos_widget, qtbot):
    widget: MainWindow
    _, widget = dock_arcos_widget
    load_real_dataset(load_image=False)
    with qtbot.waitSignal(widget._input_controller.loading_worker.finished):
        widget._input_controller.picker.ok_button.click()
    assert not widget.data.filtered_data.value.empty
    assert widget._input_controller.picker.frame.currentText() == "t"
    assert widget._input_controller.picker.track_id.currentText() == "id"
    assert widget._input_controller.picker.x_coordinates.currentText() == "x"
    assert widget._input_controller.picker.y_coordinates.currentText() == "y"
    assert widget._input_controller.picker.measurement.currentText() == "m"
