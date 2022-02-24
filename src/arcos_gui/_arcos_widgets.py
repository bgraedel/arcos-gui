from os import sep
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import napari
import numpy as np
import pandas as pd
from magicgui import magic_factory, magicgui
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from napari.types import LayerDataTuple
from napari.utils.notifications import show_info
from qtpy import QtWidgets, uic
from qtpy.QtCore import Qt
from scipy.stats import gaussian_kde
from superqt import QDoubleRangeSlider, QRangeSlider

if TYPE_CHECKING:
    import napari.layers
    import napari.viewer

# local imports
from arcos_gui.arcos_module import ARCOS, process_input
from arcos_gui.export_movie import iterate_over_frames, resize_napari
from arcos_gui.magic_guis import columnpicker, show_timestamp_options, timestamp_options
from arcos_gui.shape_functions import (
    COLOR_CYCLE,
    assign_color_id,
    format_verticesHull,
    get_verticesHull,
    make_shapes,
    make_timestamp,
)
from arcos_gui.temp_data_storage import data_storage

# initalize class
stored_variables = data_storage()


class _MainUI:

    UI_FILE = str(Path(__file__).parent / "_ui" / "ARCOS_widget.ui")

    # The UI_FILE above contains these objects:
    frame_interval_label: QtWidgets.QLabel
    min_tracklength_label: QtWidgets.QLabel
    max_tracklength_label: QtWidgets.QLabel
    rescale_meas_label: QtWidgets.QLabel
    position_label: QtWidgets.QLabel
    file_LineEdit: QtWidgets.QLineEdit
    open_file_button: QtWidgets.QPushButton
    browse_file: QtWidgets.QPushButton
    position: QtWidgets.QComboBox
    frame_interval: QtWidgets.QSpinBox
    rescale_measurment: QtWidgets.QSpinBox
    min_tracklength: QtWidgets.QSlider
    min_tracklength_spinbox: QtWidgets.QDoubleSpinBox
    max_tracklength: QtWidgets.QSlider
    max_tracklength_spinbox: QtWidgets.QDoubleSpinBox
    filter_groupBox: QtWidgets.QGroupBox
    filter_input_data: QtWidgets.QPushButton
    horizontalLayout_tracklength: QtWidgets.QHBoxLayout

    clip_low_label: QtWidgets.QLabel
    clip_high_label: QtWidgets.QLabel
    intervale_type_label: QtWidgets.QLabel
    bias_method_label: QtWidgets.QLabel
    smooth_k_label: QtWidgets.QLabel
    bias_k_label: QtWidgets.QLabel
    polyDeg_label: QtWidgets.QLabel
    bin_peak_threshold_label: QtWidgets.QLabel
    bin_threshold_label: QtWidgets.QLabel
    neighbourhood_label: QtWidgets.QLabel
    min_clustersize_label: QtWidgets.QLabel
    min_dur_label: QtWidgets.QLabel
    tot_size_label: QtWidgets.QLabel

    interpolate_meas: QtWidgets.QCheckBox
    clip_meas: QtWidgets.QCheckBox
    clip_low: QtWidgets.QDoubleSpinBox
    clip_high: QtWidgets.QDoubleSpinBox
    interval_type: QtWidgets.QComboBox
    bias_method: QtWidgets.QComboBox
    smooth_k: QtWidgets.QComboBox
    bias_k: QtWidgets.QSpinBox
    polyDeg: QtWidgets.QSpinBox
    bin_peak_threshold: QtWidgets.QDoubleSpinBox
    bin_threshold: QtWidgets.QDoubleSpinBox
    neighbourhood_size: QtWidgets.QSpinBox
    min_clustersize: QtWidgets.QSpinBox
    min_dur: QtWidgets.QSpinBox
    total_event_size: QtWidgets.QSpinBox
    Progress: QtWidgets.QProgressBar
    update_arcos: QtWidgets.QPushButton
    arcos_group: QtWidgets.QGroupBox
    clip_frame: QtWidgets.QFrame

    point_size_label: QtWidgets.QLabel
    select_lut_label: QtWidgets.QLabel
    max_lut_mapping_label: QtWidgets.QLabel
    min_lut_mapping_label: QtWidgets.QLabel
    point_size: QtWidgets.QDoubleSpinBox
    LUT: QtWidgets.QComboBox
    max_lut: QtWidgets.QSlider
    max_lut_spinbox: QtWidgets.QDoubleSpinBox
    min_lut: QtWidgets.QSlider
    min_lut_spinbox: QtWidgets.QDoubleSpinBox
    reset_lut: QtWidgets.QPushButton
    layer_properties: QtWidgets.QGroupBox
    horizontalLayout_lut: QtWidgets.QHBoxLayout

    def setup_ui(self):
        uic.loadUi(self.UI_FILE, self)  # load QtDesigner .ui file

        self.LUT.addItems(stored_variables.colormaps)
        self.LUT.setCurrentText("RdYlBu_r")

        # set text of Line edit
        self.file_LineEdit.setText(".")


