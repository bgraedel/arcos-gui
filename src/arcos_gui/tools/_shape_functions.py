from copy import deepcopy

import numpy as np
import pandas as pd
from arcos_gui.tools import ARCOS_LAYERS, COLOR_CYCLE
from scipy.spatial import ConvexHull, QhullError

# # Definitions and custom functions
# Color Cycle used throughout the plugin for collective events.
# Color values correspond to hex values of the matplotlib tab20
# colorscale

# text parameters for the timestamp
text_parameters = {
    "string": "{label}",
    "size": 12,
    "color": "white",
    "anchor": "center",
    "translation": [0, 0],
}


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
        "string": "{label}",
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
    """Calculates the convex hull for a 2d array of points.

    Parameters:
        array (np.ndarray): A 2d array of points with x and y coordinates.

    Returns (np.ndarray): If shape of input array can be used
    to calculate convex hull the vertices of the convex hull are returned.
    If shape is less, the points themselfs are returned.
    """
    # Todo check if there is a better way to check for coplanar
    # points rathern than using QhullError
    try:
        if array.shape[0] > 2:
            hull = ConvexHull(array[:, 2:])
            array_out = array[hull.vertices]
            return array_out
        if array.shape[0] == 2:
            return array
    except QhullError:
        return np.array([])


def calculate_convex_hull_3d(array):
    """Calculates the convex hull for a 3d array of points.

    Parameters:
        array (np.ndarray): A 2d array of points with x y and z coordinates.

    Returns (np.ndarray): If shape of input array can be used
    to calculate convex hull the vertices of the convex hull are returned.
    If shape is less, the points themselfs are returned.
    """
    if array.shape[0] > 3:
        hull = ConvexHull(array[:, 2:])
        array_faces = hull.simplices
        if array_faces.shape[0] != 0:
            return array_faces
    if array.shape[0] == 3:
        array_faces = np.array([[0, 1, 2]])
        return array_faces
    if array.shape[0] == 2:
        array_faces = np.array([[0, 1, 1]])
        return array_faces
    if array.shape[0] == 1:
        array_faces = np.array([[0, 0, 0]])
        return array_faces


def get_verticesHull(df, frame, colid, col_x, col_y):
    """Calculate convex hull for 2d collective events.

    Input dataframe is converted into a numpy array and split into groups
    according to unique collective ids.
    For each set array the convex hull is calculated.

    Parameters:
        df (pd.DataFrame): A dataframe with at least 4 columns
        containing the XY coordinates of a set of points aswell
        as frame and collective id columns.
        frame (str): Name of frame column in df.
        colid (str): Name of collective id column in df.
        col_x (str): Name of column x coordinate column in df.
        col_y (str): Name of column y coordinate column in df.

    Returns (np.ndarray,np.ndarray): Tuple containing arrays of vertices,
    one for each collective event. Array of colors, a unique
    one for each collective event.
    """
    df = df.sort_values([colid, frame])
    array_txy = df[[colid, frame, col_y, col_x]].to_numpy()
    array_txy = array_txy[~np.isnan(array_txy).any(axis=1)]
    grouped_array = np.split(
        array_txy, np.unique(array_txy[:, 0:2], axis=0, return_index=True)[1][1:]
    )
    # map to grouped_array
    convex_hulls = [calculate_convex_hull(i) for i in grouped_array if i.shape[0] > 1]
    color_ids = np.take(
        np.array(COLOR_CYCLE),
        [int(i[0, 0]) for i in convex_hulls if i.size > 0],
        mode="wrap",
    )
    # color_ids = recycle_palette(COLOR_CYCLE, len(convex_hulls))
    out = [i[:, 1:] for i in convex_hulls]
    return out, color_ids


