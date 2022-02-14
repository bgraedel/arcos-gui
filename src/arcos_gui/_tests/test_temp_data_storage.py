import pytest
import pandas as pd
from arcos_gui import temp_data_storage

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

def test_update_what_to_run(storage, diff_variables):
    data = diff_variables['what_to_run_test_list'][0]
    storage.clear_what_to_run()
    storage.update_what_to_run(data)
    new_data = storage.arcos_what_to_run
    assert (new_data[0] == data)



