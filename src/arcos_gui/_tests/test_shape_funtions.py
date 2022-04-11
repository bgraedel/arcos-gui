import numpy as np
import pandas as pd
import pytest
from arcos_gui.shape_functions import (
    COLOR_CYCLE,
    assign_color_id,
    format_verticesHull,
    get_verticesHull,
    make_shapes,
)
from numpy.testing import assert_equal
from pandas.testing import assert_frame_equal


@pytest.fixture
def data_frame():
    col_2 = list(range(5, 10))
    col_2.extend(list(range(10, 5, -1)))
    d = {
        "time": [1 for i in range(0, 10)],
        "X": list(range(0, 10)),
        "Y": col_2,
        "collid": [1 for i in range(0, 10)],
    }
    df = pd.DataFrame(data=d)
    return df


def test_assign_color_id(data_frame):
    color_id = assign_color_id(data_frame, palette=COLOR_CYCLE, col_id="X")
    color_list = color_id["color"].to_list()
    assert color_list == COLOR_CYCLE


def test_get_verticesHull(data_frame):
    hulls = get_verticesHull(data_frame, "X", "Y")
    d = [[0, 5], [9, 6], [5, 10]]
    cols = ["X", "Y"]
    df = pd.DataFrame(data=d, columns=cols)
    assert_frame_equal(df, hulls.iloc[:, [1, 2]].reset_index(drop=True))


def test_format_verticesHull(data_frame):
    hulls = get_verticesHull(data_frame, "X", "Y")
    datChull = format_verticesHull(hulls, "time", "X", "Y", "collid")
    d_2 = [
        [0, "polygon", 0, 1, 5, 0, 1],
        [0, "polygon", 1, 1, 6, 9, 1],
        [0, "polygon", 2, 1, 10, 5, 1],
    ]
    cols_2 = [
        "index",
        "shape-type",
        "vertex-index",
        "axis-0",
        "axis-1",
        "axis-2",
        "collid",
    ]
    df = pd.DataFrame(data=d_2, columns=cols_2)
    assert_frame_equal(df, datChull)


def test_make_shapes(data_frame):
    d_2 = [
        [0, "polygon", 0, 1, 5, 0, 1],
        [0, "polygon", 1, 1, 6, 9, 1],
        [0, "polygon", 2, 1, 10, 5, 1],
    ]
    cols_2 = [
        "index",
        "shape-type",
        "vertex-index",
        "axis-0",
        "axis-1",
        "axis-2",
        "collid",
    ]
    datChull = pd.DataFrame(data=d_2, columns=cols_2)
    datChull_color = assign_color_id(datChull, COLOR_CYCLE)
    datChull = datChull.merge(datChull_color, on="collid")
    shapes = make_shapes(datChull)
    dict_exp = {
        "face_color": ["#1f77b4"],
        "data": [np.array([[1, 5, 0], [1, 6, 9], [1, 10, 5]])],
    }
    print(shapes, "\n")
    print(dict_exp)
    assert_equal(shapes, dict_exp)
