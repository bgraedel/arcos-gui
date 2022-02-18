# imports dependencies
from copy import deepcopy
from os import sep
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from magicgui import magic_factory, magicgui
from magicgui.widgets import ProgressBar
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from napari import current_viewer
from napari.types import LayerDataTuple
from napari.utils.notifications import show_info
from qtpy.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from scipy.stats import gaussian_kde

# local imports
from .arcos_module import ARCOS, process_input
from .export_movie import iterate_over_frames, resize_napari
from .magic_guis import columnpicker, show_timestamp_options, timestamp_options
from .shape_functions import (
    COLOR_CYCLE,
    assign_color_id,
    format_verticesHull,
    get_verticesHull,
    make_shapes,
    make_timestamp,
)
from .temp_data_storage import data_storage

if TYPE_CHECKING:
    import napari.viewer

# define some variables
TOFFSET = 0

# initalize class
stored_variables = data_storage()


# init function for magic_factory add_timestamp
def on_ts_init(new_widget):
    new_widget.Set_Timestamp_Options.changed.connect(show_timestamp_options)


@magic_factory(
    widget_init=on_ts_init,
    call_button="Add Timestamp",
    Set_Timestamp_Options={"widget_type": "PushButton"},
)
def add_timestamp(
    viewer: "napari.viewer.Viewer", Set_Timestamp_Options=False
) -> LayerDataTuple:
    """Button to add timestamp"""
    if list(viewer.layers) and viewer.layers.ndim > 2:
        if "Timestamp" in stored_variables.layer_names:
            viewer.layers.remove("Timestamp")
        kw_timestamp = make_timestamp(
            viewer,
            start_time=timestamp_options.start_time.value,
            step_time=timestamp_options.step_time.value,
            prefix=timestamp_options.prefix.value,
            suffix=timestamp_options.suffix.value,
            position=timestamp_options.position.value,
            size=timestamp_options.size.value,
            x_shift=timestamp_options.x_shift.value,
            y_shift=timestamp_options.y_shift.value,
        )
        time_stamp = (
            kw_timestamp["data"],
            {
                "properties": kw_timestamp["properties"],
                "face_color": kw_timestamp["face_color"],
                "edge_color": kw_timestamp["edge_color"],
                "shape_type": kw_timestamp["shape_type"],
                "text": kw_timestamp["text"],
                "opacity": kw_timestamp["opacity"],
                "name": "Timestamp",
            },
            "shapes",
        )
        return [time_stamp]
    else:
        show_info("No Layers to add Timestamp to")


def on_export_data_init(new_widget):
    """init function for the export data widget"""
    new_widget.Export_ARCOS_as_csv.changed.connect(show_output_csv_folder)
    new_widget.Export_movie.changed.connect(show_output_movie_folder)


@magic_factory(
    widget_init=on_export_data_init,
    call_button=False,
    Export_ARCOS_as_csv={"widget_type": "PushButton"},
    Export_movie={"widget_type": "PushButton"},
)
def export_data(Export_ARCOS_as_csv=False, Export_movie=False):
    """Widget to export csv and movie data"""


