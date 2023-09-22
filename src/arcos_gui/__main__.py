"""Main module for napari plugin."""

import napari
from arcos_gui import open_plugin


def main():
    """Main function. Opens napari viewer and adds plugin dock widget."""
    viewer = napari.Viewer()
    open_plugin(viewer)
    napari.run()


if __name__ == "__main__":
    main()
