from unittest.mock import Mock

import pandas as pd
import pytest
from arcos_gui.processing import DataStorage
from arcos_gui.widgets import BottomBarWidget
from pytestqt.qtbot import QtBot
from qtpy import QtCore, QtGui


@pytest.fixture
def data_storage_instance():
    return Mock(spec=DataStorage)


@pytest.fixture
def bottom_bar_widget(data_storage_instance: DataStorage, qtbot: QtBot):
    bb_widget = BottomBarWidget(data_storage_instance)
    qtbot.addWidget(bb_widget)
    return bb_widget


def test_bottom_bar_widget_initialization(bottom_bar_widget):
    assert isinstance(bottom_bar_widget, BottomBarWidget)


def test_update_event_counter(
    bottom_bar_widget: BottomBarWidget, data_storage_instance: DataStorage
):
    # Test with empty dataframe
    df = pd.DataFrame()
    data_storage_instance.arcos_stats.value = df
    bottom_bar_widget.update_event_counter()
    assert bottom_bar_widget.collev_number_display.intValue() == 0

    # Test with non-empty dataframe
    df = pd.DataFrame({"collid": [1, 2, 2, 3, 3, 3]})
    data_storage_instance.arcos_stats.value = df
    bottom_bar_widget.update_event_counter()
    assert bottom_bar_widget.collev_number_display.intValue() == 3


def test_update_help_pressed(bottom_bar_widget, mocker):
    mocker.patch("PyQt5.QtCore.QUrl")
    mocker.patch("PyQt5.QtGui.QDesktopServices.openUrl")
    bottom_bar_widget.arcos_help_button.click()
    QtGui.QDesktopServices.openUrl.assert_called_once_with(
        QtCore.QUrl("https://bgraedel.github.io/arcos-gui/Usage/")
    )
