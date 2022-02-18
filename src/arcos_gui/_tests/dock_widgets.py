import napari

viewer = napari.Viewer()
mywidget = viewer.window.add_plugin_dock_widget(
    plugin_name="arcos-gui", widget_name="ARCOS Main Widget"
)
mywidget[1]()


napari.run()
