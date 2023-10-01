"""Module contiaing serveral utility functions to prepare layer data tuples."""

from __future__ import annotations

from typing import Union

import numpy as np
import pandas as pd
from arcos_gui.tools import (
    ARCOS_LAYERS,
    COLOR_CYCLE,
    TAB20,
    fix_3d_convex_hull,
    get_verticesHull,
    make_surface_3d,
    reshape_by_input_string,
)


def prepare_all_cells_layer(
    df_all: pd.DataFrame,
    vColsCore: list[str | None],
    track_id_col: str | None,
    measurement_name: str,
    lut: str,
    min_max: list[float],
    size: float,
    axis_order: str | None = None,
) -> Union[tuple, None]:
    """Prepare all cells layer.

    Parameters
    ----------
    df_all : pd.DataFrame
        dataframe with all cells
    vColsCore : list
        list with core columns in dataframe
        order: [framecol, ycol, xcol, zcol(optional)]
    measurement_name : str
        name of measurement
    lut : str
        name of lut
    min_max : tuple
        min and max values for measurement
    size : float
        size of cells
    axis_order : str
        order of axis, e.g. 'tzyx', possible values: ['t', 'z', 'y', 'x'].
        Default: 'tzyx' for 3D data, 'tyx' for 2D data
    Returns
    -------
    all_cells_layer : dict
        dictionary with all cells layer
    """
    # np matrix with all cells
    df_all = df_all.copy()
    df_all.interpolate(method="linear", inplace=True)
    data_all_np = df_all[vColsCore].to_numpy()
    data_all_np = reshape_by_input_string(data_all_np, axis_order, vColsCore)

    if track_id_col:
        data_id_np = df_all[track_id_col].to_numpy()
    else:
        data_id_np = np.zeros(data_all_np.shape[0])

    # a dictionary with activities;
    # shown as a color code of all cells
    data_all_prop = {"act": df_all[measurement_name].astype(float), "id": data_id_np}
    # tuple to return layer as layer.data.tuple
    all_cells = (
        data_all_np,
        {
            "properties": data_all_prop,
            "edge_width": 0,
            "edge_color": "act",
            "face_color": "act",
            "face_colormap": lut,
            "face_contrast_limits": tuple(min_max),
            "size": size,
            "opacity": 1,
            "symbol": "disc",
            "name": ARCOS_LAYERS["all_cells"],
        },
        "points",
    )
    return all_cells


def prepare_active_cells_layer(
    df_bin: pd.DataFrame,
    vColsCore: list,
    measbin_col: str | None,
    size: float,
    axis_order: str | None = None,
    padd_time: bool = True,
) -> Union[tuple, None]:
    """Prepare active cells layer.

    Parameters
    ----------
    df_bin : pd.DataFrame
        dataframe with binarized data
    vColsCore : list
        list with core columns in dataframe
        order: [framecol, ycol, xcol, zcol(optional)]
    measbin_col : str
        name of binarized measurement column
    size : float
        size of cells
    axis_order : str
        order of axis, e.g. 'tzyx', possible values: ['t', 'z', 'y', 'x'].
        Default: 'tzyx' for 3D data, 'tyx' for 2D data.
    padd_time : bool
        if True, add a row with timepoint 0 if not present
        to make sure the timeaxis starts with 0
    Returns
    -------
    active_cells_layer : tuple
        tuple with active cells layer
    """

    # np matrix with acvtive cells; shown as black dots
    df_bin_filtered = df_bin[df_bin[measbin_col] > 0]
    datAct = df_bin_filtered[vColsCore].to_numpy()
    datAct = reshape_by_input_string(datAct, axis_order, vColsCore)

    # check if datAct starts with timepoint 0 if not add a row with timepoint 0
    if datAct[0][0] != 0 and padd_time:
        # take first timepoint and replace it with 0
        dat_tp0 = datAct[0].copy()
        dat_tp0[0] = 0
        datAct = np.insert(datAct, 0, dat_tp0, axis=0)
        shown_points = np.repeat(True, datAct.shape[0])
        shown_points[0] = False
    else:
        shown_points = np.repeat(True, datAct.shape[0])

    if datAct.size == 0:
        return None

    active_cells = (
        datAct,
        {
            "size": round(size / 2.5, 2),
            "edge_width": 0,
            "face_color": "black",
            "opacity": 1,
            "symbol": "disc",
            "name": ARCOS_LAYERS["active_cells"],
            "shown": shown_points,
        },
        "points",
    )

    return active_cells


