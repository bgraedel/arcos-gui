import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from arcos_gui import temp_data_storage
from arcos_gui import arcos_module

@pytest.fixture
def storage():
    test_storage = temp_data_storage.data_storage()
    return test_storage

@pytest.fixture
def diff_variables():
    d= {'col1': [1, 2], 'col2': [3, 4]}
    test_dict ={"data": pd.DataFrame(data=d),
    "layer_test_list": ["layer_1", "layer_2"],
    "arcos": object,
    "what_to_run_test_list": ["all"],
    "test_pos": 1,
    "test_pos_list": [1,2,3],
    "test_minmax": (1,2)}
    return test_dict

def test_pos(storage):
    pos = 1
    storage.update_current_pos(pos)
    new_pos = storage.get_current_pos()
    assert (new_pos == pos)

def test_data(storage,diff_variables):
    data = diff_variables['data']
    storage.update_data(data)
    new_data = storage.get_data()
    assert_frame_equal(new_data,data)

def test_dataframe(storage,diff_variables):
    data = diff_variables['data']
    storage.update_dataframe(data)
    new_data = storage.get_dataframe()
    assert_frame_equal(new_data,data)

def test_data_merged(storage,diff_variables):
    data = diff_variables['data']
    storage.update_data_merged(data)
    new_data = storage.get_data_merged()
    assert_frame_equal(new_data,data)

def test_update_arcos_object(storage,diff_variables):
    obj = diff_variables['arcos']
    storage.update_arcos_object(obj)
    new_obj = storage.get_arcos_object()
    assert obj == new_obj

def test_update_ts_data(storage, diff_variables):
    data = diff_variables['data']
    storage.update_ts_data(data)
    new_data = storage.get_ts_data()
    assert_frame_equal(new_data,data)

def test_update_what_to_run(storage, diff_variables):
    data = diff_variables['what_to_run_test_list'][0]
    storage.clear_what_to_run()
    storage.update_what_to_run(data)
    new_data = storage.get_what_to_run()
    assert (new_data[0] == data)

def test_append_layer_names(storage, diff_variables):
    data = diff_variables['layer_test_list']
    storage.append_layer_names(data[0])
    storage.append_layer_names(data[1])
    storage.remove_layer_names(data[0])
    new_data = storage.get_layer_names()
    assert (new_data[0] == data[1])

def test_update_positions_list(storage, diff_variables):
    data = diff_variables['test_pos_list']
    storage.update_positions_list(data)
    new_data = storage.get_positions_list()
    assert (new_data == data)

def test_update_color_min_max(storage, diff_variables):
    data = diff_variables['test_minmax']
    storage.update_color_min_max(data)
    new_data = storage.get_color_min_max()
    assert (new_data == data)

def test_update_lut(storage):
    lut = "viridis"
    storage.update_lut(lut)
    new_lut = storage.get_lut()
    assert (lut == new_lut)




