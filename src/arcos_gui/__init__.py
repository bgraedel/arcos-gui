"""Arcos GUI Plugin for Napari."""

__version__ = "0.0.7"


from napari.utils.notifications import show_info

from ._loading_functions import load_dataframe, open_plugin

show_info("Loading Plugin")

__all__ = ["open_plugin", "load_dataframe"]