# @profile
def make_surface_3d(
    df: pd.DataFrame, frame: str, col_x: str, col_y: str, col_z: str, colid: str
):
    """Calculate convex hull for 3d collective events.

    Input dataframe is converted into a numpy array and split into groups
    according to unique collective ids.
    For each set array the convex hull is calculated.
    A tuple that can be used to add 3d convex hull with the napari
    add_surface function is generated.
    Output has to be appended with empy vertices and surfaces for the
    timepoints where no surface should be drawn. Otherwise will
    result in a nontype subscription error.

    Parameters:
        df (pd.DataFrame): A dataframe with at least 4 columns
        containing the XY coordinates of a set of points aswell
        as frame and collective id columns.
        frame (str): Name of frame column in df.
        colid (str): Name of collective id column in df.
        col_x (str): Name of x coordinate column in df.
        col_y (str): Name of y coordinate column in df.
        col_z (str): Name of z coordinate column in df.

    Returns (tuple(np.ndarray, np.ndarray, np.ndarray)): Tuple that contains
    vertex coordinates, face indices and color ids
    """
    dataFaces = []
    vertices_count = 0
    # sort needed for np.split
    df = df.sort_values([colid, frame])
    array_idtyxz = df[[colid, frame, col_y, col_x, col_z]].to_numpy()
    array_idtyxz = array_idtyxz[~np.isnan(array_idtyxz).any(axis=1)]
    # split array into list of arrays, one for each collid/timepoint combination
    grouped_array = np.split(
        array_idtyxz, np.unique(array_idtyxz[:, 0:2], axis=0, return_index=True)[1][1:]
    )
    # calc convex hull for every array in the list
    convex_hulls = [calculate_convex_hull_3d(i) for i in grouped_array]
    # generates color ids (integers for LUT in napari)
    color_ids = np.concatenate([i[:, 0].astype(np.int64) for i in grouped_array])
    out_vertices = np.concatenate(grouped_array)[:, 1:]
    # merge convex hull face list and shift indexes according to groups
    for i, val in enumerate(convex_hulls):
        dataFaces.append(np.add(val, vertices_count))
        vertices_count += len(grouped_array[i])
    out_faces = np.concatenate(dataFaces)
    return (out_vertices, out_faces, color_ids)


# @profile
def fix_3d_convex_hull(df, vertices, faces, colors, col_t):
    """Generate empty vertex and faces to fix napari subset error.

    Parameters:
        df (pd.DataFrame): A dataframe used to calculate convex hulls.
        vertices (np.ndarray): vertex coordinates.
        faces (np.ndarray): Array containing face indices.
        colors (np.ndarray): Array containing color ids.
        col_t (str): String name of frame column in df.
    """
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

    empty_vertex = np.array(empty_vertex)
    empty_faces = np.array(empty_faces)
    empty_colors = np.array(empty_colors)

    if empty_vertex.size > 0:
        vertices = np.concatenate((vertices, empty_vertex), axis=0)
        faces = np.concatenate((faces, empty_faces), axis=0)
        colors = np.concatenate((colors, empty_colors), axis=0)
        return (vertices, faces, colors)
    else:
        return (vertices, faces, colors)


def calc_bbox(array: np.ndarray):
    """Calcualte the bounding box of input array.

    Parameters:
        array (np.ndarray): 2d array of coordinates
        for which to compute the bounding box.

    Returns (np.ndarray): 2d array of coordinates for the bounding box.
    """
    t = array[0, 0]
    pos_array = array[:, 1:]
    # 3d case
    if pos_array.shape[1] == 3:

        miny, minx, minz = np.min(pos_array, axis=0)
        maxy, maxx, maxz = np.max(pos_array, axis=0)
        return np.array(
            [
                [t, miny, minx, minz],
                [t, miny, minx, maxz],
                [t, miny, maxx, maxz],
                [t, miny, maxx, minz],
                [t, maxy, maxx, minz],
                [t, maxy, minx, minz],
                [t, maxy, minx, maxz],
                [t, maxy, maxx, maxz],
            ]
        )
    # 2d case
    miny, minx = np.min(pos_array, axis=0)
    maxy, maxx = np.max(pos_array, axis=0)
    return np.array(
        [[t, miny, minx], [t, miny, maxx], [t, maxy, maxx], [t, maxy, minx]]
    )