def on_arcos_widget_init(widget):
    # get current viewer
    viewer = current_viewer()

    def close_columnpicker():
        """
        listens for PushButton Press in columnpicker widget
        and gets the chosen columns to be stored inside of a dictionnary
        as a parameter of the columnpicker widget. Additionally,
        determines minimum and maximum tracklength and unique positoins
        for filtering the TimeSeries later on via sliders in filter_widget
        and updates these variables in the stored_variables object.
        Function also initializes callbacks for when new layers are inserted
        and removes layers once new data gets loaded.
        """
        # populate column dictionnary
        frame = columnpicker.frame.value
        track_id = columnpicker.track_id.value
        x_coordinates = columnpicker.x_coordinates.value
        y_coordinates = columnpicker.y_coordinates.value
        measurment = columnpicker.measurment.value
        field_of_view_id = columnpicker.field_of_view_id.value
        columnpicker.close()
        columnpicker.dicCols.value = {
            "frame": frame,
            "x_coordinates": x_coordinates,
            "y_coordinates": y_coordinates,
            "track_id": track_id,
            "measurment": measurment,
            "field_of_view_id": field_of_view_id,
        }

    def set_positions():
        # get unique positions for filter_widget
        if columnpicker.dicCols.value["field_of_view_id"] != "None":
            positions = list(
                stored_variables.data[
                    columnpicker.dicCols.value["field_of_view_id"]
                ].unique()
            )
        else:
            positions = ["None"]

        if columnpicker.field_of_view_id == "None":
            widget.position.visible = False
        else:
            widget.position.visible = True

        # set positions in filter widget, filter data
        widget.position.choices = []
        widget.position.choices = positions
        stored_variables.positions = positions
        stored_variables.current_position = widget.position.value

        # hides position choice if no position column exists in the raw data
        # i.e. during columnpicker position was set to None.
        # Also hides it if there is only one position available.
        # Updates everytime when new data is read in
        if len(widget.position.choices) == 1:
            widget.position.hide()
        else:
            widget.position.show()

    def get_tracklengths():
        """
        Groups filtered data by track_id and
        returns minimum and maximum tracklenght.
        Updates min and max tracklenght in the arcos_widget.
        """
        data = stored_variables.data
        if not data.empty:
            if columnpicker.dicCols.value["field_of_view_id"] != "None":
                track_lenths = stored_variables.data.groupby(
                    [
                        columnpicker.dicCols.value["field_of_view_id"],
                        columnpicker.dicCols.value["track_id"],
                    ]
                ).size()
            else:
                track_lenths = stored_variables.data.groupby(
                    [columnpicker.dicCols.value["track_id"]]
                ).size()
            minmax = (min(track_lenths), max(track_lenths))

            widget.min_track_length.min = minmax[0]
            widget.min_track_length.max = minmax[1]
            widget.max_track_length.min = minmax[0]
            widget.max_track_length.max = minmax[1]
            widget.min_track_length.value = minmax[0]
            widget.max_track_length.value = minmax[1]

    def remove_layers_after_columnpicker():
        """
        removes existing arcos layers before loading new data
        """
        for layer in [
            "coll cells",
            "coll events",
            "active cells",
            "all_cells",
            "Timestamp",
        ]:
            if layer in stored_variables.layer_names:
                viewer.layers.remove(layer)
                stored_variables.layer_names.remove(layer)

    def add_new_layers_list(event):
        """
        adds newly inserted layers to the list stored in the stored_variables object
        """
        for idx, layer in enumerate(viewer.layers):
            if layer.name not in stored_variables.layer_names:
                stored_variables.layer_names.append(layer.name)

        positions = sorted(stored_variables.positions)
        current_pos = stored_variables.current_position
        for i in positions:
            if i is not None:
                widget.position.del_choice(str(i))

        widget.position.choices = positions

        widget.position.value = current_pos

    def remove_old_layers_list(event):
        """
        removes layers that are not present in napari
        anymore form the list the stored_variables object
        """
        for idx, layer in enumerate(viewer.layers):
            if layer.name not in [x.name for x in viewer.layers]:
                stored_variables.layer_names.remove(layer.name)

        positions = sorted(stored_variables.positions)
        for i in positions:
            if i is not None:
                widget.position.del_choice(str(i))
        current_pos = stored_variables.current_position
        widget.position.choices = positions

        widget.position.value = current_pos

    def update_what_to_run_variable():
        """
        updates a 'what to run' variable in the stored_variables object,
        that is used in arcos_widget to check if what to run
        when certain field have updated values
        """
        stored_variables.update_what_to_run("all")

    def open_columnpicker():
        """
        Take a filename and if it is a csv file,
        open it and stores it in the stored_variables_object.
        Shows columnpicker dialog.
        """
        columns = columnpicker.frame.choices
        column_keys = columnpicker.dicCols.value.keys()
        for i in column_keys:
            for index, j in enumerate(columns):
                getattr(columnpicker, i).del_choice(str(j))
        csv_file = widget.filename.value
        if str(csv_file).endswith(".csv"):
            stored_variables.data = pd.read_csv(csv_file)
            columns = list(stored_variables.data.columns)
            columnpicker.frame.choices = columns
            columnpicker.track_id.choices = columns
            columnpicker.x_coordinates.choices = columns
            columnpicker.y_coordinates.choices = columns
            columnpicker.measurment.choices = columns
            columnpicker.field_of_view_id.choices = columns
            columnpicker.field_of_view_id.set_choice("None", "None")
            columnpicker.show()
        else:
            show_info("Not a csv file")

    def filter_data():
        """
        Used to filter the input datato contain a single position.
        filter options also include minimum and maximum tracklength.
        Allows for rescaling of measurment variable.
        """
        # gets raw data read in by arcos_widget from stored_variables object
        # and columns from columnpicker value
        in_data = process_input(
            df=stored_variables.data, columns=columnpicker.dicCols.value
        )
        if (
            stored_variables.data.empty
            or columnpicker.dicCols.value["field_of_view_id"]
            == columnpicker.dicCols.value["measurment"]
        ):
            show_info("No data loaded, or not loaded correctly")
        else:
            # if the position column was not chosen in columnpicker,
            # dont filter by position
            if columnpicker.dicCols.value["field_of_view_id"] != "None":
                # hast to be done before .filter_tracklenght otherwise code could break
                # if track ids are not unique to positions
                in_data.filter_position(widget.position.value)
            # filter by tracklenght
            in_data.filter_tracklength(
                widget.min_track_length.value, widget.max_track_length.value
            )
            # option to rescale the measurment column
            in_data.rescale_measurment(rescale_factor=widget.rescale_measurment.value)
            # option to set frame interval
            in_data.frame_interval(widget.frame_interval.value)

            dataframe = in_data.return_pd_df()

            # get min and max values
            if not dataframe.empty:
                max_meas = max(dataframe[columnpicker.dicCols.value["measurment"]])
                min_meas = min(dataframe[columnpicker.dicCols.value["measurment"]])
                stored_variables.min_max = (min_meas, max_meas)
            stored_variables.dataframe = dataframe
            stored_variables.current_position = widget.position.value
            show_info("Data Filtered!")

        # several functions to update the 'what to run' variable in stored_variables

    def update_what_to_run_all():
        stored_variables.update_what_to_run("all")

    def update_what_to_run_tracking():
        stored_variables.update_what_to_run("from_tracking")

    def update_what_to_run_filtering():
        stored_variables.update_what_to_run("from_filtering")

    def toggle_clip_meas_visibility():
        widget.clip_low.visible = not widget.clip_low.visible
        widget.clip_high.visible = not widget.clip_high.visible

    def toggle_bias_method_parameter_visibility():
        """
        based on the seleciton of bias method:
        shows or hides the appropriate options in the widget
        """
        if widget.bias_method.value == "runmed":
            widget.smooth_k.visible = True
            widget.polyDeg.visible = False
            widget.bias_k.visible = True
            widget.bin_peak_threshold.visible = True
            widget.bin_threshold.visible = True

        if widget.bias_method.value == "lm":
            widget.smooth_k.visible = True
            widget.polyDeg.visible = True
            widget.bias_k.visible = False
            widget.bin_peak_threshold.visible = True
            widget.bin_threshold.visible = True

        if widget.bias_method.value == "none":
            widget.smooth_k.visible = True
            widget.polyDeg.visible = False
            widget.bias_k.visible = False
            widget.bin_peak_threshold.visible = False
            widget.bin_threshold.visible = True

    def set_point_size():
        """
        updates values in lut mapping sliders
        """
        data = stored_variables.data
        if not data.empty:
            minx = min(data[columnpicker.dicCols.value["x_coordinates"]])
            maxx = max(data[columnpicker.dicCols.value["x_coordinates"]])
            miny = min(data[columnpicker.dicCols.value["y_coordinates"]])
            maxy = max(data[columnpicker.dicCols.value["y_coordinates"]])

            max_coord_diff = max(maxx - minx, maxy - miny)
            widget.point_size.value = (
                0.75482
                + 0.00523857 * max_coord_diff
                + 9.0618311e-6 * max_coord_diff ** 2
            )

    def reset_contrast():
        """
        updates values in lut mapping sliders
        """
        min_max = stored_variables.min_max
        # change slider values
        widget.max_contrast.max = min_max[1]
        widget.max_contrast.min = min_max[0]
        widget.min_contrast.max = min_max[1]
        widget.min_contrast.min = min_max[0]
        widget.max_contrast.value = widget.max_contrast.max
        widget.min_contrast.value = widget.min_contrast.min

    def update_lut():
        """
        updates LUT choice in stored_variables
        """
        stored_variables.lut = widget.LUT.value

    # hook up callbacks to execute LUT and point functions
    widget.ResetLUT.changed.connect(reset_contrast)
    widget.LUT.changed.connect(update_lut)

    # callback for updating 'what to run' in stored_variables object
    widget.clip_low.changed.connect(update_what_to_run_all)
    widget.clip_high.changed.connect(update_what_to_run_all)
    widget.smooth_k.changed.connect(update_what_to_run_all)
    widget.interval_type.changed.connect(update_what_to_run_all)
    widget.bias_k.changed.connect(update_what_to_run_all)
    widget.bin_threshold.changed.connect(update_what_to_run_all)
    widget.neighbourhood_size.changed.connect(update_what_to_run_tracking)
    widget.bin_peak_threshold.changed.connect(update_what_to_run_all)
    widget.min_clustersize.changed.connect(update_what_to_run_tracking)
    widget.min_clustersize.changed.connect(update_what_to_run_tracking)
    widget.min_duration.changed.connect(update_what_to_run_filtering)
    widget.total_event_size.changed.connect(update_what_to_run_filtering)
    widget.clip_measurments.changed.connect(toggle_clip_meas_visibility)

    # callback for chaning available options of bias method
    widget.bias_method.changed.connect(toggle_bias_method_parameter_visibility)

    # callback for updating what to run in arcos_widget
    widget.filename.changed.connect(open_columnpicker)

    # callback for updating several variables after OK press in columnpicker widget
    columnpicker.Ok.changed.connect(close_columnpicker)
    columnpicker.Ok.changed.connect(set_positions)
    columnpicker.Ok.changed.connect(get_tracklengths)
    columnpicker.Ok.changed.connect(remove_layers_after_columnpicker)

    # callbackfor filtering data
    widget.filter_input_data.changed.connect(filter_data)

    # reset what to run
    widget.filter_input_data.changed.connect(update_what_to_run_variable)

    # reset contrast and point size
    widget.filter_input_data.changed.connect(reset_contrast)
    widget.filter_input_data.changed.connect(set_point_size)

    # callback for removing and adding layers to a list of layers
    viewer.layers.events.inserted.connect(add_new_layers_list)
    viewer.layers.events.removed.connect(remove_old_layers_list)

    def run():
        widget()

    widget.Update_ARCOS.changed.connect(run)

    def change_cell_colors():
        """
        function to update lut and corresponding lut mappings
        """
        viewer = current_viewer()
        if "all_cells" in stored_variables.layer_names:
            viewer.layers["all_cells"].face_colormap = widget.LUT.value
            viewer.layers["all_cells"].face_contrast_limits = (
                widget.min_contrast.value,
                widget.max_contrast.value,
            )
            viewer.layers["all_cells"].refresh_colors()

    def change_cell_size():
        """
        function to update size of points and shapes layers:
        "all_cells, "active cells", "coll cells" and "coll events"
        """
        if "all_cells" in stored_variables.layer_names:
            viewer.layers["all_cells"].size = widget.point_size.value
            viewer.layers["active cells"].size = round(widget.point_size.value / 2.5, 2)

        if "coll cells" in stored_variables.layer_names:
            viewer.layers["coll cells"].size = round(widget.point_size.value / 1.7, 2)
            viewer.layers["coll events"].edge_width = widget.point_size.value / 5
            viewer.layers["coll events"].refresh()

    widget.max_contrast.changed.connect(change_cell_colors)
    widget.min_contrast.changed.connect(change_cell_colors)
    widget.LUT.changed.connect(change_cell_colors)
    widget.point_size.changed.connect(change_cell_size)
    widget.called.connect(change_cell_size)


