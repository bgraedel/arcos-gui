
__version__ = "0.0.1"


from napari.utils.notifications import show_info

show_info("Loading Plugin")

from ._arcos_widgets import change_cell_colors, add_timestamp, arcos_widget, filter_widget,filepicker, CollevPlotter, TimeSeriesPlots

# __all__ = ["ExampleQWidget", "example_function_widget", "print_hello", "open_filepicker"]
