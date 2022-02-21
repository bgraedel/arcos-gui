import napari

viewer = napari.Viewer()
viewer.window.add_plugin_dock_widget(
    plugin_name="arcos-gui",
    widget_name="ARCOS Main Widget",
)


napari.run()
