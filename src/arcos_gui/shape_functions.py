from copy import deepcopy

import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
from scipy.spatial.qhull import QhullError

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


# @profile
def recycle_palette(l_colors, length):
    ntimes = length // len(l_colors)
    remainder = length % len(l_colors)
    return l_colors * ntimes + l_colors[:remainder]


# @profile
def assign_color_id(df, palette, col_id="collid", col_color="color"):
    """
    Assign one color to each unique value in a column.
    Returns a DF with the assignment.
    """
    unique_id = df[col_id].unique()
    palette_val = recycle_palette(palette, len(unique_id))
    df_out = pd.DataFrame.from_dict({col_id: unique_id, col_color: palette_val})
    return df_out


# @profile
def make_shapes(
    df,
    col_id="index",
    col_x="axis-2",
    col_y="axis-1",
    col_t="axis-0",
    col_colors="color",
):
    """
    Take a pandas df with the coordinates of polygons vertices in "long"
    format and turn them into a list of numpy arrays, one for each polygon.
    Outputs a dictionary suitable for napari viewer.add_shapes
    """
    all_cols = [col_id, col_t, col_y, col_x, col_colors]

    # Drop irrelevant columns, check columns are ordered according to napari's format
    df = df[[c for c in df.columns if c in all_cols]]
    df_np = df[[col_id, col_t, col_y, col_x]].to_numpy(dtype=np.float64)
    out = {}
    # np array with collid polygons
    l_shapes = np.split(
        df_np[:, 1:], np.unique(df_np[:, 0:2], axis=0, return_index=True)[1][1:]
    )
    # The color is duplicated for each point in the polygon, take only first value
    out["face_color"] = (
        df[col_colors].iloc[df[[col_id, col_t]].drop_duplicates().index].to_list()
    )
    out["data"] = l_shapes
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


def calculate_convex_hull(array):
    try:
        if array.shape[0] < 3:
            return np.array([])
        hull = ConvexHull(array[:, 2:])
        array_out = array[hull.vertices]
        return array_out
    except QhullError:
        return np.array([])


def calculate_convex_hull_3d(array):
    try:
        if array.shape[0] < 4:
            return
        hull = ConvexHull(array[:, 2:])
        array_faces = hull.simplices
        return array_faces
    except QhullError:
        return


# @profile
def get_verticesHull(df, frame, colid, col_x, col_y):
    """From a set of point coordinates (XY), grouped by collid
    return an array containing arrays of vertices, one for each
    collective event. Also returns a list of colors, a unique
    one for each collective event.

    Args:
        df (pd.DataFrame): A dataframe with at least 4 columns
        containing the XY coordinates of a set of points aswell
        as frame and collective id columns.
        frame (st): Name of frame column in df.
        colid (str): Name of collective id column in df.
        col_x (str): Name of column x coordinate column in df.
        col_y (str): Name of column y coordinate column in df.
    """
    df = df.sort_values([colid, frame])
    array_txy = df[[colid, frame, col_y, col_x]].to_numpy()
    array_txy = array_txy[~np.isnan(array_txy).any(axis=1)]
    grouped_array = np.split(
        array_txy, np.unique(array_txy[:, 0:2], axis=0, return_index=True)[1][1:]
    )
    # map to grouped_array
    convex_hulls = [calculate_convex_hull(i) for i in grouped_array]
    color_ids = np.take(
        np.array(COLOR_CYCLE), [int(i[0, 0]) for i in convex_hulls], mode="wrap"
    )
    # color_ids = recycle_palette(COLOR_CYCLE, len(convex_hulls))
    out = np.array([i[:, 1:] for i in convex_hulls])
    return out, color_ids


# @profile
def make_surface_3d(df: pd.DataFrame, frame, col_x, col_y, col_z, colid):
    """
    Takes a dataframe and generates a tuple that can be used
    to add 3d convex hull with the napari add_surface function.
    Output has to be appended with empy vertices and surfaces for the
    timepoints where no surface should be drawn. Otherwise will
    result in a nontype subscription error.
    """
    dataFaces = []
    vertices_count = 0
    # sort needed for np.split
    df = df.sort_values([frame, colid])
    array_idtyxz = df[[colid, frame, col_y, col_x, col_z]].to_numpy()
    array_idtyxz = array_idtyxz[~np.isnan(array_idtyxz).any(axis=1)]
    # split array into list of arrays, one for each collid/timepoint combination
    grouped_array = np.split(
        array_idtyxz, np.unique(array_idtyxz[:, 0:2], axis=0, return_index=True)[1][1:]
    )
    # calc convex hull for every array in the list
    convex_hulls = [
        calculate_convex_hull_3d(i) for i in grouped_array if i.shape[0] > 3
    ]
    # generates color ids (integers for LUT in napari)
    color_ids = np.concatenate([i[:, 0].astype(np.int64) for i in grouped_array])
    out_vertices = array_idtyxz[:, 1:]
    # merge convex hull face list and shift indexes according to groups
    for i, value in enumerate(convex_hulls):
        dataFaces.append(np.add(value, vertices_count))
        vertices_count += len(grouped_array[i])
    out_faces = np.concatenate(dataFaces)
    return (out_vertices, out_faces, color_ids)


# @profile
def fix_3d_convex_hull(df, vertices, faces, colors, col_t):
    """Generate empty vertex and faces to fix napari subset error."""
    empty_vertex = []
    empty_faces = []
    empty_colors = []
    time_points = np.unique(vertices[:, 0])
    arr_size = vertices.shape[0]
    for i in df[col_t].unique():
        if i not in time_points:
            empty_vertex.append([i, 0, 0, 0])
            empty_faces.append([arr_size, arr_size, arr_size])
            arr_size = arr_size + 1
            empty_colors.append(0)

    surface_tuple_0 = np.concatenate((vertices, np.array(empty_vertex)), axis=0)
    surface_tuple_1 = np.concatenate((faces, np.array(empty_faces)), axis=0)
    surface_tuple_2 = np.concatenate((colors, np.array(empty_colors)), axis=0)

    return (surface_tuple_0, surface_tuple_1, surface_tuple_2)
