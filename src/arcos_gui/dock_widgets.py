import napari
from arcos_gui._arcos_widgets import columnpicker

viewer = napari.Viewer()
viewer, mywidget = viewer.window.add_plugin_dock_widget(
    plugin_name="arcos-gui", widget_name="ARCOS Main Widget"
)
file = "C:/Users/benig/Downloads/objNuclei_1line_clean_tracks_wA3_fov01.csv.gz"
mywidget.file_LineEdit.setText(file)
mywidget.open_columnpicker()

columnpicker.frame.value = "Image_Metadata_T"
columnpicker.x_coordinates.value = "objNuclei_Location_Center_X"
columnpicker.y_coordinates.value = "objNuclei_Location_Center_Y"
columnpicker.track_id.value = "track_id"
columnpicker.z_coordinates.value = "None"
columnpicker.measurment.value = "objNuclei_Intensity_MeanIntensity_imKTR"
columnpicker.second_measurment.value = "objCytoRing_Intensity_MeanIntensity_imKTR"
columnpicker.field_of_view_id.value = "Image_Metadata_Site"
columnpicker.measurement_math.value = "Divide"

napari.run()