@magic_factory(
    widget_init=on_arcos_widget_init,
    call_button=False,
    filename={"label": "Choose CSV file:"},
    position={"choices": ["None"], "visible": False},
    min_track_length={"widget_type": "Slider", "min": 0, "max": 10},
    max_track_length={"widget_type": "Slider", "min": 0, "max": 10},
    filter_input_data={"widget_type": "PushButton", "value": False},
    spacer={"widget_type": "Label", "name": ""},
    arcos_label={"widget_type": "Label", "name": ""},
    interval_type={"choices": ["fixed", "var"]},
    bias_method={"choices": ["runmed", "lm", "none"]},
    polyDeg={"visible": False},
    clip_low={"min": 0, "max": 1, "step": 0.001, "tooltip": "Measurment in Quantiles"},
    clip_high={"min": 0, "max": 1, "step": 0.001, "tooltip": "Measurment in Quantiles"},
    bin_peak_threshold={"min": 0, "step": 0.01},
    bin_threshold={"min": 0, "step": 0.01},
    neighbourhood_size={"min": 0, "max": 10000},
    Progress={"min": 0, "step": 4, "max": 40, "value": 0},
    Update_ARCOS={"widget_type": "PushButton", "value": False},
    spacer_2={"widget_type": "Label", "name": ""},
    max_contrast={"widget_type": "FloatSlider", "max": 1},
    min_contrast={"widget_type": "FloatSlider", "max": 1},
    point_size={"min": 0},
    ResetLUT={"widget_type": "PushButton"},
    LUT={"widget_type": "ComboBox", "choices": stored_variables.colormaps},
)
def arcos_widget(
    viewer: "napari.viewer.Viewer",
    filename=Path(),
    position="None",
    rescale_measurment=1,
    frame_interval=1,
    min_track_length=0,
    max_track_length=10,
    filter_input_data=False,
    spacer="",
    arcos_label="ARCOS Parameters",
    interpolate_measurments=True,
    clip_measurments=True,
    clip_low=0.001,
    clip_high=0.999,
    interval_type="fixed",
    bias_method="runmed",
    smooth_k=1,
    polyDeg=1,
    bias_k=25,
    bin_peak_threshold=0.2,
    bin_threshold=0.1,
    neighbourhood_size=40,
    min_clustersize=5,
    min_duration=3,
    total_event_size=30,
    Progress: ProgressBar = 0,
    Update_ARCOS=False,
    spacer_2="",
    LUT="RdYlBu_r",
    max_contrast: float = 1,
    min_contrast: float = 0,
    point_size: float = 5,
    ResetLUT=False,
) -> LayerDataTuple:

    """
    widget allowing a user to import a csv file, filter this file,
    choose arcos parameters, choose LUT mappings aswell as shape sizes
    When called runs arcos.
    Returns a list of napari.types.LayerDataTuble to add or update layers.

    Returned layers are:
    all_cells:
    returns color coded points of all cells filtered by the filter_widget.
    Color code represents measurment active_cells: returns black dots,
    representing cells determined as being active by arcos binarise measurment function

    active cells:
    points representing cells that have been classified as being active
    by the arcos binarization approach.

    coll cells:
    returns black crosses representing cells that are according
    to the calculation done by arcos part of a collective event

    coll events:
    returns polycons representing the convex hulls of individual collective
    events, color coded accoring to a color_cycle attribute
    """
    # checks if this part of the function has to be run,
    # depends on the parameters changed in arcos widget
    if stored_variables.dataframe.empty:
        show_info("No Data Loaded, Use arcos_widget to load and filter data first")
    else:
        if "all" in stored_variables.arcos_what_to_run:

            # sets Progressbar to 0
            arcos_widget.Progress.value = 0
            # create arcos object, run arcos
            arcos = ARCOS(stored_variables.dataframe, columnpicker.dicCols.value)
            arcos.create_arcosTS(
                interval=1, inter_type=arcos_widget.interval_type.value
            )

            arcos_widget.Progress.increment()

            # if corresponding checkbox was selected run interpolate measurments
            if arcos_widget.interpolate_measurments:
                arcos.interpolate_measurements()

            # if corresponding checkbock was selected run clip_measuremnts
            if arcos_widget.clip_measurments:
                arcos.clip_measurements(
                    clip_low=arcos_widget.clip_low.value,
                    clip_high=arcos_widget.clip_high.value,
                )

            arcos_widget.Progress.increment()

            # updates arcos object in the stored_variables object
            stored_variables.arcos = arcos

            # binarize data and update ts variable in stored_variables
            # update from where to run
            ts = arcos.bin_measurements(
                arcos_widget.bias_method.value,
                arcos_widget.smooth_k.value,
                arcos_widget.bias_k.value,
                arcos_widget.bin_peak_threshold.value,
                arcos_widget.bin_threshold.value,
                arcos_widget.polyDeg.value,
                return_dataframe=True,
            )
            stored_variables.ts_data = ts
            stored_variables.update_what_to_run("from_tracking")

            arcos_widget.Progress.increment()

        # if statement checks if this part of the function has to be run
        # depends on the parameters changed in arcos widget
        if "from_tracking" in stored_variables.arcos_what_to_run:
            arcos = stored_variables.arcos  # type: ignore
            ts = stored_variables.ts_data
            # if active cells were detected, run this
            if 1 in ts["meas.bin"].values:
                # track collective events
                arcos.track_events(
                    arcos_widget.neighbourhood_size.value,
                    arcos_widget.min_clustersize.value,
                )

                arcos_widget.Progress.value = 12

            # if no active cells were detected remove previous layer,
            # since this does not correspont to current widget parameters
            else:
                # check if layers exist, if yes, remove them
                if "active cells" in stored_variables.layer_names:
                    viewer.layers.remove("active cells")
                    viewer.layers.remove("all_cells")
                    stored_variables.layer_names.remove("active cells")
                    stored_variables.layer_names.remove("all_cells")
                    arcos_widget.Progress.value = 40
                show_info("No active Cells detected, consider adjusting parameters")

            # update stored variables
            stored_variables.arcos = arcos
            stored_variables.update_what_to_run("from_filtering")

        # depending on the parameters changed in arcos widget
        if "from_filtering" in stored_variables.arcos_what_to_run:

            # set progressbar value
            arcos_widget.Progress.value = 20

            # get most recent data from stored_variables
            arcos = stored_variables.arcos  # type: ignore
            ts = stored_variables.ts_data

            # if no data show info to run arcos first and set the progressbar to 100%
            if arcos is None:
                show_info("No data available, run arcos first")
                arcos_widget.Progress.value = 40

            # if cells were classifed as being active (represented by a 1)
            # filter tracked events acording to chosen parameters
            elif 1 in ts["meas.bin"].values:

                # set return varaibles to check which layers have to be created
                return_collev = False
                return_points = True
                out = arcos.filter_tracked_events(
                    arcos_widget.min_duration.value,
                    arcos_widget.total_event_size.value,
                    as_pd_dataframe=True,
                )

                arcos_widget.Progress.increment()

                # update stats variable
                arcos.calculate_stats()

                arcos_widget.Progress.increment()

                # merge tracked and original data
                merged_data = pd.merge(
                    ts,
                    out[
                        [
                            columnpicker.dicCols.value["frame"],
                            columnpicker.dicCols.value["track_id"],
                            "collid",
                        ]
                    ],
                    how="left",
                    on=[
                        columnpicker.dicCols.value["frame"],
                        columnpicker.dicCols.value["track_id"],
                    ],
                )
                stored_variables.data_merged = merged_data

                # subtract timeoffset
                merged_data[columnpicker.dicCols.value["frame"]] -= TOFFSET

                # column list
                vColsCore = [
                    columnpicker.dicCols.value["frame"],
                    columnpicker.dicCols.value["y_coordinates"],
                    columnpicker.dicCols.value["x_coordinates"],
                ]

                # np matrix with all cells
                datAll = merged_data[vColsCore].to_numpy()

                # a dictionary with activities;
                # shown as a color code of all cells

                datAllProp = {
                    "act": merged_data[columnpicker.dicCols.value["measurment"]]
                }

                # np matrix with acvtive cells; shown as black dots
                datAct = merged_data[merged_data["meas.bin"] > 0][vColsCore].to_numpy()

                active_cells = (
                    datAct,
                    {
                        "size": round(point_size / 2.5, 2),
                        "edge_width": 0,
                        "face_color": "black",
                        "opacity": 1,
                        "symbol": "disc",
                        "name": "active cells",
                    },
                    "points",
                )

                # np matrix with cells in collective events; shown as black pluses
                datColl = merged_data[~np.isnan(merged_data["collid"])][
                    vColsCore
                ].to_numpy()

                # tuple to return layer as layer.data.tuple
                all_cells = (
                    datAll,
                    {
                        "properties": datAllProp,
                        "edge_width": 0,
                        "edge_color": "act",
                        "face_color": "act",
                        "face_colormap": stored_variables.lut,
                        "face_contrast_limits": stored_variables.min_max,
                        "size": point_size,
                        "edge_width": 0,
                        "opacity": 1,
                        "symbol": "disc",
                        "name": "all_cells",
                    },
                    "points",
                )

                arcos_widget.Progress.increment()

                # check if collective events were detected and add layer,
                # if yes calculate convex hulls for collective events
                if datColl.size != 0:
                    # convex hulls
                    df_gb = merged_data[~np.isnan(merged_data["collid"])].groupby(
                        [columnpicker.dicCols.value["frame"], "collid"]
                    )
                    datChull = df_gb.apply(
                        get_verticesHull,
                        col_x=columnpicker.dicCols.value["x_coordinates"],
                        col_y=columnpicker.dicCols.value["y_coordinates"],
                    ).reset_index(drop=True)
                    # check if error Qhullerror was raised in get_verticesHull
                    # shows column info that was passed on to the function
                    if type(datChull) == list:
                        show_info(
                            f"Error in convex hull creation, \
                            correct x/y columns selected? \n x, y columns: {datChull}"
                        )

                    datChull = format_verticesHull(
                        datChull,
                        columnpicker.dicCols.value["frame"],
                        columnpicker.dicCols.value["x_coordinates"],
                        columnpicker.dicCols.value["y_coordinates"],
                        "collid",
                    )
                    datChull["axis-0"] -= TOFFSET

                    df_collid_colors = assign_color_id(
                        df=datChull,
                        palette=COLOR_CYCLE,
                    )

                    datChull = datChull.merge(df_collid_colors, on="collid")

                    # creates actuall shapes
                    kw_shapes = make_shapes(datChull, col_text="collid")

                    # create remaining layer.data.tuples
                    coll_cells = (
                        datColl,
                        {
                            "face_color": "black",
                            "size": round(point_size / 1.7, 2),
                            "edge_width": 0,
                            "opacity": 0.75,
                            "symbol": "x",
                            "name": "coll cells",
                        },
                        "points",
                    )
                    coll_events = (
                        kw_shapes["data"],
                        {
                            "face_color": kw_shapes["face_color"],
                            "properties": kw_shapes["properties"],
                            "shape_type": "polygon",
                            "text": None,
                            "opacity": 0.5,
                            "edge_color": "white",
                            "edge_width": round(point_size / 5, 2),
                            "name": "coll events",
                        },
                        "shapes",
                    )
                    return_collev = True

                    arcos_widget.Progress.increment()
                else:
                    # check if layers exit, if yes remove them
                    if "coll cells" in stored_variables.layer_names:
                        viewer.layers.remove("coll cells")
                        viewer.layers.remove("coll events")
                        stored_variables.layer_names.remove("coll cells")
                        stored_variables.layer_names.remove("coll events")
                    show_info(
                        "No collective events detected, consider adjusting parameters"
                    )
                arcos_widget.Progress.value = 40

                # empty what to run list to check for new parameter changes
                stored_variables.clear_what_to_run()

                # update layers
                # check which layers need to be added, add these layers
                if return_collev and return_points:
                    return [all_cells, active_cells, coll_cells, coll_events]
                elif not return_collev and return_points:
                    return [all_cells, active_cells]


