import pandas as pd
import pytest
from arcos_gui._arcos_widgets import columnpicker, stored_variables
from arcos_gui._sample_data import load_sample_data
from pandas.testing import assert_frame_equal


@pytest.mark.xfail
def test_loading_sample_data(make_napari_viewer, qtbot):
    viewer = make_napari_viewer()
    viewer.window.add_plugin_dock_widget(
        plugin_name="arcos-gui", widget_name="ARCOS Main Widget"
    )
    load_sample_data()
    # arcos_widget.callback_file_Linedit_text(str(
    #     Path("src/arcos_gui/_tests/test_data/arcos_data.csv"))
    # )
    test_data = stored_variables.data
    direct_test_data = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
    assert columnpicker.frame.value == "t"
    assert columnpicker.track_id.value == "id"
    assert columnpicker.x_coordinates.value == "x"
    assert columnpicker.y_coordinates.value == "y"
    assert columnpicker.measurment.value == "m"
    assert columnpicker.field_of_view_id.value == "Position"
    assert_frame_equal(test_data, direct_test_data)