def prepare_events_layer(
    df_coll: pd.DataFrame,
    vColsCore: list,
    size: float,
    axis_order: str | None = None,
    padd_time: bool = True,
) -> Union[tuple, None]:
    """Prepare events layer.

    Parameters
    ----------
    df_coll : pd.DataFrame
        dataframe with events
    vColsCore : list
        list with core columns in dataframe
        order: [framecol, ycol, xcol, zcol(optional)]
    size : float
        size of cells
    axis_order : str
        order of axis, e.g. 'tzyx', possible values: ['t', 'z', 'y', 'x'].
        Default: 'tzyx' for 3D data, 'tyx' for 2D data.
    padd_time : bool
        if True, add a row with timepoint 0 if not present
        to make sure the timeaxis starts with 0
    Returns
    -------
    coll_cells : tuple
        tuple with events layer
    """
    # np matrix with cells in collective events
    data_collevent_np = df_coll[vColsCore].to_numpy()
    data_collevent_np = reshape_by_input_string(
        data_collevent_np, axis_order, vColsCore
    )

    # create remaining layer.data.tuples
    np_clids = df_coll["collid"].to_numpy()

    if np_clids.size == 0:
        return None

    # check if datAct starts with timepoint 0 if not add a row with timepoint 0
    if data_collevent_np[0][0] != 0 and padd_time:
        dat_collev_0 = data_collevent_np[0].copy()
        dat_collev_0[0] = 0
        data_collevent_np = np.insert(data_collevent_np, 0, dat_collev_0, axis=0)
        np_clids = np.insert(np_clids, 0, 0, axis=0)
        shown_points = np.repeat(True, data_collevent_np.shape[0])
        shown_points[0] = False
    else:
        shown_points = np.repeat(True, data_collevent_np.shape[0])

    color_ids = np.take(np.array(COLOR_CYCLE), list(np_clids), mode="wrap")
    coll_cells = (
        data_collevent_np,
        {
            "face_color": color_ids,
            "size": round(size / 1.2, 2),
            "edge_width": 0,
            "opacity": 1,
            "name": ARCOS_LAYERS["collective_events_cells"],
            "shown": shown_points,
        },
        "points",
    )

    return coll_cells


def prepare_convex_hull_layer(
    df_filtered: pd.DataFrame,
    df_coll: pd.DataFrame,
    collid_name: str,
    vColsCore: list,
    axis_order: str | None = None,
) -> Union[tuple, None]:
    """Prepare convex hull layer.

    Parameters
    ----------
    df_filtered : pd.DataFrame
        dataframe with filtered data
    df_coll : pd.DataFrame
        dataframe with events
    collid_name : str
        name of collid column
    vColsCore : list
        list with core columns in dataframe
        order: [framecol, ycol, xcol, zcol(optional)]
    axis_order : str
        order of axis, e.g. 'tzyx', possible values: ['t', 'z', 'y', 'x'].
        Default: 'tzyx' for 3D data, 'tyx' for 2D data.

    Returns
    -------
    coll_hull : tuple
        tuple with convex hull layer
    """

    if df_coll[collid_name].to_numpy().size == 0:
        return None

    if len(vColsCore) == 3:
        # 2D data
        datChull, color_ids = get_verticesHull(
            df_coll,
            frame=vColsCore[0],
            colid=collid_name,
            col_x=vColsCore[2],
            col_y=vColsCore[1],
        )

        # order according to input string
        datChull = [
            reshape_by_input_string(i, input_string=axis_order, vColsCore=vColsCore)
            for i in datChull
        ]

        coll_events = (
            datChull,
            {
                "face_color": color_ids,
                "shape_type": "polygon",
                "text": None,
                "opacity": 0.5,
                "edge_color": "white",
                "edge_width": 0,
                "name": ARCOS_LAYERS["event_hulls"],
            },
            "shapes",
        )
        return coll_events

    # 3D data
    # reorder columns list to match axis order

    event_surfaces = make_surface_3d(
        df_coll,
        vColsCore=vColsCore,
        colid=collid_name,
        output_order=axis_order,
    )

    event_surfaces = fix_3d_convex_hull(
        df_filtered[vColsCore],
        event_surfaces[0],
        event_surfaces[1],
        event_surfaces[2],
        col_t=vColsCore[0],
    )

    coll_events = (
        event_surfaces,
        {
            "colormap": TAB20,
            "name": ARCOS_LAYERS["event_hulls"],
            "opacity": 0.5,
        },
        "surface",
    )
    return coll_events