class CollevPlotter(QWidget):
    """
    QWidget for plotting.
    Class to make a matplotlib figure canvas and add it to a Qwidget.
    Canvas, figure and axis objects can be acessed by self.canvas,
    self.fig and self.ax. This plots duration of Collective events over their size as
    returned by arcos.
    """

    def __init__(self, viewer: "napari.viewer.Viewer", parent=None):
        """Initialise instance.
        :param viewer: Napari viewer instance
        :type viewer: napari.viewer.Viewer
        :param parent: Parent widget, optional
        :type parent: qtpy.QtWidgets.QWidget
        """
        super().__init__(parent)
        self.viewer = viewer
        self._init_mpl_widgets()
        self.update_plot()

        # connect callbacks
        self.viewer.layers.events.inserted.connect(self.update_plot)
        self.viewer.layers.events.removed.connect(self.update_plot)

    def _init_mpl_widgets(self):
        """
        Method to initialise a matplotlib figure canvas, to generate,
        set plot style and axis, and populate it with a matplotlib.figure.Figure.
        """
        # set up figure and axe objects
        with plt.style.context("dark_background"):
            plt.rcParams["figure.dpi"] = 110
            plt.rcParams["axes.edgecolor"] = "#ffffff"
            self.fig = Figure(figsize=(3, 2))
            self.canvas = FigureCanvas(self.fig)
            self.ax = self.fig.add_subplot(111)
            self.ax.scatter([], [])
            self.ax.set_xlabel("Total Size")
            self.ax.set_ylabel("Event Duration")
            self.canvas.figure.tight_layout()

        # construct layout
        layout = QVBoxLayout()
        # layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.setWindowTitle("Collective Events")

    def update_plot(self):
        """
        Method to update the matplotlibl axis object self.ax with new values from
        the stored_variables object
        """
        arcos = stored_variables.arcos
        # if no calculation was run so far (i.e. when the widget is initialized)
        # populate it with no data
        if arcos is not None:
            stats = arcos.calculate_stats()
        else:
            stats = pd.DataFrame(data={"totSz": [], "clDur": []})
        self.ax.cla()
        self.ax.spines["bottom"].set_color("white")
        self.ax.spines["top"].set_color("white")
        self.ax.spines["right"].set_color("white")
        self.ax.spines["left"].set_color("white")
        self.ax.xaxis.label.set_color("white")
        self.ax.yaxis.label.set_color("white")
        self.ax.tick_params(colors="white", which="both")
        self.ax.axis("on")
        stats = stats[["totSz", "clDur"]]
        self.ax.scatter(stats[["totSz"]], stats[["clDur"]], alpha=0.8)
        self.ax.set_xlabel("Total Size")
        self.ax.set_ylabel("Event Duration")
        self.fig.canvas.draw_idle()