class MainWindow(QtWidgets.QWidget, _MainUI):
    """
    widget allowing a user to import a csv file, filter this file,
    choose arcos parameters, choose LUT mappings aswell as shape sizes
    When called runs arcos.
    list of napari.types.LayerDataTuble to add or update layers is generated.
    """

    def __init__(self, viewer: napari.viewer.Viewer, remote=True):
        super().__init__()
        self.setup_ui()
        self.layers_to_create: list = []
        self.what_to_run: list = []
        self.viewer: napari.viewer.Viewer = viewer
        self._filename: str = self.file_LineEdit.text()

        self._init_ranged_sliderts()
        self._set_default_visible()

        self._init_callbacks_for_whattorun()
        self._init_columnpicker_callbacks()
        self._init_callback_for_sample_data()
        self._init_size_contrast_callbacks()
        self._connect_ranged_sliders_to_spinboxes()
        self._connect_pushbutton_callbacks()
        self._init_callbacks_visible_arcosparameters()

    def _init_callbacks_visible_arcosparameters(self):
        # callback for changing available options of bias method
        self.bias_method.currentIndexChanged.connect(
            self.toggle_bias_method_parameter_visibility
        )

    def _connect_pushbutton_callbacks(self):
        # callback to open file dialog
        self.browse_file.clicked.connect(self.browse_files)
        # callback for updating what to run in arcos_widget
        self.open_file_button.clicked.connect(self.open_columnpicker)
        # reset what to run
        self.filter_input_data.clicked.connect(self.update_what_to_run_variable)
        self.open_file_button.clicked.connect(self.what_to_run.clear)
        # callbackfor filtering data
        self.filter_input_data.clicked.connect(self.filter_data)
        self.update_arcos.clicked.connect(self.reset_contrast)
        self.update_arcos.clicked.connect(self.run)

    def _connect_ranged_sliders_to_spinboxes(self):
        self.tracklenght_slider.valueChanged.connect(
            self.handleSlider_tracklength_ValueChange
        )
        self.min_tracklength_spinbox.valueChanged.connect(
            self.handle_min_tracklenght_box_ValueChange
        )
        self.max_tracklength_spinbox.valueChanged.connect(
            self.handle_max_tracklength_box_ValueChange
        )
        self.lut_slider.valueChanged.connect(self.handleSlider_lut_ValueChange)
        self.min_lut_spinbox.valueChanged.connect(self.handle_min_lut_box_ValueChange)
        self.max_lut_spinbox.valueChanged.connect(self.handle_max_lut_box_ValueChange)

    def _init_size_contrast_callbacks(self):
        # reset contrast and point size
        self.filter_input_data.clicked.connect(self.reset_contrast)
        self.filter_input_data.clicked.connect(self.set_point_size)
        # execute LUT and point functions
        self.reset_lut.clicked.connect(self.reset_contrast)
        # update size and LUT
        self.LUT.currentIndexChanged.connect(self.update_lut)
        self.lut_slider.valueChanged.connect(self.change_cell_colors)
        self.LUT.currentIndexChanged.connect(self.change_cell_colors)
        self.point_size.valueChanged.connect(self.change_cell_size)

    def _init_callback_for_sample_data(self):
        stored_variables.register_callback(self.callback_file_Linedit_text)

    def _init_columnpicker_callbacks(self):
        # callback for updating several variables after OK press in columnpicker widget
        columnpicker.Ok.changed.connect(self.close_columnpicker)
        columnpicker.Ok.changed.connect(self.set_positions)
        columnpicker.Ok.changed.connect(self.get_tracklengths)
        columnpicker.Ok.changed.connect(self.remove_layers_after_columnpicker)

    def _init_callbacks_for_whattorun(self):
        # callback for updating 'what to run' in stored_variables object
        self.clip_low.valueChanged.connect(self.update_what_to_run_all)
        self.clip_high.valueChanged.connect(self.update_what_to_run_all)
        self.smooth_k.valueChanged.connect(self.update_what_to_run_all)
        self.interval_type.currentIndexChanged.connect(self.update_what_to_run_all)
        self.bias_k.valueChanged.connect(self.update_what_to_run_all)
        self.bin_threshold.valueChanged.connect(self.update_what_to_run_all)
        self.neighbourhood_size.valueChanged.connect(self.update_what_to_run_tracking)
        self.bin_peak_threshold.valueChanged.connect(self.update_what_to_run_all)
        self.min_clustersize.valueChanged.connect(self.update_what_to_run_tracking)
        self.min_clustersize.valueChanged.connect(self.update_what_to_run_tracking)
        self.min_dur.valueChanged.connect(self.update_what_to_run_filtering)
        self.total_event_size.valueChanged.connect(self.update_what_to_run_filtering)

    def _init_ranged_sliderts(self):
        self.lut_slider = QDoubleRangeSlider(Qt.Horizontal)
        self.tracklenght_slider = QRangeSlider(Qt.Horizontal)
        self.horizontalLayout_lut.addWidget(self.lut_slider)
        self.horizontalLayout_tracklength.addWidget(self.tracklenght_slider)

        # set starting values
        self.lut_slider.setRange(0, 10)
        self.tracklenght_slider.setRange(0, 10)
        self.tracklenght_slider.setValue((0, 10))
        self.lut_slider.setValue((0, 10))

    def handleSlider_tracklength_ValueChange(self):
        slider_vals = self.tracklenght_slider.value()
        self.min_tracklength_spinbox.setValue(slider_vals[0])
        self.max_tracklength_spinbox.setValue(slider_vals[1])

    def handle_min_tracklenght_box_ValueChange(self, value):
        slider_vals = self.tracklenght_slider.value()
        self.tracklenght_slider.setValue((value, slider_vals[1]))

    def handle_max_tracklength_box_ValueChange(self, value):
        slider_vals = self.tracklenght_slider.value()
        self.tracklenght_slider.setValue((slider_vals[0], value))

    def handleSlider_lut_ValueChange(self):
        slider_vals = self.lut_slider.value()
        self.min_lut_spinbox.setValue(slider_vals[0])
        self.max_lut_spinbox.setValue(slider_vals[1])

    def handle_min_lut_box_ValueChange(self, value):
        slider_vals = self.lut_slider.value()
        self.lut_slider.setValue((value, slider_vals[1]))

    def handle_max_lut_box_ValueChange(self, value):
        slider_vals = self.lut_slider.value()
        self.lut_slider.setValue((slider_vals[0], value))

    def _set_default_visible(self):
        self.position.setVisible(False)
        self.position_label.setVisible(False)
        self.polyDeg.setVisible(False)
        self.polyDeg_label.setVisible(False)

    def browse_files(self):
        self.filename = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load CSV file", str(Path.home()), "csv(*.csv)"
        )
        self.file_LineEdit.setText(self.filename[0])

    def close_columnpicker(self):
        """
        gets the chosen columns to be stored inside of a dictionnary
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
        self.subtract_timeoffset()

    def subtract_timeoffset(self):
        data = stored_variables.data
        data[columnpicker.dicCols.value["frame"]] -= min(
            data[columnpicker.dicCols.value["frame"]]
        )

    def set_positions(self):
        # get unique positions for filter_widget
        if columnpicker.dicCols.value["field_of_view_id"] != "None":
            positions = list(
                stored_variables.data[
                    columnpicker.dicCols.value["field_of_view_id"]
                ].unique()
            )
        else:
            positions = ["None"]

        # set positions in filter widget, filter data
        self.position.clear()
        for i in positions:
            self.position.addItem(str(i), i)

        # hides position choice if no position column exists in the raw data
        # i.e. during columnpicker position was set to None.
        # Also hides it if there is only one position available.
        # Updates everytime when new data is read in
        if self.position.count() <= 1:
            self.position.setVisible(False)
            self.position_label.setVisible(False)
        else:
            self.position.setVisible(True)
            self.position_label.setVisible(True)

    def get_tracklengths(self):
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

            if minmax[1] - minmax[0] > 1:
                self.tracklenght_slider.setMinimum(minmax[0])
                self.tracklenght_slider.setMaximum(minmax[1])

            self.min_tracklength_spinbox.setMinimum(minmax[0])
            self.max_tracklength_spinbox.setMinimum(minmax[0])

            self.min_tracklength_spinbox.setMaximum(minmax[1])
            self.max_tracklength_spinbox.setMaximum(minmax[1])

            self.min_tracklength_spinbox.setValue(minmax[0])
            self.max_tracklength_spinbox.setValue(minmax[1])

    def remove_layers_after_columnpicker(self):
        """
        removes existing arcos layers before loading new data
        """
        layer_list = self.get_layer_list()
        for layer in [
            "coll cells",
            "coll events",
            "active cells",
            "all_cells",
            "Timestamp",
        ]:
            if layer in layer_list:
                self.viewer.layers.remove(layer)

    def get_layer_list(self):
        layer_list = [layer.name for layer in self.viewer.layers]
        return layer_list

    def update_what_to_run_variable(self):
        """
        updates a 'what to run' variable in the stored_variables object,
        that is used in arcos_widget to check if what to run
        when certain field have updated values
        """
        self.what_to_run.append("all")

    def open_columnpicker(self):
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
        csv_file = self.file_LineEdit.text()
        if str(csv_file).endswith(".csv"):
            self.layers_to_create.clear()
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

    def filter_data(self):
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
                in_data.filter_position(self.position.currentData())
            # filter by tracklenght
            in_data.filter_tracklength(
                self.min_tracklength_spinbox.value(),
                self.max_tracklength_spinbox.value(),
            )
            # option to rescale the measurment column
            in_data.rescale_measurment(rescale_factor=self.rescale_measurment.value())
            # option to set frame interval
            in_data.frame_interval(self.frame_interval.value())

            dataframe = in_data.return_pd_df()

            # get min and max values
            if not dataframe.empty:
                max_meas = max(dataframe[columnpicker.dicCols.value["measurment"]])
                min_meas = min(dataframe[columnpicker.dicCols.value["measurment"]])
                stored_variables.min_max = (min_meas, max_meas)
            stored_variables.dataframe = dataframe
            show_info("Data Filtered!")

    # several functions to update the 'what to run' variable in stored_variables

    def update_what_to_run_all(self):
        self.what_to_run.append("all")

    def update_what_to_run_tracking(self):
        self.what_to_run.append("from_tracking")

    def update_what_to_run_filtering(self):
        self.what_to_run.append("from_filtering")

    def toggle_bias_method_parameter_visibility(self):
        """
        based on the seleciton of bias method:
        shows or hides the appropriate options in the widget
        """
        if self.bias_method.currentText() == "runmed":
            self.smooth_k.setVisible(True)
            self.smooth_k_label.setVisible(True)
            self.polyDeg.setVisible(False)
            self.polyDeg_label.setVisible(False)
            self.bias_k.setVisible(True)
            self.bias_k_label.setVisible(True)
            self.bin_peak_threshold.setVisible(True)
            self.bin_peak_threshold_label.setVisible(True)
            self.bin_threshold.setVisible(True)
            self.bin_threshold_label.setVisible(True)

        if self.bias_method.currentText() == "lm":
            self.smooth_k.setVisible(True)
            self.smooth_k_label.setVisible(True)
            self.polyDeg.setVisible(True)
            self.polyDeg_label.setVisible(True)
            self.bias_k.setVisible(False)
            self.bias_k_label.setVisible(False)
            self.bin_peak_threshold.setVisible(True)
            self.bin_peak_threshold_label.setVisible(True)
            self.bin_threshold.setVisible(True)
            self.bin_threshold_label.setVisible(True)

        if self.bias_method.currentText() == "none":
            self.smooth_k.setVisible(True)
            self.smooth_k_label.setVisible(True)
            self.polyDeg.setVisible(False)
            self.polyDeg_label.setVisible(False)
            self.bias_k.setVisible(False)
            self.bias_k_label.setVisible(False)
            self.bin_peak_threshold.setVisible(False)
            self.bin_peak_threshold_label.setVisible(False)
            self.bin_threshold.setVisible(True)
            self.bin_threshold_label.setVisible(True)

    def set_point_size(self):
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
            self.point_size.setValue(
                0.75482
                + 0.00523857 * max_coord_diff
                + 9.0618311e-6 * max_coord_diff ** 2
            )

    def reset_contrast(self):
        """
        updates values in lut mapping slider
        """
        min_max = stored_variables.min_max
        # change slider values
        self.max_lut_spinbox.setMaximum(min_max[1])
        self.max_lut_spinbox.setMinimum(min_max[0])
        self.min_lut_spinbox.setMaximum(min_max[1])
        self.min_lut_spinbox.setMinimum(min_max[0])
        self.lut_slider.setRange(*min_max)
        self.max_lut_spinbox.setValue(min_max[1])
        self.min_lut_spinbox.setValue(min_max[0])

    def update_lut(self):
        """
        updates LUT choice in stored_variables
        """
        stored_variables.lut = self.LUT.currentText()

    def change_cell_colors(self):
        """
        function to update lut and corresponding lut mappings
        """
        layer_list = self.get_layer_list()
        min_value = self.min_lut_spinbox.value()
        max_value = self.max_lut_spinbox.value()
        if "all_cells" in layer_list:
            self.viewer.layers["all_cells"].face_colormap = self.LUT.currentText()
            self.viewer.layers["all_cells"].face_contrast_limits = (
                min_value,
                max_value,
            )
            self.viewer.layers["all_cells"].refresh_colors()

    def change_cell_size(self):
        """
        function to update size of points and shapes layers:
        "all_cells, "active cells", "coll cells" and "coll events"
        """
        layer_list = self.get_layer_list()
        size = self.point_size.value()
        if "all_cells" in layer_list:
            self.viewer.layers["all_cells"].size = size
            self.viewer.layers["active cells"].size = round(size / 2.5, 2)

        if "coll cells" in layer_list:
            self.viewer.layers["coll cells"].size = round(size / 1.7, 2)
            self.viewer.layers["coll events"].edge_width = size / 5
            self.viewer.layers["coll events"].refresh()

    def arcos_function(self) -> LayerDataTuple:
        """
        ARCOS function to execute R code and detect collective events.

        Returned data can contain:
        all_cells:
        returns color coded points of all cells filtered by the filter_widget.
        Color code represents measurment active_cells: returns black dots,
        representing cells determined as being active
        by arcos binarise measurment function

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
            if "all" in self.what_to_run:

                # get point_size
                size = self.point_size.value()

                # sets Progressbar to 0
                self.Progress.reset()
                # create arcos object, run arcos
                arcos = ARCOS(stored_variables.dataframe, columnpicker.dicCols.value)
                arcos.create_arcosTS(
                    interval=1, inter_type=self.interval_type.currentText()
                )

                self.Progress.setValue(4)

                # if corresponding checkbox was selected run interpolate measurments
                if self.interpolate_meas.isChecked:
                    arcos.interpolate_measurements()

                # if corresponding checkbock was selected run clip_measuremnts
                if self.clip_meas.isChecked:
                    arcos.clip_measurements(
                        clip_low=self.clip_low.value(),
                        clip_high=self.clip_high.value(),
                    )

                self.Progress.setValue(8)

                # updates arcos object in the stored_variables object
                stored_variables.arcos = arcos

                # binarize data and update ts variable in stored_variables
                # update from where to run
                ts = arcos.bin_measurements(
                    self.bias_method.currentText(),
                    self.smooth_k.value(),
                    self.bias_k.value(),
                    self.bin_peak_threshold.value(),
                    self.bin_threshold.value(),
                    self.polyDeg.value(),
                    return_dataframe=True,
                )
                stored_variables.ts_data = ts
                self.what_to_run.append("from_tracking")

                self.Progress.setValue(12)

            # if statement checks if this part of the function has to be run
            # depends on the parameters changed in arcos widget
            if "from_tracking" in self.what_to_run:
                arcos = stored_variables.arcos  # type: ignore
                ts = stored_variables.ts_data
                # if active cells were detected, run this
                if 1 in ts["meas.bin"].values:
                    # track collective events
                    arcos.track_events(
                        self.neighbourhood_size.value(),
                        self.min_clustersize.value(),
                    )

                    self.Progress.setValue(16)

                # if no active cells were detected remove previous layer,
                # since this does not correspont to current widget parameters
                else:
                    layer_list = self.get_layer_list()
                    # check if layers exist, if yes, remove them
                    if "active cells" in layer_list:
                        self.viewer.layers.remove("active cells")
                        self.viewer.layers.remove("all_cells")
                    self.Progress.setValue(40)
                    show_info("No active Cells detected, consider adjusting parameters")

                # update stored variables
                stored_variables.arcos = arcos
                self.what_to_run.append("from_filtering")

            # depending on the parameters changed in arcos widget
            if "from_filtering" in self.what_to_run:

                # get most recent data from stored_variables
                arcos = stored_variables.arcos  # type: ignore
                ts = stored_variables.ts_data

                # if no data show info to run arcos first
                # and set the progressbar to 100%
                if arcos is None:
                    show_info("No data available, run arcos first")
                    self.Progress.setValue(0)

                # if cells were classifed as being active (represented by a 1)
                # filter tracked events acording to chosen parameters
                elif 1 in ts["meas.bin"].values:

                    # set return varaibles to check which layers have to be created
                    return_collev = False
                    return_points = True
                    out = arcos.filter_tracked_events(
                        self.min_dur.value(),
                        self.total_event_size.value(),
                        as_pd_dataframe=True,
                    )

                    self.Progress.setValue(20)

                    # update stats variable
                    arcos.calculate_stats()

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
                    datAct = merged_data[merged_data["meas.bin"] > 0][
                        vColsCore
                    ].to_numpy()

                    # get point_size
                    size = self.point_size.value()

                    active_cells = (
                        datAct,
                        {
                            "size": round(size / 2.5, 2),
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
                            "size": size,
                            "edge_width": 0,
                            "opacity": 1,
                            "symbol": "disc",
                            "name": "all_cells",
                        },
                        "points",
                    )
                    self.Progress.setValue(24)

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
                                correct x/y columns selected? \n \
                                x, y columns: {datChull}"
                            )

                        datChull = format_verticesHull(
                            datChull,
                            columnpicker.dicCols.value["frame"],
                            columnpicker.dicCols.value["x_coordinates"],
                            columnpicker.dicCols.value["y_coordinates"],
                            "collid",
                        )

                        self.Progress.setValue(28)

                        df_collid_colors = assign_color_id(
                            df=datChull,
                            palette=COLOR_CYCLE,
                        )

                        datChull = datChull.merge(df_collid_colors, on="collid")

                        # creates actuall shapes
                        kw_shapes = make_shapes(datChull, col_text="collid")

                        self.Progress.setValue(32)

                        # get point_size
                        size = self.point_size.value()
                        # create remaining layer.data.tuples
                        coll_cells = (
                            datColl,
                            {
                                "face_color": "black",
                                "size": round(size / 1.7, 2),
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
                                "edge_width": round(size / 5, 2),
                                "name": "coll events",
                            },
                            "shapes",
                        )
                        return_collev = True

                        self.Progress.setValue(36)
                    else:
                        layer_list = self.get_layer_list()
                        # check if layers exit, if yes remove them
                        if "coll cells" in layer_list:
                            self.viewer.layers.remove("coll cells")
                            self.viewer.layers.remove("coll events")
                        show_info(
                            "No collective events detected, consider adjusting parameters"  # NOQA
                        )
                    self.Progress.setValue(40)
                    self.layers_to_create.clear()

                    # update layers
                    # check which layers need to be added, add these layers
                    if return_collev and return_points:
                        self.layers_to_create = [
                            all_cells,
                            active_cells,
                            coll_cells,
                            coll_events,
                        ]
                    elif not return_collev and return_points:
                        self.layers_to_create = [all_cells, active_cells]
                    self.what_to_run.clear()

    def make_layers(self):
        layers_names = [layer.name for layer in self.viewer.layers]
        if self.layers_to_create:
            for layer in [
                "coll cells",
                "coll events",
                "active cells",
                "all_cells",
            ]:
                if layer in layers_names:
                    self.viewer.layers.remove(layer)
            for result in self.layers_to_create:
                self.viewer.add_layer(napari.layers.Layer.create(*result))

    def callback_file_Linedit_text(self, value):
        self.file_LineEdit.setText(value)
        self.open_columnpicker()
        columnpicker.frame.value = "t"
        columnpicker.track_id.value = "id"
        columnpicker.x_coordinates.value = "x"
        columnpicker.y_coordinates.value = "y"
        columnpicker.measurment.value = "m"
        columnpicker.field_of_view_id.value = "Position"

    def run(self):
        self.arcos_function()
        self.make_layers()
        self.change_cell_size()


