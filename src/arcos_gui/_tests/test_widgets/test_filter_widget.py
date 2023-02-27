from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from arcos_gui.processing import DataStorage
from arcos_gui.tools import set_track_lenths
from arcos_gui.widgets import FilterController
from qtpy.QtCore import Qt

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


@pytest.fixture()
def make_input_widget(qtbot, make_napari_viewer) -> tuple[FilterController, QtBot]:
    viewer = make_napari_viewer()
    ds = DataStorage()
    controller = FilterController(viewer, ds)
    qtbot.addWidget(controller.widget)
    return controller, qtbot


def test_open_widget(make_input_widget: tuple[FilterController, QtBot]):
    input_data_widget, _ = make_input_widget
    assert input_data_widget


def test_ranged_slider_widget(make_input_widget: tuple[FilterController, QtBot]):
    controller, qtbot = make_input_widget
    assert controller.widget.tracklenght_slider


def test_ranged_slider_connection_to_spinboxes(
    make_input_widget: tuple[FilterController, QtBot]
):
    controller, qtbot = make_input_widget

    # set the range of the slider and spinboxes
    set_track_lenths(
        (0, 20),
        controller.widget.tracklenght_slider,
        controller.widget.min_tracklength_spinbox,
        controller.widget.max_tracklength_spinbox,
    )
    controller.widget.tracklenght_slider.setValue((0, 20))
    assert controller.widget.min_tracklength_spinbox.value() == 0
    assert controller.widget.max_tracklength_spinbox.value() == 20

    controller.widget.tracklenght_slider.setValue((5, 15))
    assert controller.widget.min_tracklength_spinbox.value() == 5
    assert controller.widget.max_tracklength_spinbox.value() == 15

    controller.widget.min_tracklength_spinbox.setValue(10)
    assert controller.widget.tracklenght_slider.value() == (10, 15)

    controller.widget.max_tracklength_spinbox.setValue(10)
    assert controller.widget.tracklenght_slider.value() == (10, 10)


def test_default_visible(make_input_widget: tuple[FilterController, QtBot]):
    controller, qtbot = make_input_widget
    assert controller.widget.tracklenght_slider.isVisibleTo(controller.widget) is True
    assert controller.widget.tracklength_label.isVisibleTo(controller.widget) is True
    assert (
        controller.widget.min_tracklength_spinbox.isVisibleTo(controller.widget) is True
    )
    assert (
        controller.widget.max_tracklength_spinbox.isVisibleTo(controller.widget) is True
    )
    assert controller.widget.position.isVisibleTo(controller.widget) is False
    assert controller.widget.position_label.isVisibleTo(controller.widget) is False
    assert (
        controller.widget.additional_filter_combobox.isVisibleTo(controller.widget)
        is False
    )
    assert (
        controller.widget.additional_filter_combobox_label.isVisibleTo(
            controller.widget
        )
        is False
    )


def test_toggle_visible(make_input_widget: tuple[FilterController, QtBot]):
    controller, qtbot = make_input_widget
    assert controller.widget.position_label.isVisibleTo(controller.widget) is False
    assert controller.widget.position.isVisibleTo(controller.widget) is False
    assert (
        controller.widget.additional_filter_combobox.isVisibleTo(controller.widget)
        is False
    )
    assert (
        controller.widget.additional_filter_combobox_label.isVisibleTo(
            controller.widget
        )
        is False
    )
    controller.widget.set_position_visible()
    assert controller.widget.position.isVisibleTo(controller.widget) is True
    assert controller.widget.position_label.isVisibleTo(controller.widget) is True
    controller.widget.set_additional_filter_visible()
    assert (
        controller.widget.additional_filter_combobox.isVisibleTo(controller.widget)
        is True
    )
    assert (
        controller.widget.additional_filter_combobox_label.isVisibleTo(
            controller.widget
        )
        is True
    )
    controller._set_default_values()
    assert controller.widget.position.isVisibleTo(controller.widget) is False
    assert controller.widget.position_label.isVisibleTo(controller.widget) is False
    assert (
        controller.widget.additional_filter_combobox.isVisibleTo(controller.widget)
        is False
    )
    assert (
        controller.widget.additional_filter_combobox_label.isVisibleTo(
            controller.widget
        )
        is False
    )