class TimeSeriesPlots(QWidget):
    """
    QWidget for plotting.
    Class to make a matplotlib figure canvas and add it to a Qwidget.
    Canvas, figure and axis objects can be acessed by self.canvas, self.fig and self.ax.
    This plots several different Timeseries plots such as Position/t plots,
    tracklength histogram and a measurment density plot.
    """

    def __init__(self, napari_viewer, parent=None):
        """
        Initialise instance.
        :param viewer: Napari viewer instance
        :type viewer: napari.viewer.Viewer
        :param parent: Parent widget, optional
        :type parent: qtpy.QtWidgets.QWidget
        """
        super().__init__(parent)
        self.viewer = napari_viewer
        # available plots
        self.plot_list = [
            "tracklength histogram",
            "measurment density plot",
            "x/t-plot",
            "y/t-plot",
        ]
        self._init_widgets()

    def _init_widgets(self):
        """
        Method to initialise a matplotlib figure canvas as well as a spinbox,
        Button and label widgets. Additionally, generates a
        matplotlib.backends.backend_qt5agg.FigureCanvas, a set plot style and axis,
        and populates it with a matplotlib.figure.Figure.
        These are the added to a QVboxlayout.
        """
        # creating spinbox widget
        self.sample_number = QSpinBox()
        self.sample_number.setMinimum(1)
        self.sample_number.setMaximum(200)
        self.sample_number.setValue(100)

        self.button = QPushButton("Update Plot")
        self.button.clicked.connect(self.update_plot)

        # label
        self.spinbox_title = QLabel("Sample Size")

        # creating a combo box widget
        self.combo_box = QComboBox(self)
        self.combo_box.addItems(self.plot_list)
        self.combo_box.currentIndexChanged.connect(self.update_plot)

        # set up figure and axe objects
        with plt.style.context("dark_background"):
            plt.rcParams["figure.dpi"] = 110
            plt.rcParams["axes.edgecolor"] = "#ffffff"
            self.fig = Figure(figsize=(3, 2))
            self.canvas = FigureCanvas(self.fig)
            self.ax = self.fig.add_subplot(111)
            self.ax.scatter([], [])
            self.ax.set_xlabel("X Axis")
            self.ax.set_ylabel("Y Axis")
            self.canvas.figure.tight_layout()

        # construct layout
        layout = QVBoxLayout()
        layout_combobox = QVBoxLayout()
        layout_spinbox = QHBoxLayout()

        # add widgets to sub_layouts
        layout_combobox.addWidget(self.button)
        layout_combobox.addWidget(self.combo_box)
        layout_spinbox.addWidget(self.spinbox_title)
        layout_spinbox.addWidget(self.sample_number)

        # add sublayouts together
        layout.addLayout(layout_combobox)
        layout.addLayout(layout_spinbox)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.setWindowTitle("Collective Events")

    def update_plot(self):
        """
        Method to update the from the dropdown menu chosen
        matplotlibl plot with values from
        the stored_variables object dataframe.
        """
        # return plottype that should be plotted
        plottype = self.combo_box.currentText()

        # sample number for position/t-plots
        n = self.sample_number.value()

        # get column values and dataframe
        columns = columnpicker.dicCols.value
        dataframe = stored_variables.dataframe

        # check if some data was loaded already, otherwise do nothing
        if not dataframe.empty:
            self.ax.cla()
            self.ax.spines["bottom"].set_color("white")
            self.ax.spines["top"].set_color("white")
            self.ax.spines["right"].set_color("white")
            self.ax.spines["left"].set_color("white")
            self.ax.xaxis.label.set_color("white")
            self.ax.yaxis.label.set_color("white")
            self.ax.tick_params(colors="white", which="both")
            self.ax.axis("on")

            # tracklength histogram
            if plottype == "tracklength histogram":
                track_length = dataframe.groupby(columns["track_id"]).size()
                self.ax.hist(track_length)
                self.ax.set_xlabel("tracklength")
                self.ax.set_ylabel("counts")

            # measurment density plot, kde
            elif plottype == "measurment density plot":
                density = gaussian_kde(dataframe[columns["measurment"]].interpolate())
                x = np.linspace(
                    min(dataframe[columns["measurment"]]),
                    max(dataframe[columns["measurment"]]),
                    100,
                )
                y = density(x)
                self.ax.plot(x, y)
                self.ax.set_xlabel("measurement values")
                self.ax.set_ylabel("density")

            # xy/t plots
            elif plottype == "x/t-plot":
                sample = pd.Series(dataframe[columns["track_id"]].unique()).sample(
                    n, replace=True
                )
                pd_from_r_df = dataframe.loc[
                    dataframe[columns["track_id"]].isin(sample)
                ]
                for label, df in pd_from_r_df.groupby(columns["track_id"]):
                    self.ax.plot(df[columns["frame"]], df[columns["x_coordinates"]])
                self.ax.set_xlabel("Frame")
                self.ax.set_ylabel("Position X")

            elif plottype == "y/t-plot":
                sample = pd.Series(dataframe[columns["track_id"]].unique()).sample(
                    n, replace=True
                )
                pd_from_r_df = dataframe.loc[
                    dataframe[columns["track_id"]].isin(sample)
                ]
                for label, df in pd_from_r_df.groupby(columns["track_id"]):
                    self.ax.plot(df[columns["frame"]], df[columns["y_coordinates"]])
                self.ax.set_xlabel("Frame")
                self.ax.set_ylabel("Position Y")
            self.fig.canvas.draw_idle()
        else:
            show_info("No Data to plot")


