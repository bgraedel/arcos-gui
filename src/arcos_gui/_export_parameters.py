import os
from datetime import datetime

import pandas as pd


def get_parmeters(arcos_gui_object):
    filepath = arcos_gui_object.file_LineEdit.text()
    arcos_parameters = {
        "filepath": filepath,
        "interpolate_state": arcos_gui_object.interpolate_meas.isChecked(),
        "clip_state": arcos_gui_object.clip_meas.isChecked(),
        "clip_low_value": arcos_gui_object.clip_low.value(),
        "clip_high_value": arcos_gui_object.clip_high.value(),
        "bias_method": arcos_gui_object.bias_method.currentText(),
        "smooth_k": arcos_gui_object.smooth_k.value(),
        "bias_k": arcos_gui_object.bias_k.value(),
        "polyDeg": arcos_gui_object.polyDeg.value(),
        "bin_peak_threshold": arcos_gui_object.bin_peak_threshold.value(),
        "bin_threshold": arcos_gui_object.bin_threshold.value(),
        "neighbourhood_size": arcos_gui_object.neighbourhood_size.value(),
        "min_clustersize": arcos_gui_object.min_clustersize.value(),
        "min_dur": arcos_gui_object.min_dur.value(),
        "total_event_size": arcos_gui_object.total_event_size.value(),
        "convex_hull_checkbox": arcos_gui_object.add_convex_hull_checkbox.isChecked(),
    }
    arcos_parameters_df = pd.DataFrame(data=arcos_parameters)
    return arcos_parameters_df


def get_columns(arcos_gui_object):
    filepath = arcos_gui_object.file_LineEdit.text()
    column_names = {
        "file": filepath,
        "frame": arcos_gui_object.frame,
        "track_id": arcos_gui_object.track_id,
        "x_coordinates": arcos_gui_object.x_coordinates,
        "y_coordinates": arcos_gui_object.y_coordinates,
        "z_coordinates": arcos_gui_object.z_coordinates,
        "first_measurement": arcos_gui_object.first_measurement,
        "second_measurement": arcos_gui_object.second_measurement,
        "field_of_view_id": arcos_gui_object.field_of_view_id,
        "additional_filter_column_name": arcos_gui_object.additional_filter_column_name,
    }

    column_df = pd.DataFrame(data=column_names)
    return column_df


def save_data(
    data: pd.DataFrame, filepath: str, filename: str = "arcos_gui_parameters"
):
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y_%H:%M:%S")
    filename_time = f"{filename}_{dt_string}"
    full_path = os.path.join(filepath, filename_time)
    data.to_csv(full_path)
