from arcos_gui.shape_functions import COLOR_CYCLE, assign_color_id, get_verticesHull
import pytest
import pandas as pd
from pandas.testing import assert_frame_equal

@pytest.fixture
def data_frame():
    col_2= list(range(5,10))
    col_2.extend(list(range(10,5,-1)))
    d= {'col1': list(range(0,10)), 'col2': col_2}
    df = pd.DataFrame(data=d)
    return df

def test_assign_color_id(data_frame):
    color_id = assign_color_id(data_frame, palette=COLOR_CYCLE, col_id='col1')
    color_list = color_id['color'].to_list()
    assert (color_list == COLOR_CYCLE)

def test_get_verticesHull(data_frame):
    hulls = get_verticesHull(data_frame, 'col1', 'col2')
    d = [[0,5],[9,6],[5,10]]
    cols = ['col1', 'col2']
    df = pd.DataFrame(data=d, columns=cols)
    assert_frame_equal(df,hulls)