# function to export csv to specified path
def export_csv(merged_data):
    """
    function to export the arcos data sotred in the
    stored_varaibles object and save it to the
    filepath set with the arcos_widget widget
    """
    if merged_data.empty:
        show_info("No data to export, run arcos first")
    else:
        output_csv_folder.close()
        path = str(output_csv_folder.filename.value)
        output_path = f"{path}{sep}{output_csv_folder.Name.value}.csv"
        merged_data.to_csv(output_path)
        show_info(f"wrote csv file to {output_path}")


# export movie
def movie_export(viewer, automatic_viewer_size):
    """
    function to export image sequence from the viewer
    """
    # gets current viewer
    viewer = current_viewer()
    # closes magicgui filepicker
    output_movie_folder.close()
    # if no layers are present, dont export data
    if len(viewer.layers) == 0:
        show_info("No data to export, run arcos first")
    else:
        # hides dock widgets, sets path, gets viwer dimensions
        hide_dock_widgets(viewer)
        path = str(output_movie_folder.filename.value)
        output_path = f"{path}{sep}{output_movie_folder.Name.value}"
        rgt, rgy, rgx = deepcopy(viewer.dims.range)
        maxx, maxy = rgx[1], rgy[1]
        # resize viewer if chosen
        if automatic_viewer_size:
            resize_napari([maxx, maxy], viewer)
        # iterate over frames to export data to chosen output path
        iterate_over_frames.show()
        iterate_over_frames(viewer, output_path)
        iterate_over_frames.close()
        show_dock_widgets(viewer)


