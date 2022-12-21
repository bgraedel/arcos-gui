import operator

from napari.utils import Colormap

OPERATOR_DICTIONARY = {
    "Divide": (operator.truediv, "Measurement_Ratio"),
    "Multiply": (operator.mul, "Measurement_Product"),
    "Add": (operator.add, "Measurement_Sum"),
    "Subtract": (operator.sub, "Measurement_Difference"),
}

measurement_math_options = list(OPERATOR_DICTIONARY.keys())
measurement_math_options.append("None")


COLOR_CYCLE = [
    "#1f77b4",
    "#aec7e8",
    "#ff7f0e",
    "#ffbb78",
    "#2ca02c",
    "#98df8a",
    "#d62728",
    "#ff9896",
    "#9467bd",
    "#c5b0d5",
    "#8c564b",
    "#c49c94",
    "#e377c2",
    "#f7b6d2",
    "#7f7f7f",
    "#c7c7c7",
    "#bcbd22",
    "#dbdb8d",
    "#17becf",
    "#9edae5",
]

TAB20 = Colormap(COLOR_CYCLE, "tab20", interpolation="zero")

ARCOS_LAYERS = {
    "all_cells": "All Cells",
    "active_cells": "Active Cells",
    "collective_events_cells": "Collective Events Cells",
    "event_hulls": "Collective Events",
    "event_boundingbox": "Event Bounding Box",
    "timestamp": "Timestamp",
}
