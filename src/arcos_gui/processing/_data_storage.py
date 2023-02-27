"""Contains the data storage classes for the arcos_gui.

The data storage classes are used to store the data and the settings for the
different widgets. Moste of the attributes contain callbacks functionallity
which are used to update the widgets when the data changes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Union

import pandas as pd
from napari.utils.colormaps import AVAILABLE_COLORMAPS


@dataclass
class data_frame_storage:
    """Holds the dataframes and notifies the observers when the value changes.

    The dataframes are stored in the value attribute. The value attribute is a
    pandas dataframe. The value attribute can be set with the value setter.
    When the value is set the observers are notified and the callback functions
    are executed. The observers are registered with the value_changed_connect
    method. The observers are unregistered with the unregister_callback method.

    Attributes:
        value: The dataframe that is stored.
        callbacks_blocked: If True the callbacks are not executed when the
            value attribute is set.
        verbose: If True the callbacks are printed when they are executed.

    Methods:
        value_changed_connect: Register a callback function.
        unregister_callback: Unregister a callback function.
        toggle_callback_block: Toggle the callbacks_blocked attribute.
        toggle_verbose: Toggle the verbose attribute.
    """

    _value: pd.DataFrame = field(default_factory=pd.DataFrame)
    _callbacks: list = field(default_factory=list)
    value_name: str = "None"
    callbacks_blocked: bool = False
    verbose = False

    @property
    def value(self):
        """Return the value attribute."""
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self._notify_observers()

    def _notify_observers(self):
        """Notify the observers that the value attribute has changed."""
        if self.callbacks_blocked:
            return
        for callback in self._callbacks:
            if self.verbose:
                print(
                    f"data_frame_storage: {self.value_name} changed. Executing {callback}"
                )
            callback()

    def value_changed_connect(self, callback):
        """Register a callback function.

        The callback function is executed when the value attribute is set.

        Parameters
        ----------
        callback : function
            The callback function.
        """
        self._callbacks.append(callback)

    def unregister_callback(self, callback):
        """Unregister a callback function.

        Parameters
        ----------
        callback : function
            The callback function to be unregistered.
        """
        self._callbacks.remove(callback)

    def toggle_callback_block(self, set_explicit: bool | None = None):
        """Toggle the callbacks_blocked attribute."""
        if set_explicit is not None:
            self.callbacks_blocked = set_explicit
            return
        self.callbacks_blocked = not self.callbacks_blocked

    def toggle_verbose(self):
        """Toggle the verbose attribute."""
        self.verbose = not self.verbose

    def __repr__(self):
        return repr(self._value)


@dataclass
class value_callback:
    """Holds a value and notifies the observers when the value changes.

    The value is stored in the value attribute. The value attribute can be set
    with the value setter. When the value is set the observers are notified and
    the callback functions are executed. The observers are registered with the
    value_changed_connect method. The observers are unregistered with the
    unregister_callback method.

    Attributes
    ----------
    value: The value that is stored.
    callbacks_blocked: If True the callbacks are not executed when the value
        attribute is set.
    verbose: If True the callbacks are printed when they are executed.

    Methods
    -------
    value_changed_connect: Register a callback function.
    unregister_callback: Unregister a callback function.
    toggle_callback_block: Toggle the callbacks_blocked attribute.
    toggle_verbose: Toggle the verbose attribute.
    """

    _value: Union[int, str, None, Any]
    _callbacks: list = field(default_factory=list)
    callbacks_blocked: bool = False
    value_name: str = "value_callback"
    verbose = False

    @property
    def value(self):
        """Get the value that is stored."""
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self._notify_observers()

    def _notify_observers(self):
        """Notify the observers that the value attribute has changed."""
        if self.callbacks_blocked:
            return
        for callback in self._callbacks:
            if self.verbose:
                print(
                    f"value_callback: {self.value_name} changed. Executing {callback}"
                )
            callback()

    def value_changed_connect(self, callback):
        """Register a callback function.

        The callback function is executed when the value attribute is set.

        Parameters
        ----------
        callback : function
            The callback function.
        """
        self._callbacks.append(callback)

    def unregister_callback(self, callback):
        """Unregister a callback function.

        Parameters
        ----------
        callback : function
            The callback function to be unregistered.
        """
        self._callbacks.remove(callback)

    def toggle_callback_block(self, set_explicit: bool | None = None):
        """Toggle the callbacks_blocked attribute."""
        if set_explicit is not None:
            self.callbacks_blocked = set_explicit
            return
        self.callbacks_blocked = not self.callbacks_blocked

    def toggle_verbose(self):
        """Toggle the verbose attribute."""
        self.verbose = not self.verbose

    def __repr__(self):
        return repr(self._value)

    def __eq__(self, other):
        return self._value == other


@dataclass
class columnnames:
    """Stores column names for the dataframes.

    Attributes
    ----------
    frame_column: str
        The name of the column that contains the frame number.
    position_id: str
        The name of the column that contains the position id.
    object_id: str
        The name of the column that contains the object id.
    x_column: str
        The name of the column that contains the x coordinate.
    y_column: str
        The name of the column that contains the y coordinate.
    z_column: str
        The name of the column that contains the z coordinate.
    measurement_column_1: str
        The name of the column that contains the first measurement.
    measurement_column_2: str
        The name of the column that contains the second measurement.
    additional_filter_column: str
        The name of the column that contains the additional filter.
    measurement_math_operatoin: str
        The name of the column that contains the measurement math operation.
    measurement_bin: str | None
        The name of the column that contains the measurement bin.
    measurement_resc: str | None
        The name of the column that contains the measurement resc.
    collid_name: str
        The name of the column that contains the collid.
    measurement_column: str
        The name of the column that contains the measurement.
    pickablepickable_columns_names: list
        A list of all column names that can be set in the columnpicker_widget.
    posCol: list
        A list of all column names that are used for the position calculation.
        returns values for x, y and optionally z, if z is not 'None'.
    vcolscore: list
        A list of all column names that are used for the adding layers.
    as_dataframe: pandas.DataFrame
        A pandas.DataFrame containing all column names.
    """

    frame_column: str = "frame"
    position_id: str = "position_id"
    object_id: str = "track_id"
    x_column: str = "x"
    y_column: str = "y"
    z_column: str = "z"
    measurement_column_1: str = "measurement"
    measurement_column_2: str = "measurement_2"
    additional_filter_column: str = "additional_filter"
    measurement_math_operatoin: str = "None"
    measurement_bin: Union[str, None] = None
    measurement_resc: Union[str, None] = None
    collid_name: str = "collid"
    measurement_column: str = "measurement"

    @property
    def pickablepickable_columns_names(self):
        """returns a list of all column names that can be set in the columnpicker_widget"""
        return [
            self.frame_column,
            self.object_id,
            self.x_column,
            self.y_column,
            self.z_column,
            self.measurement_column_1,
            self.measurement_column_2,
            self.position_id,
            self.additional_filter_column,
            self.measurement_math_operatoin,
        ]

    @property
    def posCol(self):
        """returns a list of all coordinate columns"""
        if self.z_column != "None":
            return [self.x_column, self.y_column, self.z_column]
        return [self.x_column, self.y_column]

    @property
    def vcolscore(self):
        """returns a list of core columns columns"""
        if self.z_column != "None":
            return [self.frame_column, self.y_column, self.x_column, self.z_column]
        return [self.frame_column, self.y_column, self.x_column]

    @property
    def as_dataframe(self):
        """creates a dataframe from the columnnames"""
        df = pd.DataFrame(
            columns=["Column", "value"],
            data=[
                ["frame_column", self.frame_column],
                ["position_id", self.position_id],
                ["object_id", self.object_id],
                ["x_column", self.x_column],
                ["y_column", self.y_column],
                ["z_column", self.z_column],
                ["measurement_column_1", self.measurement_column_1],
                ["measurement_column_2", self.measurement_column_2],
                ["additional_filter_column", self.additional_filter_column],
                ["measurement_math_operatoin", self.measurement_math_operatoin],
                ["measurement_bin", self.measurement_bin],
                ["measurement_resc", self.measurement_resc],
                ["collid_name", self.collid_name],
                ["measurement_column", self.measurement_column],
            ],
        )
        return df


@dataclass(frozen=True)
class arcos_parameters:
    """Stores the parameters for the arcos algorithm that can be set in the arcos widget.

    Attributes
    ----------
    interpolate_meas: bool
        wether to interpolate the measurements or not.
    clip_meas: bool
        wether to clip the measurements or not.
    clip_low: float
        the lower bound for the clipping.
    clip_high: float,
        the upper bound for the clipping.
    smooth_k: int,
        the smoothing kernel size.
    bias_k: int,
        the bias kernel size, for long term detrending.
    bias_method: str,
        the bias method.
    polyDeg: int,
        the polynomial degree, used for lm detrending.
    bin_threshold: float,
        the bin threshold, used for binarization.
    bin_peak_threshold: float,
        the bin peak threshold, used for binarization.
    eps_method: str,
        the eps method, used for estimating the eps parameter.
    neighbourhood_size: float,
        the eps parameter, used for the clustering within arcos.
    epsPrev: float,
        epsilon used for linking.
    min_cluster_size: int,
        the minimum cluster size, used for the clustering within arcos.
    nprev: int,
        the number of previous frames to consider for linking.
    min_dur: int,
        the minimum duration of a collective event.
    total_event_size: int,
        the minimum number of unique objects in a collective event.
    add_convex_hull: bool,
        wether to add the convex hull layer.
    as_dataframe: pandas.DataFrame
         a pandas.DataFrame containing all parameters.

    Methods
    -------
    set_all_parameters(parameters: arcos_parameters)
        set all parameters from another arcos_parameters object.
    reset_all_parameters()
        reset all parameters to their default values.
    set_verbose(verbose: bool)
        set the verbose parameter. If true, when a a callback is triggered,
        the callback function will be printed to the console.
    toggle_callback_block(block: bool)
        block or unblock all callbacks.
    """

    _interpolate_meas: value_callback = field(
        default_factory=lambda: value_callback(False, value_name="interpolate_meas")
    )
    _clip_meas: value_callback = field(
        default_factory=lambda: value_callback(False, value_name="clip_meas")
    )
    _clip_low: value_callback = field(
        default_factory=lambda: value_callback(0.0, value_name="clip_low")
    )
    _clip_high: value_callback = field(
        default_factory=lambda: value_callback(1, value_name="clip_high")
    )
    _smooth_k: value_callback = field(
        default_factory=lambda: value_callback(1, value_name="smooth_k")
    )
    _bias_k: value_callback = field(
        default_factory=lambda: value_callback(5, value_name="bias_k")
    )
    _bias_method: value_callback = field(
        default_factory=lambda: value_callback("none", value_name="bias_method")
    )
    _polyDeg: value_callback = field(
        default_factory=lambda: value_callback(1, value_name="polyDeg")
    )
    _bin_threshold: value_callback = field(
        default_factory=lambda: value_callback(0.5, value_name="bin_threshold")
    )
    _bin_peak_threshold: value_callback = field(
        default_factory=lambda: value_callback(0.5, value_name="bin_peak_threshold")
    )
    _eps_method: value_callback = field(
        default_factory=lambda: value_callback("manual", value_name="eps_method")
    )
    _neighbourhood_size: value_callback = field(
        default_factory=lambda: value_callback(20, value_name="neighbourhood_size")
    )
    _epsPrev: value_callback = field(
        default_factory=lambda: value_callback(20, value_name="epsPrev")
    )
    _min_clustersize: value_callback = field(
        default_factory=lambda: value_callback(5, value_name="min_clustersize")
    )
    _nprev: value_callback = field(
        default_factory=lambda: value_callback(1, value_name="nprev")
    )
    _min_dur: value_callback = field(
        default_factory=lambda: value_callback(1, value_name="min_dur")
    )
    _total_event_size: value_callback = field(
        default_factory=lambda: value_callback(5, value_name="total_event_size")
    )
    _add_convex_hull: value_callback = field(
        default_factory=lambda: value_callback(True, value_name="add_convex_hull")
    )

    @property
    def as_dataframe(self):
        """creates a dataframe from the arcos parameters"""
        df = pd.DataFrame(
            columns=["parameter", "value"],
            data=[
                ["interpolate_meas", self.interpolate_meas.value],
                ["clip_meas", self.clip_meas.value],
                ["clip_low", self.clip_low.value],
                ["clip_high", self.clip_high.value],
                ["smooth_k", self.smooth_k.value],
                ["bias_k", self.bias_k.value],
                ["bias_method", self.bias_method.value],
                ["polyDeg", self.polyDeg.value],
                ["bin_threshold", self.bin_threshold.value],
                ["bin_peak_threshold", self.bin_peak_threshold.value],
                ["eps_method", self.eps_method.value],
                ["neighbourhood_size", self.neighbourhood_size.value],
                ["epsPrev", self.epsPrev.value],
                ["min_clustersize", self.min_clustersize.value],
                ["nprev", self.nprev.value],
                ["min_dur", self.min_dur.value],
                ["total_event_size", self.total_event_size.value],
            ],
        )
        df["value"] = df["value"].astype(str)
        return df

    def set_all_parameters(
        self, arcos_parameters_object: arcos_parameters, trigger_callback: bool = True
    ):
        """sets all parameters to the values of the given arcos_parameters object.

        Parameters
        ----------
        arcos_parameters_object : arcos_parameters
            the arcos_parameters object from which the values are taken
        trigger_callback : bool, optional
            if True, the callback functions associated with the parameters are triggered, by default True
        """
        self.toggle_callback_block(not trigger_callback)
        self.interpolate_meas.value = arcos_parameters_object.interpolate_meas.value
        self.clip_meas.value = arcos_parameters_object.clip_meas.value
        self.clip_low.value = arcos_parameters_object.clip_low.value
        self.clip_high.value = arcos_parameters_object.clip_high.value
        self.smooth_k.value = arcos_parameters_object.smooth_k.value
        self.bias_k.value = arcos_parameters_object.bias_k.value
        self.bias_method.value = arcos_parameters_object.bias_method.value
        self.polyDeg.value = arcos_parameters_object.polyDeg.value
        self.bin_threshold.value = arcos_parameters_object.bin_threshold.value
        self.bin_peak_threshold.value = arcos_parameters_object.bin_peak_threshold.value
        self.eps_method.value = arcos_parameters_object.eps_method.value
        self.neighbourhood_size.value = arcos_parameters_object.neighbourhood_size.value
        self.epsPrev.value = arcos_parameters_object.epsPrev.value
        self.min_clustersize.value = arcos_parameters_object.min_clustersize.value
        self.nprev.value = arcos_parameters_object.nprev.value
        self.min_dur.value = arcos_parameters_object.min_dur.value
        self.total_event_size.value = arcos_parameters_object.total_event_size.value
        self.toggle_callback_block(False)

    def reset_all_parameters(self, trigger_callback=True):
        """resets all values to default.

        Parameters
        ----------
        trigger_callback : bool, optional
            if True, the callback functions associated with the parameters are triggered, by default True.
        """
        self.toggle_callback_block(not trigger_callback)
        self.interpolate_meas.value = False
        self.clip_meas.value = False
        self.clip_low.value = 0.0
        self.clip_high.value = 1
        self.smooth_k.value = 1
        self.bias_k.value = 5
        self.bias_method.value = "none"
        self.polyDeg.value = 1
        self.bin_threshold.value = 0.5
        self.bin_peak_threshold.value = 0.5
        self.eps_method.value = "manual"
        self.neighbourhood_size.value = 20
        self.epsPrev.value = 20
        self.min_clustersize.value = 5
        self.nprev.value = 1
        self.min_dur.value = 1
        self.total_event_size.value = 5
        self.add_convex_hull.value = True
        self.toggle_callback_block(False)

    def set_verbose(self, verbose: bool = False):
        """sets all parameters to verbose.

        Parameters
        ----------
        verbose : bool, optional
            if True, the parameters are set to verbose, by default False
        """
        self.interpolate_meas.verbose = verbose
        self.clip_meas.verbose = verbose
        self.clip_low.verbose = verbose
        self.clip_high.verbose = verbose
        self.smooth_k.verbose = verbose
        self.bias_k.verbose = verbose
        self.bias_method.verbose = verbose
        self.polyDeg.verbose = verbose
        self.bin_threshold.verbose = verbose
        self.bin_peak_threshold.verbose = verbose
        self.eps_method.verbose = verbose
        self.neighbourhood_size.verbose = verbose
        self.epsPrev.verbose = verbose
        self.min_clustersize.verbose = verbose
        self.nprev.verbose = verbose
        self.min_dur.verbose = verbose
        self.total_event_size.verbose = verbose
        self.add_convex_hull.verbose = verbose

    def toggle_callback_block(self, block: bool | None = None):
        """blocks all callbacks.

        Parameters
        ----------
        block : bool | None, optional
            if True, all callbacks are blocked, if False, all callbacks are unblocked,
            if None, the current state is toggled.
            by default None.
        """
        self.interpolate_meas.toggle_callback_block(block)
        self.clip_meas.toggle_callback_block(block)
        self.clip_low.toggle_callback_block(block)
        self.clip_high.toggle_callback_block(block)
        self.smooth_k.toggle_callback_block(block)
        self.bias_k.toggle_callback_block(block)
        self.bias_method.toggle_callback_block(block)
        self.polyDeg.toggle_callback_block(block)
        self.bin_threshold.toggle_callback_block(block)
        self.bin_peak_threshold.toggle_callback_block(block)
        self.eps_method.toggle_callback_block(block)
        self.neighbourhood_size.toggle_callback_block(block)
        self.epsPrev.toggle_callback_block(block)
        self.min_clustersize.toggle_callback_block(block)
        self.nprev.toggle_callback_block(block)
        self.min_dur.toggle_callback_block(block)
        self.total_event_size.toggle_callback_block(block)
        self.add_convex_hull.toggle_callback_block(block)

    @property
    def interpolate_meas(self):
        """interpolate measurement"""
        return self._interpolate_meas

    @property
    def clip_meas(self):
        """clip measurement"""
        return self._clip_meas

    @property
    def clip_low(self):
        """clip low"""
        return self._clip_low

    @property
    def clip_high(self):
        """clip high"""
        return self._clip_high

    @property
    def smooth_k(self):
        """smooth k"""
        return self._smooth_k

    @property
    def bias_k(self):
        """bias k"""
        return self._bias_k

    @property
    def bias_method(self):
        """bias method"""
        return self._bias_method

    @property
    def polyDeg(self):
        """poly deg"""
        return self._polyDeg

    @property
    def bin_threshold(self):
        """bin threshold"""
        return self._bin_threshold

    @property
    def bin_peak_threshold(self):
        """bin peak threshold"""
        return self._bin_peak_threshold

    @property
    def eps_method(self):
        """eps method"""
        return self._eps_method

    @property
    def neighbourhood_size(self):
        """neighbourhood size"""
        return self._neighbourhood_size

    @property
    def epsPrev(self):
        """eps prev"""
        return self._epsPrev

    @property
    def min_clustersize(self):
        """min cluster size"""
        return self._min_clustersize

    @property
    def nprev(self):
        """nprev spinbox"""
        return self._nprev

    @property
    def min_dur(self):
        """min dur"""
        return self._min_dur

    @property
    def total_event_size(self):
        """total event size"""
        return self._total_event_size

    @property
    def add_convex_hull(self):
        """add convex hull"""
        return self._add_convex_hull


@dataclass(frozen=True)
class timestamp_parameters:
    """Stores the parameters for the timestamp options that can be set in the timestamp widget.


    Attributes
    ----------
    start_time : int
        the start time of the timestamp
    step_time : int
        the step time of the timestamp
    prefix : str
        the prefix of the timestamp
    suffix : str
        the suffix of the timestamp
    position : str
        the position of the timestamp
    size : int
        the size of the timestamp
    x_shift : int
        the x shift of the timestamp
    y_shift : int
        the y shift of the timestamp
    as_dataframe : pd.DataFrame
        a dataframe with the parameters
    """

    start_time: int = 0
    step_time: int = 1
    prefix: str = "t"
    suffix: str = ""
    position: str = "upper_left"
    size: int = 1
    x_shift: int = 0
    y_shift: int = 0

    @property
    def as_dataframe(self):
        """creates a dataframe from the timestamp parameters"""
        df = pd.DataFrame(
            columns=["parameter", "value"],
            data=[
                ["start_time", self.start_time],
                ["step_time", self.step_time],
                ["prefix", self.prefix],
                ["suffix", self.suffix],
                ["size", self.size],
                ["x_shift", self.x_shift],
                ["y_shift", self.y_shift],
            ],
        )
        return df


@dataclass
class DataStorage:
    """Stores data for the GUI.

    Most of the attributes are stored as either a value_callback or a dataframe_storage object.
    Both of these objects are wrappers around the actual data that are used to trigger the
    appropriate actions when the data is changed.


    Attributes
    ----------
    file_name : file name of the input file
    original_data : original, unfiltered data
    filtered_data : filtered data based on the filter parameters set in the filter widget
    arcos_binarization : stores the binarization of the data for arcos
    arcos_output : stores the most recent output from arcos
    arcos_stats : stores the most recent stats from arcos
    columns : stores the column names of the data relevant for the analysis
    arcos_parameters : stores the parameters for arcos
    timestamp_parameters : stores the parameters for the timestamp dialog
    min_max_meas: stores the min and max values of the measurement
    colormaps: stores the colormap currently selected for the measurement

    Methods
    -------
    reset_all_attributes(trigger_callbacks=False)
        Resets all attributes to their default values. If trigger_callbacks is True, the
        callbacks of all attributes are triggered.
    reset_relevant_attributes(trigger_callbacks=False)
        Resets all attributes that are relevant for the analysis to their default values.
        If trigger_callbacks is True, the callbacks of all attributes are triggered.


    """

    _file_name: value_callback = field(
        default_factory=lambda: value_callback(".", value_name="file_name")
    )
    _original_data: data_frame_storage = field(
        default_factory=lambda: data_frame_storage(
            pd.DataFrame(), value_name="original_data"
        )
    )
    _filtered_data: data_frame_storage = field(
        default_factory=lambda: data_frame_storage(
            pd.DataFrame(), value_name="filtered_data"
        )
    )
    _arcos_binarization: data_frame_storage = field(
        default_factory=lambda: data_frame_storage(
            pd.DataFrame(), value_name="arcos_binarization"
        )
    )
    _arcos_output: data_frame_storage = field(
        default_factory=lambda: data_frame_storage(
            pd.DataFrame(), value_name="arcos_output"
        )
    )
    _arcos_stats: data_frame_storage = field(
        default_factory=lambda: data_frame_storage(
            pd.DataFrame(), value_name="arcos_stats"
        )
    )
    _columns: columnnames = field(default_factory=columnnames)
    _arcos_parameters: arcos_parameters = field(default_factory=arcos_parameters)
    min_max_meas: tuple = field(default=(0, 0.5))
    colormaps: list = field(default_factory=lambda: list(AVAILABLE_COLORMAPS))
    point_size = 10
    _selected_object_id: value_callback = field(
        default_factory=lambda: value_callback(None, value_name="selected_object_id")
    )
    lut: str = "inferno"
    _timestamp_parameters: value_callback = field(
        default_factory=lambda: value_callback(
            timestamp_parameters(), value_name="timestamp_parameters"
        )
    )
    verbose: bool = False

    def reset_all_attributes(self, trigger_callback=False):
        """resets all attributes to their default values.

        Parameters
        ----------
        trigger_callback : bool, optional
            if True, the callback function of the value_callback attributes will be triggered, by default False.
        """
        self.toggle_callback_block(not trigger_callback)
        self._file_name.value = "."
        self._original_data.value = pd.DataFrame()
        self._filtered_data.value = pd.DataFrame()
        self._arcos_binarization.value = pd.DataFrame()
        self._arcos_output.value = pd.DataFrame()
        self._arcos_stats.value = pd.DataFrame()
        self._columns = columnnames()
        self._arcos_parameters.reset_all_parameters()
        self.min_max_meas = (0, 0.5)
        self.colormaps = list(AVAILABLE_COLORMAPS)
        self.point_size = 10
        self._selected_object_id.value = None
        self.lut = "inferno"
        self._timestamp_parameters.value = timestamp_parameters()
        self.verbose = False
        self.toggle_callback_block(False)

    def reset_relevant_attributes(self, trigger_callback=False):
        """Resets relevant attributes to their default values.

        Parameters
        ----------
        trigger_callback : bool, optional
            If True, the callback function of the attributes will be triggered, by default False.
        """
        self.toggle_callback_block(not trigger_callback)
        self.filtered_data.value = pd.DataFrame()
        self.arcos_binarization.value = pd.DataFrame()
        self.arcos_output.value = pd.DataFrame()
        self.arcos_stats.value = pd.DataFrame()
        self.selected_object_id.value = None
        self.toggle_callback_block(False)

    def reset_arcos_data(self):
        """Resets all arcos related attributes to their default values."""
        self.arcos_binarization.value = pd.DataFrame()
        self.arcos_output.value = pd.DataFrame()
        self.arcos_stats.value = pd.DataFrame()

    def toggle_callback_block(self, block: bool | None):
        """Blocks or unblocks the callback functions of all attributes.

        Parameters
        ----------
        block : bool | None
            If True, the callback functions are blocked. If False, the callback functions are unblocked.
            If None, the callback functions are toggled.
        """
        self.file_name.toggle_callback_block(block)
        self.original_data.toggle_callback_block(block)
        self.filtered_data.toggle_callback_block(block)
        self.arcos_binarization.toggle_callback_block(block)
        self.arcos_output.toggle_callback_block(block)
        self.arcos_stats.toggle_callback_block(block)
        self.arcos_parameters.toggle_callback_block(block)
        self.selected_object_id.toggle_callback_block(block)
        self.timestamp_parameters.toggle_callback_block(block)

    def set_verbose(self, verbose: bool):
        """Sets the verbose attribute of all attributes to the given value.

        Parameters
        ----------
        verbose : bool
            The value to which the verbose attribute will be set.
        """
        self.verbose = verbose
        self.file_name.verbose = verbose
        self.original_data.verbose = verbose
        self.filtered_data.verbose = verbose
        self.arcos_binarization.verbose = verbose
        self.arcos_output.verbose = verbose
        self.arcos_stats.verbose = verbose
        self.selected_object_id.verbose = verbose
        self.timestamp_parameters.verbose = verbose
        self.arcos_parameters.set_verbose(verbose)

    @property
    def file_name(self):
        """Returns the file name."""
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        """Set the file name."""
        self._file_name.value = value

    @property
    def original_data(self):
        """Returns the original data."""
        return self._original_data

    @original_data.setter
    def original_data(self, value):
        """Set the original data."""
        self._original_data.value = value

    @property
    def filtered_data(self):
        """Returns the filtered data."""
        return self._filtered_data

    @filtered_data.setter
    def filtered_data(self, value):
        """Set the filtered data."""
        self._filtered_data.value = value

    @property
    def arcos_output(self):
        """Returns the arcos output data."""
        return self._arcos_output

    @arcos_output.setter
    def arcos_output(self, value):
        """Set the arcos output data."""
        self._arcos_output.value = value

    @property
    def columns(self):
        """Returns the columns attribute."""
        return self._columns

    @columns.setter
    def columns(self, value):
        """Set the columns attribute."""
        if not isinstance(value, columnnames):
            raise ValueError(f"columns must be of type {columnnames}")
        self._columns = value

    @property
    def arcos_stats(self):
        """Returns the arcos stats data."""
        return self._arcos_stats

    @arcos_stats.setter
    def arcos_stats(self, value):
        """Set the arcos stats data."""
        self._arcos_stats.value = value

    @property
    def arcos_binarization(self):
        """Returns the arcos binarization data."""
        return self._arcos_binarization

    @arcos_binarization.setter
    def arcos_binarization(self, value):
        """Set the arcos binarization data."""
        self._arcos_binarization.value = value

    @property
    def selected_object_id(self):
        """Returns the selected object id."""
        return self._selected_object_id

    @selected_object_id.setter
    def selected_object_id(self, value):
        """Sets the selected object id."""
        self._selected_object_id.value = value

    @property
    def arcos_parameters(self):
        """Returns the arcos parameters."""
        return self._arcos_parameters

    @arcos_parameters.setter
    def arcos_parameters(self, value):
        """Sets the arcos parameters."""
        if not isinstance(value, arcos_parameters):
            raise ValueError(f"Data must be of type {arcos_parameters}")
        self._arcos_parameters = value

    @property
    def timestamp_parameters(self):
        """Returns the timestamp parameters."""
        return self._timestamp_parameters

    @timestamp_parameters.setter
    def timestamp_parameters(self, value):
        if not isinstance(value, timestamp_parameters):
            raise ValueError(f"Data must be of type {timestamp_parameters}")
        self._timestamp_parameters.value = value

    def load_data(self, filename, trigger_callback=True):
        """Loads data from a csv file."""
        if trigger_callback:
            self.original_data = pd.read_csv(filename)
        else:
            self.original_data._value = pd.read_csv(filename)

    def __eq__(self, other):
        if isinstance(other, DataStorage):
            try:
                pd.testing.assert_frame_equal(
                    self._original_data.value, other._original_data.value
                )
                pd.testing.assert_frame_equal(
                    self._filtered_data.value, other._filtered_data.value
                )
                pd.testing.assert_frame_equal(
                    self._arcos_binarization.value, other._arcos_binarization.value
                )
                pd.testing.assert_frame_equal(
                    self._arcos_output.value, other._arcos_output.value
                )
                pd.testing.assert_frame_equal(
                    self._arcos_stats.value, other._arcos_stats.value
                )
                return (
                    self._columns == other._columns
                    and self._file_name == other._file_name
                    and self._arcos_parameters == other._arcos_parameters
                    and self.min_max_meas == other.min_max_meas
                    and self.colormaps == other.colormaps
                    and self.point_size == other.point_size
                    and self._selected_object_id.value
                    == other._selected_object_id.value
                    and self.lut == other.lut
                    and self._timestamp_parameters.value
                    == other._timestamp_parameters.value
                    and self.verbose == other.verbose
                )
            except AssertionError:
                return False
        return False


if __name__ == "__main__":
    ds = DataStorage()
    ds.timestamp_parameters.value_changed_connect(
        lambda: print("original data changed")
    )
    print(ds.filtered_data.value.empty)
    # # ds.load_data("C:/Users/benig/test.csv")
    # print(ds.columns)
    # print(ds.original_data)
