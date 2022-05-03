import numpy as np
import pandas as pd
import pytest
from arcos_gui.shape_functions import (
    fix_3d_convex_hull,
    get_verticesHull,
    make_surface_3d,
)
from numpy.testing import assert_equal


@pytest.fixture
def data_frame_2d():
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


@pytest.fixture
def data_frame_3d():
    clid = [1 for i in range(0, 9)]
    clid.append(np.nan)
    d = {
        "time": [1, 1, 1, 1, 1, 1, 1, 1, 1, 2],
        "Y": [1, 1, 1, 1, 2, 2, 2, 2, 1.5, 5],
        "X": [1, 1, 2, 2, 1, 1, 2, 2, 1.5, 5],
        "Z": [1, 2, 1, 2, 1, 2, 1, 2, 1.5, 5],
        "collid": clid,
    }
    df = pd.DataFrame(data=d)
    return df


def test_get_verticesHull(data_frame_2d):
    hulls, colors = get_verticesHull(
        df=data_frame_2d, frame="time", colid="collid", col_x="X", col_y="Y"
    )
    d_np = np.array([[5, 0], [10, 5], [6, 9]])
    assert_equal(d_np, hulls[0][:, 1:])


def test_make_surface_3d(data_frame_3d):
    df_in = data_frame_3d[data_frame_3d["collid"] == 1]
    hulls = make_surface_3d(df_in, "time", "X", "Y", "Z", "collid")
    cube_vertices = np.array(
        [
            [6, 2, 0],
            [6, 4, 0],
            [5, 4, 0],
            [5, 1, 0],
            [5, 6, 4],
            [5, 6, 7],
            [3, 2, 0],
            [3, 1, 0],
            [3, 6, 2],
            [3, 6, 7],
            [3, 5, 1],
            [3, 5, 7],
        ]
    )
    assert_equal(hulls[0], df_in.iloc[:, 0:4])
    assert_equal(hulls[1], cube_vertices)
    assert_equal(hulls[2], np.repeat(1, 9))


def test_fix_3d_convex_hull(data_frame_3d):
    df_in = data_frame_3d
    hulls = make_surface_3d(df_in, "time", "X", "Y", "Z", "collid")
    cube_vertices = np.array(
        [
            [6, 2, 0],
            [6, 4, 0],
            [5, 4, 0],
            [5, 1, 0],
            [5, 6, 4],
            [5, 6, 7],
            [3, 2, 0],
            [3, 1, 0],
            [3, 6, 2],
            [3, 6, 7],
            [3, 5, 1],
            [3, 5, 7],
            [9, 9, 9],
        ]
    )
    df_out_true = df_in.iloc[:-1, 0:4]
    df_out_true.loc[len(df_out_true.index)] = [2, 0, 0, 0]
    color_true = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 0])
    hulls_fixed = fix_3d_convex_hull(df_in, hulls[0], hulls[1], hulls[2], "time")
    print("\n", df_in, hulls_fixed[0], hulls_fixed[1], hulls_fixed[2])
    assert_equal(hulls_fixed[0], df_out_true)
    assert_equal(hulls_fixed[1], cube_vertices)
    assert_equal(hulls_fixed[2], color_true)
