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
    make_timestamp,
)


def prepare_all_cells_layer(
    df_all: pd.DataFrame,
    vColsCore,
    track_id_col: str,
    measurement_name: str,
    lut: str,
    min_max: tuple,
    size: float,
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

    Returns
    -------
    all_cells_layer : dict
        dictionary with all cells layer
    """

    # np matrix with all cells
    df_all = df_all.copy()
    df_all.interpolate(method="linear", inplace=True)
    datAll = df_all[vColsCore].to_numpy()
    datID = df_all[track_id_col].to_numpy()

    # a dictionary with activities;
    # shown as a color code of all cells
    datAllProp = {"act": df_all[measurement_name].astype(float), "id": datID}
    # tuple to return layer as layer.data.tuple
    all_cells = (
        datAll,
        {
            "properties": datAllProp,
            "edge_width": 0,
            "edge_color": "act",
            "face_color": "act",
            "face_colormap": lut,
            "face_contrast_limits": min_max,
            "size": size,
            "edge_width": 0,
            "opacity": 1,
            "symbol": "disc",
            "name": ARCOS_LAYERS["all_cells"],
        },
        "points",
    )
    return all_cells


def prepare_active_cells_layer(
    df_bin: pd.DataFrame, vColsCore: list, measbin_col: str, size: float
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

    Returns
    -------
    active_cells_layer : tuple
        tuple with active cells layer
    """

    # np matrix with acvtive cells; shown as black dots
    datAct = df_bin[df_bin[measbin_col] > 0][vColsCore].to_numpy()

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
        },
        "points",
    )

    return active_cells


def prepare_events_layer(
    df_coll: pd.DataFrame, vColsCore: list, size: float
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

    Returns
    -------
    coll_cells : tuple
        tuple with events layer
    """
    # np matrix with cells in collective events
    datColl = df_coll[vColsCore].to_numpy()

    # create remaining layer.data.tuples
    np_clids = df_coll["collid"].to_numpy()

    if np_clids.size == 0:
        return None

    color_ids = np.take(np.array(COLOR_CYCLE), [i for i in np_clids], mode="wrap")
    coll_cells = (
        datColl,
        {
            "face_color": color_ids,
            "size": round(size / 1.2, 2),
            "edge_width": 0,
            "opacity": 1,
            "name": ARCOS_LAYERS["collective_events_cells"],
        },
        "points",
    )

    return coll_cells


def prepare_convex_hull_layer(
    df_filtered: pd.DataFrame,
    df_coll: pd.DataFrame,
    collid_name: str,
    vColsCore: list,
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

    event_surfaces = make_surface_3d(
        df_coll,
        frame=vColsCore[0],
        colid=collid_name,
        col_x=vColsCore[2],
        col_y=vColsCore[1],
        col_z=vColsCore[3],
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


def prepare_timestamp_layer(
    viewer, start_time, step_time, position, prefix, suffix, size, x_shift, y_shift
):

    kw_timestamp = make_timestamp(
        viewer, start_time, step_time, prefix, suffix, position, size, x_shift, y_shift
    )

    time_stamp_layer = (
        kw_timestamp["data"],
        {
            "properties": kw_timestamp["properties"],
            "face_color": kw_timestamp["face_color"],
            "edge_color": kw_timestamp["edge_color"],
            "shape_type": kw_timestamp["shape_type"],
            "text": kw_timestamp["text"],
            "opacity": kw_timestamp["opacity"],
            "name": ARCOS_LAYERS["timestamp"],
        },
        "shapes",
    )

    return time_stamp_layer
