import napari
from arcos_gui._arcos_widgets import columnpicker

viewer = napari.Viewer()
viewer, mywidget = viewer.window.add_plugin_dock_widget(
    plugin_name="arcos-gui", widget_name="ARCOS Main Widget"
)
file = "C:/Users/benig/Documents/\
tracks_191021_wt_curated_smoothedXYZ_interpolated_binarised.csv.gz"
mywidget.file_LineEdit.setText(file)
mywidget.open_columnpicker()

columnpicker.frame.value = "time"
columnpicker.x_coordinates.value = "posx"
columnpicker.y_coordinates.value = "posy"
columnpicker.track_id.value = "trackID"
columnpicker.z_coordinates.value = "posz"
columnpicker.measurment.value = "ERK_KTR"
# columnpicker.second_measurment.value = "objCytoRing_Intensity_MeanIntensity_imKTR"
columnpicker.field_of_view_id.value = "None"
columnpicker.measurement_math.value = "None"

napari.run()
