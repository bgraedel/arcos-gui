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

    Methods:
        value_changed_connect: Register a callback function.
        unregister_callback: Unregister a callback function.
    """

    _value: pd.DataFrame = field(default_factory=pd.DataFrame)
    _callbacks: list = field(default_factory=list)
    verbous = False

    @property
    def value(self):
        """Return the value attribute."""
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self._notify_observers()

    def _notify_observers(self):
        for callback in self._callbacks:
            if self.verbous:
                print(f"data_frame_storage: value changed executing {callback}")
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

    Methods
    -------
    value_changed_connect: Register a callback function.
    unregister_callback: Unregister a callback function.
    """

    _value: Union[int, str, None, Any]
    _callbacks: list = field(default_factory=list)
    verbous = False

    @property
    def value(self):
        """Get the value that is stored."""
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self._notify_observers()

    def _notify_observers(self):
        for callback in self._callbacks:
            if self.verbous:
                print(f"value_calback: value changed, executing {callback}")
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

    def __repr__(self):
        return repr(self._value)

    def __eq__(self, other):
        return self._value == other


@dataclass
class columnnames:
    """Stores column names for the dataframes."""

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
    """Stores the parameters for the arcos algorithm that can be set in the arcos widget."""

    _interpolate_meas: value_callback = field(
        default_factory=lambda: value_callback(False)
    )
    _clip_meas: value_callback = field(default_factory=lambda: value_callback(False))
    _clip_low: value_callback = field(default_factory=lambda: value_callback(0.0))
    _clip_high: value_callback = field(default_factory=lambda: value_callback(0.0))
    _smooth_k: value_callback = field(default_factory=lambda: value_callback(0))
    _bias_k: value_callback = field(default_factory=lambda: value_callback(0))
    _bias_method: value_callback = field(default_factory=lambda: value_callback("none"))
    _polyDeg: value_callback = field(default_factory=lambda: value_callback(0))
    _bin_threshold: value_callback = field(default_factory=lambda: value_callback(0.0))
    _bin_peak_threshold: value_callback = field(
        default_factory=lambda: value_callback(0.0)
    )
    _eps_method: value_callback = field(
        default_factory=lambda: value_callback("manual")
    )
    _neighbourhood_size: value_callback = field(
        default_factory=lambda: value_callback(0.0)
    )
    _epsPrev: value_callback = field(default_factory=lambda: value_callback(0.0))
    _min_clustersize: value_callback = field(default_factory=lambda: value_callback(0))
    _nprev_spinbox: value_callback = field(default_factory=lambda: value_callback(0))
    _min_dur: value_callback = field(default_factory=lambda: value_callback(0))
    _total_event_size: value_callback = field(default_factory=lambda: value_callback(0))
    _add_convex_hull: value_callback = field(
        default_factory=lambda: value_callback(True)
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
                ["nprev_spinbox", self.nprev_spinbox.value],
                ["min_dur", self.min_dur.value],
                ["total_event_size", self.total_event_size.value],
            ],
        )
        df["value"] = df["value"].astype(str)
        return df

    def reset_values(self, trigger_callback=True):
        """resets all values to default"""
        if trigger_callback:
            self._interpolate_meas.value = False
            self._clip_meas.value = False
            self._clip_low.value = 0.0
            self._clip_high.value = 0.0
            self._smooth_k.value = 0
            self._bias_k.value = 0
            self._bias_method.value = "none"
            self._polyDeg.value = 0
            self._bin_threshold.value = 0.0
            self._bin_peak_threshold.value = 0.0
            self._eps_method.value = "manual"
            self._neighbourhood_size.value = 0.0
            self._epsPrev.value = 0.0
            self._min_clustersize.value = 0
            self._nprev_spinbox.value = 0
            self._min_dur.value = 0
            self._total_event_size.value = 0
            self._add_convex_hull.value = True
        else:
            self._interpolate_meas.value = False
            self._clip_meas.value = False
            self._clip_low.value = 0.0
            self._clip_high.value = 0.0
            self._smooth_k.value = 0
            self._bias_k.value = 0
            self._bias_method.value = "none"
            self._polyDeg.value = 0
            self._bin_threshold.value = 0.0
            self._bin_peak_threshold.value = 0.0
            self._eps_method.value = "manual"
            self._neighbourhood_size.value = 0.0
            self._epsPrev.value = 0.0
            self._min_clustersize.value = 0
            self._nprev_spinbox.value = 0
            self._min_dur.value = 0
            self._total_event_size.value = 0
            self._add_convex_hull.value = True

    def make_verbous(self):
        """makes the parameters verbous"""
        self.interpolate_meas.verbous = True
        self.clip_meas.verbous = True
        self.clip_low.verbous = True
        self.clip_high.verbous = True
        self.smooth_k.verbous = True
        self.bias_k.verbous = True
        self.bias_method.verbous = True
        self.polyDeg.verbous = True
        self.bin_threshold.verbous = True
        self.bin_peak_threshold.verbous = True
        self.eps_method.verbous = True
        self.neighbourhood_size.verbous = True
        self.epsPrev.verbous = True
        self.min_clustersize.verbous = True
        self.nprev_spinbox.verbous = True
        self.min_dur.verbous = True
        self.total_event_size.verbous = True
        self.add_convex_hull.verbous = True

    def make_quiet(self):
        """makes the parameters quiet"""
        self.interpolate_meas.verbous = False
        self.clip_meas.verbous = False
        self.clip_low.verbous = False
        self.clip_high.verbous = False
        self.smooth_k.verbous = False
        self.bias_k.verbous = False
        self.bias_method.verbous = False
        self.polyDeg.verbous = False
        self.bin_threshold.verbous = False
        self.bin_peak_threshold.verbous = False
        self.eps_method.verbous = False
        self.neighbourhood_size.verbous = False
        self.epsPrev.verbous = False
        self.min_clustersize.verbous = False
        self.nprev_spinbox.verbous = False
        self.min_dur.verbous = False
        self.total_event_size.verbous = False
        self.add_convex_hull.verbous = False

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
    def nprev_spinbox(self):
        """nprev spinbox"""
        return self._nprev_spinbox

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
    """Stores the parameters for the timestamp options that can be set in the timestamp widget"""

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
    """

    _file_name: value_callback = field(default_factory=lambda: value_callback("."))
    _original_data: data_frame_storage = field(
        default_factory=lambda: data_frame_storage(pd.DataFrame())
    )
    _filtered_data: data_frame_storage = field(
        default_factory=lambda: data_frame_storage(pd.DataFrame())
    )
    _arcos_binarization: data_frame_storage = field(
        default_factory=lambda: data_frame_storage(pd.DataFrame())
    )
    _arcos_output: data_frame_storage = field(
        default_factory=lambda: data_frame_storage(pd.DataFrame())
    )
    _arcos_stats: data_frame_storage = field(
        default_factory=lambda: data_frame_storage(pd.DataFrame())
    )
    _columns: columnnames = field(default_factory=columnnames)
    _arcos_parameters: arcos_parameters = field(default_factory=arcos_parameters)
    min_max_meas: tuple = field(default=(0, 0.5))
    colormaps: list = field(default_factory=lambda: list(AVAILABLE_COLORMAPS))
    point_size = 10
    _selected_object_id: value_callback = field(
        default_factory=lambda: value_callback(None)
    )
    lut: str = "inferno"
    _timestamp_parameters: value_callback = field(
        default_factory=lambda: value_callback(timestamp_parameters())
    )
    verbous: bool = False

    def reset_all_attributes(self, trigger_callback=False):
        """resets all attributes to their default values.

        Parameters
        ----------
        trigger_callback : bool, optional
            if True, the callback function of the value_callback attributes will be triggered, by default False.
        """
        if trigger_callback:
            self._file_name.value = "."
            self._original_data.value = pd.DataFrame()
            self._filtered_data.value = pd.DataFrame()
            self._arcos_binarization.value = pd.DataFrame()
            self._arcos_output.value = pd.DataFrame()
            self._arcos_stats.value = pd.DataFrame()
            self._columns = columnnames()
            self._arcos_parameters.reset_values()
            self.min_max_meas = (0, 0.5)
            self.colormaps = list(AVAILABLE_COLORMAPS)
            self.point_size = 10
            self._selected_object_id.value = None
            self.lut = "inferno"
            self._timestamp_parameters.value = timestamp_parameters()
            self.verbous = False
        else:
            self._file_name._value = "."
            self._original_data._value = pd.DataFrame()
            self._filtered_data._value = pd.DataFrame()
            self._arcos_binarization._value = pd.DataFrame()
            self._arcos_output._value = pd.DataFrame()
            self._arcos_stats._value = pd.DataFrame()
            self._columns = columnnames()
            self._arcos_parameters.reset_values(trigger_callback=False)
            self.min_max_meas = (0, 0.5)
            self.colormaps = list(AVAILABLE_COLORMAPS)
            self.point_size = 10
            self._selected_object_id._value = None
            self.lut = "inferno"
            self._timestamp_parameters._value = timestamp_parameters()
            self.verbous = False

    def reset_relevant_attributes(self, trigger_callback=False):
        """Resets relevant attributes to their default values.

        Parameters
        ----------
        trigger_callback : bool, optional
            If True, the callback function of the attributes will be triggered, by default False.
        """
        if trigger_callback:
            self._filtered_data.value = pd.DataFrame()
            self._arcos_binarization.value = pd.DataFrame()
            self._arcos_output.value = pd.DataFrame()
            self._arcos_stats.value = pd.DataFrame()
            self._selected_object_id.value = None
        else:
            self._filtered_data._value = pd.DataFrame()
            self._arcos_binarization._value = pd.DataFrame()
            self._arcos_output._value = pd.DataFrame()
            self._arcos_stats._value = pd.DataFrame()
            self._selected_object_id._value = None

    def make_quiet(self):
        """Sets the verbous attribute of all attributes to False.

        This is useful for debugging."""
        self.verbous = False
        self._file_name.verbous = False
        self._original_data.verbous = False
        self._filtered_data.verbous = False
        self._arcos_binarization.verbous = False
        self._arcos_output.verbous = False
        self._arcos_stats.verbous = False
        self._selected_object_id.verbous = False
        self._timestamp_parameters.verbous = False
        self.arcos_parameters.make_quiet()

    def make_verbose(self):
        """Sets the verbous attribute of all attributes to True.

        This is useful for debugging."""
        self.verbous = True
        self._file_name.verbous = True
        self._original_data.verbous = True
        self._filtered_data.verbous = True
        self._arcos_binarization.verbous = True
        self._arcos_output.verbous = True
        self._arcos_stats.verbous = True
        self._selected_object_id.verbous = True
        self._timestamp_parameters.verbous = True
        self.arcos_parameters.make_verbous()

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
                    and self.verbous == other.verbous
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
