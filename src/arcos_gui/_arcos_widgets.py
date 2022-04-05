from os import sep
from pathlib import Path
from typing import TYPE_CHECKING

import napari
import numpy as np
import pandas as pd
from magicgui import magic_factory, magicgui
from napari.types import LayerDataTuple
from napari.utils.notifications import show_info
from qtpy import QtWidgets, uic
from qtpy.QtCore import Qt
from qtpy.QtGui import QIcon
from superqt import QDoubleRangeSlider, QRangeSlider

if TYPE_CHECKING:
    import napari.layers
    import napari.viewer

# local imports
from arcos4py import ARCOS
from arcos4py.tools import filterCollev
from arcos_gui._plots import CollevPlotter, TimeSeriesPlots
from arcos_gui.data_module import process_input
from arcos_gui.export_movie import iterate_over_frames, resize_napari
from arcos_gui.magic_guis import columnpicker, show_timestamp_options, timestamp_options
from arcos_gui.shape_functions import (
    COLOR_CYCLE,
    assign_color_id,
    fix_3d_convex_hull,
    format_verticesHull,
    get_verticesHull,
    make_shapes,
    make_surface_3d,
    make_timestamp,
)
from arcos_gui.temp_data_storage import data_storage

# icons
ICONS = Path(__file__).parent / "_icons"
browse_file_icon = QIcon(str(ICONS / "folder-open-line.svg"))

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

    collevplot_goupbox: QtWidgets.QGroupBox
    timeseriesplot_groupbox: QtWidgets.QGroupBox
    evplot_layout: QtWidgets.QVBoxLayout
    tsplot_layout: QtWidgets.QVBoxLayout
    nbr_collev_display: QtWidgets.QLCDNumber

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
        self.viewer: napari.viewer.Viewer = viewer
        self.setup_ui()
        self._filename: str = self.file_LineEdit.text()
        self.layers_to_create: list = []
        self.what_to_run: set = set()
        self.data: pd.DataFrame = pd.DataFrame()
        self.filtered_data: pd.DataFrame = pd.DataFrame()
        self.arcos_filtered: pd.DataFrame = pd.DataFrame()
        self.timeseriesplot = TimeSeriesPlots(parent=self)
        self.collevplot = CollevPlotter(parent=self)
        self._add_plot_widgets()
        self._init_ranged_sliderts()
        self.browse_file.setIcon(browse_file_icon)
        self._set_default_visible()

        self._init_callbacks_for_whattorun()
        self._init_columnpicker_callbacks()
        self._init_callback_for_sample_data()
        self._init_size_contrast_callbacks()
        self._connect_ranged_sliders_to_spinboxes()
        self._connect_pushbutton_callbacks()
        self._init_callbacks_visible_arcosparameters()
        self._init_ts_plot_callbacks()
        self._init_columns()

    def _add_plot_widgets(self):
        self.evplot_layout.addWidget(self.collevplot)
        self.tsplot_layout.addWidget(self.timeseriesplot)

    def _ts_plot_update(self):
        self.timeseriesplot.update_plot(columnpicker, self.filtered_data)

    def _init_ts_plot_callbacks(self):
        self.timeseriesplot.combo_box.currentIndexChanged.connect(self._ts_plot_update)
        self.timeseriesplot.button.clicked.connect(self._ts_plot_update)

    def collev_plot_update(self):
        self.collevplot.update_plot(columnpicker, self.arcos_filtered)
        self.nbr_collev_display.display(self.collevplot.nbr_collev)

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
        self.filter_input_data.clicked.connect(self.update_what_to_run_all)
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

    def _init_columns(self):
        self.frame = "None"
        self.track_id = "None"
        self.x_coordinates = "None"
        self.y_coordinates = "None"
        self.z_coordinates = "None"
        self.measurement = "None"
        self.field_of_view_id = "None"

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
        self.clip_meas.setChecked(False)
        self.position.setVisible(False)
        self.position_label.setVisible(False)
        self.polyDeg.setVisible(False)
        self.polyDeg_label.setVisible(False)

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

    def callback_file_Linedit_text(self, value):
        """Used to load sample data from test_data.
        and set columnpicker to indicated values"""
        self.file_LineEdit.setText(value)
        self.open_columnpicker()
        columnpicker.frame.value = "t"
        columnpicker.track_id.value = "id"
        columnpicker.x_coordinates.value = "x"
        columnpicker.y_coordinates.value = "y"
        columnpicker.z_coordinates.value = "None"
        columnpicker.measurment.value = "m"
        columnpicker.field_of_view_id.value = "Position"

    def update_what_to_run_all(self):
        """
        sets 'what to run' attribute to 'all' in the what_to_run attirbute,
        that is used in the main function to check if what to run
        when certain field have updated values.
        """
        self.what_to_run.add("all")

    def update_what_to_run_tracking(self):
        """sets 'what to run' attribute to 'from_tracking' in the what_to_run attirbute,
        that is used in the main function to check if what to run
        when certain field have updated values."""
        self.what_to_run.add("from_tracking")

    def update_what_to_run_filtering(self):
        """sets 'what to run' attribute to 'from_filtering'
        in the what_to_run attirbute,
        that is used in the main function to check if what to run
        when certain field have updated values."""
        self.what_to_run.add("from_filtering")

    def browse_files(self):
        """Opens a filedialog and saves path as a string in self.filename"""
        self.filename = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load CSV file", str(Path.home()), "csv(*.csv)"
        )
        self.file_LineEdit.setText(self.filename[0])

    def subtract_timeoffset(self):
        """Method to subtract the timeoffset in the frame column of data"""
        data = self.data
        data[self.frame] -= min(data[self.frame])
        self.data = data

    def set_point_size(self):
        """
        updates values in lut mapping sliders
        """
        data = self.data
        if not data.empty:
            minx = min(data[self.x_coordinates])
            maxx = max(data[self.x_coordinates])
            miny = min(data[self.y_coordinates])
            maxy = max(data[self.y_coordinates])

            max_coord_diff = max(maxx - minx, maxy - miny)
            self.point_size.setValue(
                0.75482
                + 0.00523857 * max_coord_diff
                + 9.0618311e-6 * max_coord_diff**2
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

    def open_columnpicker(self):
        """
        Take a filename and if it is a csv file,
        opens it and stores it in the stored_variables_object.
        Shows columnpicker dialog.
        """
        columns = columnpicker.frame.choices
        column_keys = [
            "frame",
            "x_coordinates",
            "y_coordinates",
            "z_coordinates",
            "track_id",
            "measurment",
            "field_of_view_id",
        ]
        for i in column_keys:
            for index, j in enumerate(columns):
                getattr(columnpicker, i).del_choice(str(j))
        csv_file = self.file_LineEdit.text()
        if str(csv_file).endswith(".csv"):
            self.layers_to_create.clear()
            self.data = pd.read_csv(csv_file)
            columns = list(self.data.columns)
            columnpicker.frame.choices = columns
            columnpicker.track_id.choices = columns
            columnpicker.x_coordinates.choices = columns
            columnpicker.y_coordinates.choices = columns
            columnpicker.z_coordinates.choices = columns
            columnpicker.measurment.choices = columns
            columnpicker.field_of_view_id.choices = columns
            columnpicker.field_of_view_id.set_choice("None", "None")
            columnpicker.z_coordinates.set_choice("None", "None")
            columnpicker.show()
        else:
            show_info("Not a csv file")

    def close_columnpicker(self):
        """
        gets the chosen columns to be stored inside of
        class attributes and closes the columnpicker dialog.
        Additionally subtracts the frame-offset from the frame
        column in data.
        """
        # populate column dictionnary
        self.frame = columnpicker.frame.value
        self.track_id = columnpicker.track_id.value
        self.x_coordinates = columnpicker.x_coordinates.value
        self.y_coordinates = columnpicker.y_coordinates.value
        self.z_coordinates = columnpicker.z_coordinates.value
        self.measurement = columnpicker.measurment.value
        self.field_of_view_id = columnpicker.field_of_view_id.value
        columnpicker.close()
        self.subtract_timeoffset()

    def remove_layers_after_columnpicker(self):
        """removes existing arcos layers before loading new data"""
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
        """Get list of open layers"""
        layer_list = [layer.name for layer in self.viewer.layers]
        return layer_list

    def set_positions(self):
        """get unique positions from data, empty positions dialog
        for preveious data and append new positions."""
        if self.field_of_view_id != "None":
            positions = list(self.data[self.field_of_view_id].unique())
        else:
            positions = ["None"]

        # delete position values is position dialog self.positions
        self.position.clear()
        # add new positions
        for i in positions:
            self.position.addItem(str(i), i)

        # hides position choice if no position column exists in the raw data
        # i.e. during columnpicker position was set to None.
        # Also hides it if there is only one position available.
        # is updated everytime when new data is read in
        if self.position.count() <= 1:
            self.position.setVisible(False)
            self.position_label.setVisible(False)
        else:
            self.position.setVisible(True)
            self.position_label.setVisible(True)

    def set_posCol(self) -> list:
        if self.z_coordinates != "None":
            posCols = [self.x_coordinates, self.y_coordinates, self.z_coordinates]
            return posCols

        posCols = [self.x_coordinates, self.y_coordinates]
        return posCols

    def get_tracklengths(self):
        """
        Groups filtered data by track_id and
        returns minimum and maximum tracklenght.
        Updates min and max tracklenght in
        the widget spinbox and sliders.
        """
        data = self.data
        if not data.empty:
            if self.field_of_view_id != "None":
                track_lenths = self.data.groupby(
                    [
                        self.field_of_view_id,
                        self.track_id,
                    ]
                ).size()
            else:
                track_lenths = self.data.groupby([self.track_id]).size()
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

    def filter_data(self):
        """
        Used to filter the input datato contain a single position.
        filter options also include minimum and maximum tracklength.
        Allows for rescaling of measurment variable.
        """
        # gets raw data read in by arcos_widget from stored_variables object
        # and columns from columnpicker value
        posCols = self.set_posCol()
        in_data = process_input(
            df=self.data,
            field_of_view_column=self.field_of_view_id,
            frame_column=self.frame,
            pos_columns=posCols,
            track_id_column=self.track_id,
            measurement_column=self.measurement,
        )
        if self.data.empty or self.field_of_view_id == self.measurement:
            show_info("No data loaded, or not loaded correctly")
        else:
            # if the position column was not chosen in columnpicker,
            # dont filter by position
            if self.field_of_view_id != "None":
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

            filtered_data = in_data.return_pd_df()

            # get min and max values
            if not filtered_data.empty:
                max_meas = max(filtered_data[self.measurement])
                min_meas = min(filtered_data[self.measurement])
                stored_variables.min_max = (min_meas, max_meas)
            self.filtered_data = filtered_data
            self._ts_plot_update()
            show_info("Data Filtered!")

    def run_arcos(self) -> LayerDataTuple:
        """
        ARCOS method to detect collective events.

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
        returns convex hulls of individual collective
        events, in 2D case, color is coded accoring to a color_cycle attribute.
        in 3D case according to a LUT.
        """

        posCols = self.set_posCol()
        measbin_col = f"{self.measurement}.bin"
        collid_name = "collid"

        # checks if this part of the function has to be run,
        # depends on the parameters changed in arcos widget

        if self.filtered_data.empty:
            show_info("No Data Loaded, Use arcos_widget to load and filter data first")
        else:
            if "all" in self.what_to_run:

                # get point_size
                size = self.point_size.value()

                # sets Progressbar to 0
                self.Progress.reset()
                # create arcos object, run arcos
                arcos = ARCOS(
                    data=self.filtered_data,
                    posCols=posCols,
                    frame_column=self.frame,
                    id_column=self.track_id,
                    measurement_column=self.measurement,
                    clid_column=collid_name,
                )

                self.Progress.setValue(4)

                # if corresponding checkbox was selected run interpolate measurments
                if self.interpolate_meas.isChecked:
                    arcos.interpolate_measurements()

                # if corresponding checkbock was selected run clip_measuremnts
                if self.clip_meas.isChecked:
                    arcos.clip_meas(
                        clip_low=self.clip_low.value(),
                        clip_high=self.clip_high.value(),
                    )

                self.Progress.setValue(8)

                # updates arcos object in the stored_variables object
                stored_variables.arcos = arcos

                # binarize data and update ts variable in stored_variables
                # update from where to run
                ts = arcos.bin_measurements(
                    smoothK=self.smooth_k.value(),
                    biasK=self.bias_k.value(),
                    peakThr=self.bin_peak_threshold.value(),
                    binThr=self.bin_threshold.value(),
                    polyDeg=self.polyDeg.value(),
                    biasMet=self.bias_method.currentText(),
                )
                stored_variables.ts_data = ts
                self.what_to_run.add("from_tracking")

                self.Progress.setValue(12)

            # if statement checks if this part of the function has to be run
            # depends on the parameters changed in arcos widget
            if "from_tracking" in self.what_to_run:
                arcos = stored_variables.arcos  # type: ignore
                ts = stored_variables.ts_data
                # if active cells were detected, run this
                if 1 in ts[measbin_col].values:
                    # track collective events
                    arcos.trackCollev(
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
                self.what_to_run.add("from_filtering")

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
                elif 1 in ts[measbin_col].values:

                    # set return varaibles to check which layers have to be created
                    return_collev = False
                    return_points = True
                    filterer = filterCollev(arcos.data, self.frame, collid_name)
                    self.arcos_filtered = filterer.filter(
                        self.min_dur.value(),
                        self.total_event_size.value(),
                    )
                    self.Progress.setValue(20)

                    # merge tracked and original data
                    merged_data = pd.merge(
                        ts,
                        self.arcos_filtered[
                            [
                                self.frame,
                                self.track_id,
                                "collid",
                            ]
                        ],
                        how="left",
                        on=[
                            self.frame,
                            self.track_id,
                        ],
                    )
                    stored_variables.data_merged = merged_data

                    if self.z_coordinates == "None":
                        # column list
                        vColsCore = [
                            self.frame,
                            self.y_coordinates,
                            self.x_coordinates,
                        ]
                    else:
                        # column list
                        vColsCore = [
                            self.frame,
                            self.y_coordinates,
                            self.x_coordinates,
                            self.z_coordinates,
                        ]

                    # np matrix with all cells
                    datAll = merged_data[vColsCore].to_numpy()

                    # a dictionary with activities;
                    # shown as a color code of all cells

                    datAllProp = {"act": merged_data[self.measurement]}

                    # np matrix with acvtive cells; shown as black dots
                    datAct = merged_data[merged_data[measbin_col] > 0][
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
                            [self.frame, "collid"]
                        )
                        if self.z_coordinates == "None":
                            datChull = df_gb.apply(
                                get_verticesHull,
                                col_x=self.x_coordinates,
                                col_y=self.y_coordinates,
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
                                self.frame,
                                self.x_coordinates,
                                self.y_coordinates,
                                "collid",
                            )
                            self.Progress.setValue(28)

                            df_collid_colors = assign_color_id(
                                df=datChull,
                                palette=COLOR_CYCLE,
                            )

                            self.Progress.setValue(32)

                            datChull = datChull.merge(df_collid_colors, on="collid")
                            # create actual shapes
                            kw_shapes = make_shapes(datChull, col_text="collid")

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

                        else:
                            event_surfaces = make_surface_3d(
                                merged_data[~np.isnan(merged_data["collid"])],
                                self.frame,
                                self.x_coordinates,
                                self.y_coordinates,
                                self.z_coordinates,
                                "collid",
                            )

                            event_surfaces = fix_3d_convex_hull(
                                merged_data[vColsCore],
                                event_surfaces[0],
                                event_surfaces[1],
                                event_surfaces[2],
                                self.frame,
                            )
                            coll_events = (
                                event_surfaces,
                                {
                                    "colormap": "viridis",
                                    "name": "coll events",
                                    "opacity": 0.5,
                                },
                                "surface",
                            )

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
        """adds layers from self.layers_to_create,
        whitch itself is upated from run_arcos method"""
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

    def run(self):
        """main function to run arcos, add layers and change cell size"""
        self.run_arcos()
        self.make_layers()
        self.collev_plot_update()
        self.change_cell_size()


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
