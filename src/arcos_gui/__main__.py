import napari


def main(viewer: napari.Viewer):
    viewer, mywidget = viewer.window.add_plugin_dock_widget(
        plugin_name="arcos-gui", widget_name="ARCOS Main Widget"
    )
    return mywidget


if __name__ == "__main__":
    viewer = napari.Viewer()
    main(viewer)
    napari.run()
