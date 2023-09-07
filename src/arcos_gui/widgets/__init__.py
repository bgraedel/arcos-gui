"""Widgets."""

__author__ = """Benjamin Graedel"""
__email__ = "benjamin.graedel@unibe.ch"
__version__ = "0.0.7"

from ._arcos_widget import ArcosController
from ._bottom_bar_widget import BottombarController
from ._dialog_widgets import columnpicker
from ._exporting_widget import ExportController
from ._filter_widget import FilterController
from ._input_data_widget import InputdataController
from ._plot_widgets import collevPlotWidget, tsPlotWidget
from ._visualization_settings_widget import LayerpropertiesController

__all__ = [
    "ArcosController",
    "ExportController",
    "FilterController",
    "InputdataController",
    "LayerpropertiesController",
    "tsPlotWidget",
    "collevPlotWidget",
    "columnpicker",
    "BottombarController",
]
