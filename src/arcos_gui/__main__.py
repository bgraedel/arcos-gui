"""Main module for napari plugin."""

from typing import TYPE_CHECKING

import napari

if TYPE_CHECKING:
    from . import _main_widget


def main(viewer: napari.Viewer):
    """Main function. Adds plugin dock widget to napari viewer."""
    mywidget: _main_widget.MainWindow
    viewer, mywidget = viewer.window.add_plugin_dock_widget(
        plugin_name="arcos-gui", widget_name="ARCOS Main Widget"
    )
    return mywidget


if __name__ == "__main__":
    viewer = napari.Viewer()
    main(viewer)
    napari.run()