def get_bbox(
    df: pd.DataFrame, clid: int, frame: str, xcol: str, ycol: str, edge_size: float = 10
):
    """Get bounding box of dataframe in long format with position columns, for 2d case.

    Parameters:
        df (pd.DataFrame): dataframe to get bounding box form.
        frame (str): Name of frame column.
        xcol (str): X coordinate column.
        ycol (str): Y coordinate column.
        edge_size (float): Bounding Box edge_size, also used to calculate text size.

    Returns (nd.array, dict): Array that can be added to
    napari with add_shapes function aswell
    as dictionary that can be unpacked
    containing kwargs for shapes layer.
    """
    df = df.sort_values([frame])
    array_tpos = df[[frame, ycol, xcol]].to_numpy()
    array_tpos = array_tpos[~np.isnan(array_tpos).any(axis=1)]
    # split array into list of arrays, one for each collid/timepoint combination
    grouped_array = np.split(
        array_tpos, np.unique(array_tpos[:, 0], axis=0, return_index=True)[1][1:]
    )
    # calc bbox for every array in the list
    bbox = [calc_bbox(i) for i in grouped_array]
    text_size = edge_size * 2.5
    if text_size < 1:
        text_size = 1
    text_parameters = {
        "string": "Event Nbr: {label}",
        "size": text_size,
        "color": "white",
        "anchor": "upper_left",
        "translation": [-3, 0],
    }
    bbox_layer: dict = {}
    bbox_layer["properties"] = {}
    bbox_layer["properties"]["label"] = clid
    bbox_layer["text"] = text_parameters
    bbox_layer["face_color"] = "transparent"
    bbox_layer["edge_color"] = "red"
    bbox_layer["edge_width"] = edge_size
    bbox_layer["name"] = ARCOS_LAYERS["event_boundingbox"]

    return bbox, bbox_layer


def get_bbox_3d(df: pd.DataFrame, frame: str, xcol: str, ycol: str, zcol: str):
    """Get bounding box of dataframe in long format with position columns, for 3d case.

    Can be added to napari with the add_surfaces function.

    Parameters:
        df (pd.DataFrame): dataframe to get bounding box form.
        frame (str): Name of frame column.
        xcol (str): X coordinate column.
        ycol (str): Y coordinate column.
        zcol (str): Z coordinate column.

    Returns (nd.array, np.ndarray, np.ndarray): Tuple that
    can be added to napari with add_shapes
    function. Need to be passed on to the fix_3d_convex_hull
    function to avoid indexing errors in napari.
    """
    df = df.sort_values([frame])
    array_tpos = df[[frame, ycol, xcol, zcol]].to_numpy()
    array_tpos = array_tpos[~np.isnan(array_tpos).any(axis=1)]
    # split array into list of arrays, one for each collid/timepoint combination
    grouped_array = np.split(
        array_tpos, np.unique(array_tpos[:, 0], axis=0, return_index=True)[1][1:]
    )
    # calc bbox for every array in the list
    bbox = [calc_bbox(i) for i in grouped_array]
    dataFaces = []
    vertices_count = 0
    data_colors: np.ndarray = np.array([])
    # precalculated face indidec for a 3d bounding box
    face = np.array(
        [
            [3, 5, 4],
            [3, 5, 0],
            [3, 1, 2],
            [3, 1, 0],
            [7, 3, 2],
            [7, 3, 4],
            [6, 1, 0],
            [6, 5, 0],
            [6, 1, 2],
            [6, 7, 2],
            [6, 5, 4],
            [6, 7, 4],
        ]
    )
    for value in bbox:
        dataFaces.append(np.add(face, vertices_count))
        vertices_count += len(value)
    out_faces = np.concatenate(dataFaces)
    bbox_array = np.concatenate(bbox)
    data_colors = np.array([1 for i in range(bbox_array.shape[0])])
    return (bbox_array, out_faces, data_colors)