@magicgui(
    call_button="Ok",
    filename={"label": "Choose Folder:", "mode": "d"},
    Automaic_viewer_size={
        "widget_type": "CheckBox",
        "label": "Automatically determine correct \n viewer size for export",
    },
)
def output_movie_folder(
    viewer: "napari.viewer.Viewer",
    filename=Path(),
    Name="arcos",
    Automaic_viewer_size=True,
):
    """
    FileDialog with magicgui to choose movie path
    """
    output_movie_folder.close()
    movie_export(viewer, Automaic_viewer_size)


# show folder selector for movie export
def show_output_movie_folder():
    output_movie_folder.show()


@magicgui(call_button="Ok", filename={"label": "Choose Folder:", "mode": "d"})
def output_csv_folder(filename=Path(), Name="arcos_data"):
    """
    FileDialog with magicgui for writing csv file
    """
    merged_data = stored_variables.data_merged
    output_csv_folder.close()
    export_csv(merged_data)


# show folder selector for csv epxort
def show_output_csv_folder():
    output_csv_folder.show()


# function to hide and show dockwidgets -> maybe risky method?
def hide_dock_widgets(viewer):
    for key, value in viewer.window._dock_widgets.items():
        value.hide()


def show_dock_widgets(viewer):
    for key, value in viewer.window._dock_widgets.items():
        value.show()


#####################################################################################
