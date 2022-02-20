import pandas as pd
import pytest
from arcos_gui._sample_data import load_sample_data
from arcos_gui._tests.test_arcos_widgets import columnpicker, stored_variables
from pandas.testing import assert_frame_equal
from qtpy.QtCore import Qt
from qtpy.QtTest import QTest


@pytest.fixture()
def dock_arcos_widget(make_napari_viewer):
    viewer = make_napari_viewer()
    mywidget = viewer.window.add_plugin_dock_widget(
        plugin_name="arcos-gui", widget_name="ARCOS Main Widget"
    )
    return viewer, mywidget[1]


def test_loading_sample_data(dock_arcos_widget):
    load_sample_data()
    test_data = stored_variables.data
    direct_test_data = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    # manually trigger button press
    QTest.mouseClick(columnpicker.Ok.native, Qt.LeftButton)
    assert columnpicker.frame.value == "t"
    assert columnpicker.track_id.value == "t"
    assert columnpicker.x_coordinates.value == "t"
    assert columnpicker.y_coordinates.value == "t"
    assert columnpicker.measurment.value == "t"
    assert columnpicker.field_of_view_id.value == "t"
    assert_frame_equal(test_data, direct_test_data)
