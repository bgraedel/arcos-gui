from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from arcos_gui.processing import DataStorage
from arcos_gui.tools import set_track_lenths
from arcos_gui.widgets import FilterDataWidget
from qtpy.QtCore import Qt

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


@pytest.fixture()
def make_input_widget(qtbot, make_napari_viewer) -> tuple[FilterDataWidget, QtBot]:
    viewer = make_napari_viewer()
    ds = DataStorage()
    widget = FilterDataWidget(viewer, ds)
    qtbot.addWidget(widget)
    return widget, qtbot


def test_open_widget(make_input_widget: tuple[FilterDataWidget, QtBot]):
    input_data_widget, _ = make_input_widget
    assert input_data_widget


def test_ranged_slider_widget(make_input_widget: tuple[FilterDataWidget, QtBot]):
    widget, qtbot = make_input_widget
    assert widget.tracklenght_slider


def test_ranged_slider_connection_to_spinboxes(
    make_input_widget: tuple[FilterDataWidget, QtBot]
):
    widget, qtbot = make_input_widget

    # set the range of the slider and spinboxes
    set_track_lenths(
        (0, 20),
        widget.tracklenght_slider,
        widget.min_tracklength_spinbox,
        widget.max_tracklength_spinbox,
    )
    widget.tracklenght_slider.setValue((0, 20))
    assert widget.min_tracklength_spinbox.value() == 0
    assert widget.max_tracklength_spinbox.value() == 20

    widget.tracklenght_slider.setValue((5, 15))
    assert widget.min_tracklength_spinbox.value() == 5
    assert widget.max_tracklength_spinbox.value() == 15

    widget.min_tracklength_spinbox.setValue(10)
    assert widget.tracklenght_slider.value() == (10, 15)

    widget.max_tracklength_spinbox.setValue(10)
    assert widget.tracklenght_slider.value() == (10, 10)


def test_default_visible(make_input_widget: tuple[FilterDataWidget, QtBot]):
    widget, qtbot = make_input_widget
    assert widget.tracklenght_slider.isVisibleTo(widget) is True
    assert widget.tracklength_label.isVisibleTo(widget) is True
    assert widget.min_tracklength_spinbox.isVisibleTo(widget) is True
    assert widget.max_tracklength_spinbox.isVisibleTo(widget) is True
    assert widget.position.isVisibleTo(widget) is False
    assert widget.position_label.isVisibleTo(widget) is False
    assert widget.additional_filter_combobox.isVisibleTo(widget) is False
    assert widget.additional_filter_combobox_label.isVisibleTo(widget) is False


def test_toggle_visible(make_input_widget: tuple[FilterDataWidget, QtBot]):
    widget, qtbot = make_input_widget
    assert widget.position.isVisibleTo(widget) is False
    assert widget.position_label.isVisibleTo(widget) is False
    assert widget.additional_filter_combobox.isVisibleTo(widget) is False
    assert widget.additional_filter_combobox_label.isVisibleTo(widget) is False
    widget._set_position_visible()
    assert widget.position.isVisibleTo(widget) is True
    assert widget.position_label.isVisibleTo(widget) is True
    widget._set_additional_filter_visible()
    assert widget.additional_filter_combobox.isVisibleTo(widget) is True
    assert widget.additional_filter_combobox_label.isVisibleTo(widget) is True
    widget._set_defaults()
    assert widget.position.isVisibleTo(widget) is False
    assert widget.position_label.isVisibleTo(widget) is False
    assert widget.additional_filter_combobox.isVisibleTo(widget) is False
    assert widget.additional_filter_combobox_label.isVisibleTo(widget) is False


def test_filter_no_data(
    make_input_widget: tuple[FilterDataWidget, QtBot], capsys, make_napari_viewer
):
    widget, qtbot = make_input_widget
    # make viewer for show info function of napari
    make_napari_viewer()
    widget._filter_data()
    captured = capsys.readouterr()
    assert captured.out == "INFO: No data loaded, or not loaded correctly\n"
    assert widget.data_storage_instance.filtered_data.value.empty


def test_filter_data(make_input_widget: tuple[FilterDataWidget, QtBot]):
    widget, qtbot = make_input_widget
    # need to set these things otherwise the filter output will be empty
    set_track_lenths(
        (0, 100),
        widget.tracklenght_slider,
        widget.min_tracklength_spinbox,
        widget.max_tracklength_spinbox,
    )
    widget.data_storage_instance.columns.position_id = "Position"
    widget.data_storage_instance.columns.additional_filter_column = "None"
    widget.data_storage_instance.columns.x_column = "x"
    widget.data_storage_instance.columns.y_column = "y"
    widget.data_storage_instance.columns.object_id = "id"
    widget.data_storage_instance.columns.frame_column = "t"
    widget.data_storage_instance.columns.measurement_column = "m"
    widget.position.addItem(str(1), 1)
    widget.additional_filter_combobox.addItem(str(None), "None")
    widget.data_storage_instance.load_data(
        "src/arcos_gui/_tests/test_data/arcos_data.csv", trigger_callback=False
    )
    assert widget.data_storage_instance.filtered_data.value.empty
    widget._filter_data()
    assert widget.data_storage_instance.filtered_data.value.empty is False


def test_filter_data_with_buttonpress(
    make_input_widget: tuple[FilterDataWidget, QtBot]
):
    widget, qtbot = make_input_widget
    # need to set these things otherwise the filter output will be empty
    set_track_lenths(
        (0, 100),
        widget.tracklenght_slider,
        widget.min_tracklength_spinbox,
        widget.max_tracklength_spinbox,
    )
    widget.data_storage_instance.columns.position_id = "Position"
    widget.data_storage_instance.columns.additional_filter_column = "None"
    widget.data_storage_instance.columns.x_column = "x"
    widget.data_storage_instance.columns.y_column = "y"
    widget.data_storage_instance.columns.object_id = "id"
    widget.data_storage_instance.columns.frame_column = "t"
    widget.data_storage_instance.columns.measurement_column = "m"
    widget.position.addItem(str(1), 1)
    widget.additional_filter_combobox.addItem(str(None), "None")
    widget.data_storage_instance.load_data(
        "src/arcos_gui/_tests/test_data/arcos_data.csv", trigger_callback=False
    )
    assert widget.data_storage_instance.filtered_data.value.empty
    qtbot.mouseClick(widget.filter_input_data, Qt.LeftButton)
    assert widget.data_storage_instance.filtered_data.value.empty is False


def test_original_data_changed(make_input_widget: tuple[FilterDataWidget, QtBot]):
    widget, qtbot = make_input_widget
    assert widget.data_storage_instance.filtered_data.value.empty
    widget.data_storage_instance.columns.position_id = "Position"
    widget.data_storage_instance.columns.additional_filter_column = "Position"
    widget.data_storage_instance.columns.x_column = "x"
    widget.data_storage_instance.columns.y_column = "y"
    widget.data_storage_instance.columns.object_id = "id"
    widget.data_storage_instance.columns.frame_column = "t"
    widget.data_storage_instance.columns.measurement_column = "m"
    widget.data_storage_instance.load_data(
        "src/arcos_gui/_tests/test_data/arcos_data.csv"
    )
    assert widget.data_storage_instance.filtered_data.value.empty is False
