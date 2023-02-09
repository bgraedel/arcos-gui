"""Utility functoins to handle data processing."""

__author__ = """Benjamin Graedel"""
__email__ = "benjamin.graedel@unibe.ch"
__version__ = "0.0.7"


from arcos_gui.tools._config import (
    ARCOS_LAYERS,
    COLOR_CYCLE,
    OPERATOR_DICTIONARY,
    TAB20,
    measurement_math_options,
)
from arcos_gui.tools._image_sequence_export import MovieExporter
from arcos_gui.tools._plots import CollevPlotter, NoodlePlot, TimeSeriesPlots
from arcos_gui.tools._shape_functions import (
    fix_3d_convex_hull,
    get_bbox,
    get_bbox_3d,
    get_verticesHull,
    make_surface_3d,
    make_timestamp,
)
from arcos_gui.tools._ui_util_func import (
    get_layer_list,
    remove_layers_after_columnpicker,
    set_track_lenths,
)

__all__ = [
    "OPERATOR_DICTIONARY",
    "measurement_math_options",
    "COLOR_CYCLE",
    "TAB20",
    "ARCOS_LAYERS",
    "MovieExporter",
    "NoodlePlot",
    "CollevPlotter",
    "TimeSeriesPlots",
    "remove_layers_after_columnpicker",
    "get_layer_list",
    "set_track_lenths",
    "get_bbox",
    "get_bbox_3d",
    "fix_3d_convex_hull",
    "get_verticesHull",
    "make_surface_3d",
    "make_timestamp",
]