class CollevPlotter(QtWidgets.QWidget):
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
        layout = QtWidgets.QVBoxLayout()
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


class TimeSeriesPlots(QtWidgets.QWidget):
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
        self.sample_number = QtWidgets.QSpinBox()
        self.sample_number.setMinimum(1)
        self.sample_number.setMaximum(200)
        self.sample_number.setValue(20)

        self.button = QtWidgets.QPushButton("Update Plot")
        self.button.clicked.connect(self.update_plot)

        # label
        self.spinbox_title = QtWidgets.QLabel("Sample Size")

        # creating a combo box widget
        self.combo_box = QtWidgets.QComboBox(self)
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
        layout = QtWidgets.QVBoxLayout()
        layout_combobox = QtWidgets.QVBoxLayout()
        layout_spinbox = QtWidgets.QHBoxLayout()

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
                df_grp = pd_from_r_df.groupby(columns["track_id"])
                for label, df in df_grp:
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
                df_grp = pd_from_r_df.groupby(columns["track_id"])
                for label, df in df_grp:
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
        # resize viewer if chosen
        if automatic_viewer_size:
            resize_napari([np.float64(1012), np.float64(1012)], viewer)
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
    filename=Path(),
    Name="arcos",
    Automaic_viewer_size=True,
):
    viewer = napari.current_viewer()
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
        value.setVisible(False)


def show_dock_widgets(viewer):
    for key, value in viewer.window._dock_widgets.items():
        value.show()


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
        layer_list = [layer.name for layer in viewer.layers]
        if "Timestamp" in layer_list:
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


if __name__ == "__main__":
    hi = MainWindow(viewer=napari.Viewer())
    no = MainWindow(viewer=napari.Viewer())
