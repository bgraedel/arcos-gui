from copy import deepcopy

import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull, QhullError

# # Definitions and custom functions

COLOR_CYCLE = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]

text_parameters = {
    "text": "{label}",
    "size": 12,
    "color": "white",
    "anchor": "center",
    "translation": [0, 0],
}


def recycle_palette(l_colors, length):
    ntimes = length // len(l_colors)
    remainder = length % len(l_colors)
    return l_colors * ntimes + l_colors[:remainder]


def assign_color_id(df, palette, col_id="collid", col_color="color"):
    """
    Assign one color to each unique value in a column.
    Returns a DF with the assignment.
    """
    unique_id = df[col_id].unique()
    palette_val = recycle_palette(palette, len(unique_id))
    df_out = pd.DataFrame.from_dict({col_id: unique_id, col_color: palette_val})
    return df_out


def make_shapes(
    df,
    col_id="index",
    col_x="axis-2",
    col_y="axis-1",
    col_t="axis-0",
    col_colors="color",
    col_text=None,
):
    """
    Take a pandas df with the coordinates of polygons vertices in "long"
    format and turn them into a list of numpy arrays, one for each polygon.
    Outputs a dictionary suitable for napari viewer.add_shapes
    """
    all_cols = [col_id, col_t, col_y, col_x, col_colors]
    if col_text:
        all_cols.append(col_text)
    # Drop irrelevant columns, check columns are ordered according to napari's format
    df = df[df.columns.intersection(all_cols)]
    df = df.reindex(columns=all_cols)

    out = {}
    # List of 2 tuples (index, df_subset)
    l_shapes = [tup[1] for tup in list(df.groupby(col_id))]
    # The color is duplicated for each point in the polygon, take only first value
    out["face_color"] = [dff[col_colors].values[0] for dff in l_shapes]
    if col_text:
        out["properties"] = {}
        out["properties"]["label"] = [dff[col_text].values[0] for dff in l_shapes]
    l_shapes = [
        dff.drop(columns=[col_id, col_colors, col_text], errors="ignore")
        for dff in l_shapes
    ]
    out["data"] = [dff.to_numpy() for dff in l_shapes]
    return out


def make_timestamp(
    viewer,
    start_time=0,
    step_time=1,
    prefix="T =",
    suffix="frame",
    position="upper_left",
    size=12,
    x_shift=12,
    y_shift=0,
):
    """
    Create a timestamp displayed in the viewer.
    This is done by creating a dummy shape layer
    and annotating it with the current time.
    """
    anchors = ["upper_right", "upper_left", "lower_right", "lower_left", "center"]
    if position not in anchors:
        raise ValueError(f'"position" must be one of: {anchors}')

    text_parameters_tmstp = {
        "text": "{label}",
        "size": size,
        "color": "white",
        "anchor": position,
        "translation": [x_shift, y_shift],
    }
    out = {}
    rgt, rgy, rgx = deepcopy(viewer.dims.range)
    # Napari uses float64 for dims
    maxx, maxy, maxt = rgx[1], rgy[1], rgt[1] - 1
    # Points to the corners of the image at each frame
    corners = [
        np.array(
            [
                [t, np.float64(0), np.float64(0)],
                [t, np.float64(0), maxx],
                [t, maxy, maxx],
                [t, maxy, np.float64(0)],
            ]
        )
        for t in np.arange(maxt + 1).astype("float64")
    ]
    out["properties"] = {}
    timestamp = [start_time + step * step_time for step in range(int(maxt + 1))]
    out["properties"]["label"] = [f"{prefix} {str(i)} {suffix}" for i in timestamp]
    out["data"] = corners
    # Fully transparent white because just want the text, not the shape
    out["face_color"] = np.repeat("#ffffff00", len(corners))
    out["edge_color"] = np.repeat("#ffffff00", len(corners))
    out["shape_type"] = "rectangle"
    out["text"] = text_parameters_tmstp
    out["opacity"] = 1
    return out


def get_verticesHull(df, col_x, col_y):
    """From a set of point coordinates (XY), return the points
    coordinates which form the vertices of the convex hull.

    Args:
        df (pd.DataFrame): A dataframe with at least 2 columns
        containing the XY coordinates of a set of points.
    """

    df_xy = df[[col_x, col_y]].copy(deep=True)
    df_xy.dropna(inplace=True)
    # try except statement to test if Qhullerror is thrown
    # returns column names as a list of df_xy
    # instead of pd.DataFrame to check if correct columns were selected
    try:
        if df_xy.shape[0] >= 3:
            hull = ConvexHull(df_xy)
            df_out = df_xy.iloc[hull.vertices]
            # Add back the columns that do not contain the XY coords
            df_out = pd.merge(df_out, df, how="left")
        elif df_xy.shape[0] == 2:
            df_out = df
        else:
            df_out = pd.DataFrame(columns=list(df.columns))
        return df_out

    except QhullError:
        return df_xy.columns


def format_verticesHull(df, col_time, col_x, col_y, col_collid):
    """
    Format the output of get_verticesHull() applied to group

    Args:
        df (pd.DataFrame): A DataFrame with the coordinates
        of the vertices of collective events.
    """
    all_cols = [col_time, col_x, col_y, col_collid]
    df = df.loc[:, all_cols]
    df["shape-type"] = "polygon"
    df["index"] = df.groupby([col_time, col_collid]).ngroup()
    df["vertex-index"] = df.groupby("index").cumcount()
    df.rename(
        columns={
            col_time: "axis-0",
            col_y: "axis-1",
            col_x: "axis-2",
            col_collid: "collid",
        },
        inplace=True,
    )

    df = df.reindex(
        columns=[
            "index",
            "shape-type",
            "vertex-index",
            "axis-0",
            "axis-1",
            "axis-2",
            "collid",
        ]
    )
    return df