def test_filter_no_data(
    make_input_widget: tuple[FilterController, QtBot], capsys, make_napari_viewer
):
    controller, qtbot = make_input_widget
    # make viewer for show info function of napari
    make_napari_viewer()
    controller._filter_data()
    captured = capsys.readouterr()
    assert captured.out == "INFO: No data loaded, or not loaded correctly\n"
    assert controller.data_storage_instance.filtered_data.value.empty


def test_filter_data(make_input_widget: tuple[FilterController, QtBot]):
    controller, qtbot = make_input_widget
    # need to set these things otherwise the filter output will be empty
    set_track_lenths(
        (0, 100),
        controller.widget.tracklenght_slider,
        controller.widget.min_tracklength_spinbox,
        controller.widget.max_tracklength_spinbox,
    )
    controller.data_storage_instance.columns.position_id = "Position"
    controller.data_storage_instance.columns.additional_filter_column = "None"
    controller.data_storage_instance.columns.x_column = "x"
    controller.data_storage_instance.columns.y_column = "y"
    controller.data_storage_instance.columns.object_id = "id"
    controller.data_storage_instance.columns.frame_column = "t"
    controller.data_storage_instance.columns.measurement_column = "m"
    controller.widget.position.addItem(str(1), 1)
    controller.widget.additional_filter_combobox.addItem(str(None), "None")
    controller.data_storage_instance.load_data(
        "src/arcos_gui/_tests/test_data/arcos_data.csv", trigger_callback=False
    )
    assert controller.data_storage_instance.filtered_data.value.empty
    controller._filter_data()
    assert controller.data_storage_instance.filtered_data.value.empty is False


def test_filter_data_with_buttonpress(
    make_input_widget: tuple[FilterController, QtBot]
):
    controller, qtbot = make_input_widget
    # need to set these things otherwise the filter output will be empty
    set_track_lenths(
        (0, 100),
        controller.widget.tracklenght_slider,
        controller.widget.min_tracklength_spinbox,
        controller.widget.max_tracklength_spinbox,
    )
    controller.data_storage_instance.columns.position_id = "Position"
    controller.data_storage_instance.columns.additional_filter_column = "None"
    controller.data_storage_instance.columns.x_column = "x"
    controller.data_storage_instance.columns.y_column = "y"
    controller.data_storage_instance.columns.object_id = "id"
    controller.data_storage_instance.columns.frame_column = "t"
    controller.data_storage_instance.columns.measurement_column = "m"
    controller.widget.position.addItem(str(1), 1)
    controller.widget.additional_filter_combobox.addItem(str(None), "None")
    controller.data_storage_instance.load_data(
        "src/arcos_gui/_tests/test_data/arcos_data.csv", trigger_callback=False
    )
    assert controller.data_storage_instance.filtered_data.value.empty
    qtbot.mouseClick(controller.widget.filter_input_data, Qt.LeftButton)
    assert controller.data_storage_instance.filtered_data.value.empty is False


def test_original_data_changed(make_input_widget: tuple[FilterController, QtBot]):
    controller, qtbot = make_input_widget
    assert controller.data_storage_instance.filtered_data.value.empty
    controller.data_storage_instance.columns.position_id = "Position"
    controller.data_storage_instance.columns.additional_filter_column = "Position"
    controller.data_storage_instance.columns.x_column = "x"
    controller.data_storage_instance.columns.y_column = "y"
    controller.data_storage_instance.columns.object_id = "id"
    controller.data_storage_instance.columns.frame_column = "t"
    controller.data_storage_instance.columns.measurement_column = "m"
    controller.data_storage_instance.load_data(
        "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )
    assert controller.data_storage_instance.filtered_data.value.empty is False
