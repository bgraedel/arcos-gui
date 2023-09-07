"""Contains the data storage classes for the arcos_gui.

The data storage classes are used to store the data and the settings for the
different widgets. Moste of the attributes contain callbacks functionallity
which are used to update the widgets when the data changes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar, Union

import pandas as pd
from napari.utils.colormaps import AVAILABLE_COLORMAPS


@dataclass
class value_changed:
    """Inner class to provide a more intuitive API for connecting and disconnecting callbacks."""

    _outer_instance: value_callback

    def connect(self, callback: Callable) -> None:
        """Register a callback function."""
        self._outer_instance._callbacks.append(callback)

    def disconnect(self, callback: Callable) -> None:
        """Unregister a callback function."""
        self._outer_instance._callbacks.remove(callback)


T = TypeVar("T")


@dataclass
class value_callback(Generic[T]):
    _value: T
    value_changed: value_changed = field(
        init=False
    )  # Note: the type hint for value_changed needs to be defined
    _callbacks: list[Callable[[], None]] = field(default_factory=list)
    callbacks_blocked: bool = False
    value_name: str = "value_callback"
    verbose: bool = False

    def __post_init__(self):
        self.value_changed = value_changed(
            self
        )  # Note: the value_changed class needs to be defined

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, value: T):
        self._value = value
        self._notify_observers()

    def _notify_observers(self):
        if self.callbacks_blocked:
            return
        for callback in self._callbacks:
            if self.verbose:
                print(
                    f"value_callback: {self.value_name} changed. Executing {callback}"
                )
            callback()

    def toggle_callback_block(self, set_explicit: bool | None = None):
        if set_explicit is not None:
            self.callbacks_blocked = set_explicit
            return
        self.callbacks_blocked = not self.callbacks_blocked

    def toggle_verbose(self):
        self.verbose = not self.verbose

    def __repr__(self) -> str:
        return repr(self._value)

    def __eq__(self, other: Any) -> bool:
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

    # working on replacing "None" comparisons with direct comparisons to None
    frame_column: str = "frame"
    position_id: Union[str, None] = "position_id"
    object_id: Union[str, None] = "track_id"
    x_column: str = "x"
    y_column: str = "y"
    z_column: Union[str, None] = "z"
    measurement_column_1: str = "measurement"
    measurement_column_2: Union[str, None] = "measurement_2"
    additional_filter_column: Union[str, None] = "additional_filter"
    measurement_math_operation: Union[str, None] = None
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
            self.measurement_math_operation,
        ]

    @property
    def posCol(self):
        """returns a list of all coordinate columns"""
        if self.z_column:
            return [self.x_column, self.y_column, self.z_column]
        return [self.x_column, self.y_column]

    @property
    def vcolscore(self):
        """returns a list of core columns columns"""
        if self.z_column:
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
                ["measurement_math_operatoin", self.measurement_math_operation],
                ["measurement_bin", self.measurement_bin],
                ["measurement_resc", self.measurement_resc],
                ["collid_name", self.collid_name],
                ["measurement_column", self.measurement_column],
            ],
        )
        return df


@dataclass(frozen=True)
class ArcosParameters:
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

    interpolate_meas: value_callback[bool] = field(
        default_factory=lambda: value_callback(False, value_name="interpolate_meas")
    )
    clip_meas: value_callback[bool] = field(
        default_factory=lambda: value_callback(False, value_name="clip_meas")
    )
    clip_low: value_callback[float] = field(
        default_factory=lambda: value_callback(0.0, value_name="clip_low")
    )
    clip_high: value_callback[float] = field(
        default_factory=lambda: value_callback(1.0, value_name="clip_high")
    )
    smooth_k: value_callback[int] = field(
        default_factory=lambda: value_callback(1, value_name="smooth_k")
    )
    bias_k: value_callback[int] = field(
        default_factory=lambda: value_callback(5, value_name="bias_k")
    )
    bias_method: value_callback[str] = field(
        default_factory=lambda: value_callback("none", value_name="bias_method")
    )
    polyDeg: value_callback[int] = field(
        default_factory=lambda: value_callback(1, value_name="polyDeg")
    )
    bin_threshold: value_callback[float] = field(
        default_factory=lambda: value_callback(0.5, value_name="bin_threshold")
    )
    bin_peak_threshold: value_callback[float] = field(
        default_factory=lambda: value_callback(0.5, value_name="bin_peak_threshold")
    )
    eps_method: value_callback[str] = field(
        default_factory=lambda: value_callback("manual", value_name="eps_method")
    )
    neighbourhood_size: value_callback[float] = field(
        default_factory=lambda: value_callback(20, value_name="neighbourhood_size")
    )
    epsPrev: value_callback[float] = field(
        default_factory=lambda: value_callback(20, value_name="epsPrev")
    )
    min_clustersize: value_callback[int] = field(
        default_factory=lambda: value_callback(5, value_name="min_clustersize")
    )
    nprev: value_callback[int] = field(
        default_factory=lambda: value_callback(1, value_name="nprev")
    )
    min_dur: value_callback[int] = field(
        default_factory=lambda: value_callback(1, value_name="min_dur")
    )
    total_event_size: value_callback[int] = field(
        default_factory=lambda: value_callback(5, value_name="total_event_size")
    )
    add_convex_hull: value_callback[bool] = field(
        default_factory=lambda: value_callback(True, value_name="add_convex_hull")
    )
    add_all_cells: value_callback[bool] = field(
        default_factory=lambda: value_callback(True, value_name="add_all_cells")
    )
    add_bin_cells: value_callback[bool] = field(
        default_factory=lambda: value_callback(True, value_name="add_bin_cells")
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
        self, arcos_parameters_object: ArcosParameters, trigger_callback: bool = True
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
        self.add_all_cells.verbose = verbose
        self.add_bin_cells.verbose = verbose

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
        self.add_all_cells.toggle_callback_block(block)
        self.add_bin_cells.toggle_callback_block(block)


@dataclass(frozen=True)
class DataStorage:
    """Stores data for the GUI.

    Attributes are stored as a value_callback object.
    Both of these objects are wrappers around the actual data that are used to trigger the
    appropriate actions when the data is changed. Accessing the attributes value


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

    file_name: value_callback[str] = field(
        default_factory=lambda: value_callback(".", value_name="file_name")
    )
    original_data: value_callback[pd.DataFrame] = field(
        default_factory=lambda: value_callback(
            pd.DataFrame(), value_name="original_data"
        )
    )
    filtered_data: value_callback[pd.DataFrame] = field(
        default_factory=lambda: value_callback(
            pd.DataFrame(), value_name="filtered_data"
        )
    )
    arcos_binarization: value_callback[pd.DataFrame] = field(
        default_factory=lambda: value_callback(
            pd.DataFrame(), value_name="arcos_binarization"
        )
    )
    arcos_output: value_callback[pd.DataFrame] = field(
        default_factory=lambda: value_callback(
            pd.DataFrame(), value_name="arcos_output"
        )
    )
    arcos_stats: value_callback[pd.DataFrame] = field(
        default_factory=lambda: value_callback(pd.DataFrame(), value_name="arcos_stats")
    )
    columns: value_callback[columnnames] = field(
        default_factory=lambda: value_callback(columnnames(), value_name="columns")
    )
    arcos_parameters: value_callback[ArcosParameters] = field(
        default_factory=lambda: value_callback(
            ArcosParameters(), value_name="arcos_parameters"
        )
    )
    min_max_meas: value_callback[tuple] = field(
        default_factory=lambda: value_callback((0, 0.5), value_name="min_max_meas")
    )
    colormaps: value_callback[list] = field(
        default_factory=lambda: value_callback(
            list(AVAILABLE_COLORMAPS), value_name="colormaps"
        )
    )
    point_size: value_callback[float] = field(
        default_factory=lambda: value_callback(10, value_name="point_size")
    )
    selected_object_id: value_callback[int | None] = field(
        default_factory=lambda: value_callback(None, value_name="selected_object_id")
    )
    lut: value_callback[str] = field(
        default_factory=lambda: value_callback("inferno", value_name="lut")
    )
    output_order: value_callback[str] = field(
        default_factory=lambda: value_callback("txyz", value_name="output_order")
    )

    def reset_all_attributes(self, trigger_callback=False):
        """resets all attributes to their default values.

        Parameters
        ----------
        trigger_callback : bool, optional
            if True, the callback function of the value_callback attributes will be triggered, by default False.
        """
        self.toggle_callback_block(not trigger_callback)
        self.file_name.value = "."
        self.original_data.value = pd.DataFrame()
        self.filtered_data.value = pd.DataFrame()
        self.arcos_binarization.value = pd.DataFrame()
        self.arcos_output.value = pd.DataFrame()
        self.arcos_stats.value = pd.DataFrame()
        self.columns.value = columnnames()
        self.arcos_parameters.value.reset_all_parameters()
        self.min_max_meas.value = (0, 0.5)
        self.colormaps.value = list(AVAILABLE_COLORMAPS)
        self.point_size.value = 10
        self.selected_object_id.value = None
        self.lut.value = "inferno"
        self.output_order.value = "txyz"
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
        self.arcos_parameters.value.toggle_callback_block(block)
        self.selected_object_id.toggle_callback_block(block)

    def set_verbose(self, verbose: bool):
        """Sets the verbose attribute of all attributes to the given value.

        Parameters
        ----------
        verbose : bool
            The value to which the verbose attribute will be set.
        """
        self.file_name.verbose = verbose
        self.original_data.verbose = verbose
        self.filtered_data.verbose = verbose
        self.arcos_binarization.verbose = verbose
        self.arcos_output.verbose = verbose
        self.arcos_stats.verbose = verbose
        self.selected_object_id.verbose = verbose
        self.arcos_parameters.value.set_verbose(verbose)

    def load_data(self, filename, trigger_callback=True):
        """Loads data from a csv file."""
        if trigger_callback:
            self.original_data.value = pd.read_csv(filename)
        else:
            self.original_data._value = pd.read_csv(filename)

    def __eq__(self, other):
        if not isinstance(other, DataStorage):
            return False

        dataframes_to_check = [
            ("original_data", self.original_data.value, other.original_data.value),
            ("filtered_data", self.filtered_data.value, other.filtered_data.value),
            (
                "arcos_binarization",
                self.arcos_binarization.value,
                other.arcos_binarization.value,
            ),
            ("arcos_output", self.arcos_output.value, other.arcos_output.value),
            ("arcos_stats", self.arcos_stats.value, other.arcos_stats.value),
        ]

        for name, df1, df2 in dataframes_to_check:
            if not self._are_dataframes_equal(df1, df2):
                return False

        attributes_to_check = [
            "columns",
            "file_name",
            "arcos_parameters",
            "min_max_meas",
            "colormaps",
            "point_size",
            "selected_object_id",
            "lut",
        ]

        for attr in attributes_to_check:
            if getattr(self, attr) != getattr(other, attr):
                return False

        return True

    def _are_dataframes_equal(self, df1, df2):
        try:
            pd.testing.assert_frame_equal(df1, df2)
            return True
        except AssertionError:
            return False


if __name__ == "__main__":
    ds = DataStorage()
    ds.columns.value_changed.connect(lambda: print("columns changed"))
    ds.columns.value = columnnames()
