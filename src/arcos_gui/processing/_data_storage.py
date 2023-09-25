"""Contains the data storage classes for the arcos_gui.

The data storage classes are used to store the data and the settings for the
different widgets. Moste of the attributes contain callbacks functionallity
which are used to update the widgets when the data changes."""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any, Callable, Generic, Literal, Sequence, TypeVar, Union, cast

import pandas as pd
import yaml
from arcos_gui.tools import ALLOWED_SETTINGS, ARCOSPARAMETERS_DEFAULTS


@dataclass
class value_changed:
    """Inner class to provide a more intuitive API for connecting and disconnecting callbacks."""

    _outer_instance: value_callback

    def connect(self, callback: Callable) -> None:
        """Register a callback function."""
        if callback not in self._outer_instance._callbacks and callable(callback):
            self._outer_instance._callbacks.append(callback)
        else:
            raise ValueError(
                "Callback is already registered or not callable. Use disconnect() to unregister."
            )

    def disconnect(self, callback: Callable) -> None:
        """Unregister a callback function."""
        if callback in self._outer_instance._callbacks:
            self._outer_instance._callbacks.remove(callback)
        else:
            raise ValueError("Callback is not registered.")


T = TypeVar("T")


@dataclass
class value_callback(Generic[T]):
    _value: T
    allowed_types: tuple[type, ...] = field(default_factory=tuple)
    value_changed: value_changed = field(init=False)
    _callbacks: list[Callable[[], None]] = field(default_factory=list, init=False)
    callbacks_blocked: bool = False
    value_name: str = "value_callback"
    verbose: bool = False
    missed_callbacks: int = 0

    def __post_init__(self):
        self.value_changed = value_changed(self)

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, value: T):
        if not isinstance(value, self.allowed_types):
            raise TypeError(
                f"Value for {self.value_name} must be of type {type(self._value)}"
            )

        self._value = value
        self._notify_observers()

    def _notify_observers(self):
        if self.callbacks_blocked:
            self.missed_callbacks += 1
            return
        self._emit()

    def _emit(self):
        for callback in self._callbacks:
            if self.verbose:
                print(
                    f"value_callback: {self.value_name} changed. Executing {callback}"
                )
            callback()

    def emit(self, only_missed: bool = False):
        if only_missed and self.missed_callbacks > 0:
            self._emit()
            self.missed_callbacks = 0
        else:
            self._notify_observers()

    def toggle_callback_block(self, set_explicit: bool | None = None):
        if set_explicit is not None:
            self.callbacks_blocked = set_explicit
        else:
            self.callbacks_blocked = not self.callbacks_blocked
        if not self.callbacks_blocked:
            self.missed_callbacks = 0

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
        data = [(attr.name, getattr(self, attr.name)) for attr in fields(self)]
        df = pd.DataFrame(columns=["Column", "value"], data=data)
        df["value"] = df["value"].astype(str)
        return df


def create_value_callback(default, name):
    return field(default_factory=lambda: value_callback(default[name], value_name=name))


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
        default_factory=lambda: value_callback(
            False, (bool,), value_name="interpolate_meas"
        )
    )
    clip_meas: value_callback[bool] = field(
        default_factory=lambda: value_callback(False, (bool,), value_name="clip_meas")
    )
    clip_low: value_callback[float] = field(
        default_factory=lambda: value_callback(0.0, (float,), value_name="clip_low")
    )
    clip_high: value_callback[float] = field(
        default_factory=lambda: value_callback(1.0, (float,), value_name="clip_high")
    )
    smooth_k: value_callback[int] = field(
        default_factory=lambda: value_callback(1, (int,), value_name="smooth_k")
    )
    bias_k: value_callback[int] = field(
        default_factory=lambda: value_callback(5, (int,), value_name="bias_k")
    )
    bias_method: value_callback[str] = field(
        default_factory=lambda: value_callback("none", (str,), value_name="bias_method")
    )
    polyDeg: value_callback[int] = field(
        default_factory=lambda: value_callback(1, (int,), value_name="polyDeg")
    )
    bin_threshold: value_callback[float] = field(
        default_factory=lambda: value_callback(
            0.5, (float, int), value_name="bin_threshold"
        )
    )
    bin_peak_threshold: value_callback[float] = field(
        default_factory=lambda: value_callback(
            0.5, (float, int), value_name="bin_peak_threshold"
        )
    )
    eps_method: value_callback[str] = field(
        default_factory=lambda: value_callback(
            "manual", (str,), value_name="eps_method"
        )
    )
    neighbourhood_size: value_callback[float] = field(
        default_factory=lambda: value_callback(
            20.0, (float, int), value_name="neighbourhood_size"
        )
    )
    epsPrev: value_callback[float] = field(
        default_factory=lambda: value_callback(
            20.0, (float, int, type(None)), value_name="epsPrev"
        )
    )
    min_clustersize: value_callback[int] = field(
        default_factory=lambda: value_callback(5, (int,), value_name="min_clustersize")
    )
    nprev: value_callback[int] = field(
        default_factory=lambda: value_callback(1, (int,), value_name="nprev")
    )
    min_dur: value_callback[int] = field(
        default_factory=lambda: value_callback(1, (int,), value_name="min_dur")
    )
    total_event_size: value_callback[int] = field(
        default_factory=lambda: value_callback(5, (int,), value_name="total_event_size")
    )
    add_convex_hull: value_callback[bool] = field(
        default_factory=lambda: value_callback(
            True, (bool,), value_name="add_convex_hull"
        )
    )
    add_all_cells: value_callback[bool] = field(
        default_factory=lambda: value_callback(
            True, (bool,), value_name="add_all_cells"
        )
    )
    add_bin_cells: value_callback[bool] = field(
        default_factory=lambda: value_callback(
            True, (bool,), value_name="add_bin_cells"
        )
    )
    bin_advanded_settings: value_callback[bool] = field(
        default_factory=lambda: value_callback(
            False, (bool,), value_name="bin_advanded_settings"
        )
    )
    detect_advanced_options: value_callback[bool] = field(
        default_factory=lambda: value_callback(
            False, (bool,), value_name="detect_advanced_options"
        )
    )

    @property
    def as_dataframe(self):
        """creates a dataframe from the arcos parameters"""
        data = [(attr.name, getattr(self, attr.name).value) for attr in fields(self)]
        df = pd.DataFrame(columns=["parameter", "value"], data=data)
        df["value"] = df["value"].astype(str)
        return df

    def set_all_parameters(
        self, arcos_parameters_object: ArcosParameters, trigger_callback: bool = True
    ):
        """sets all parameters to the values of another ArcosParameters object."""
        self.toggle_callback_block(not trigger_callback)
        for _field in fields(arcos_parameters_object):
            getattr(self, _field.name).value = getattr(
                arcos_parameters_object, _field.name
            ).value
        self.toggle_callback_block(False)

    def reset_all_parameters(self, trigger_callback: bool = True):
        """resets all values to their default values."""
        self.toggle_callback_block(not trigger_callback)
        for _field in fields(self):
            getattr(self, _field.name).value = ARCOSPARAMETERS_DEFAULTS[_field.name]
        self.toggle_callback_block(False)

    def set_verbose(self, verbose: bool = False):
        """sets the verbose parameter for all attributes."""
        for _field in fields(self):
            getattr(self, _field.name).verbose = verbose

    def toggle_callback_block(self, block: Union[bool, None] = None):
        """blocks or unblocks all callbacks."""
        for _field in fields(self):
            getattr(self, _field.name).toggle_callback_block(block)

    def emit(self, only_missed: bool = False):
        """emits all callbacks.

        Parameters
        ----------
        only_missed : bool, optional
            if True, only the missed callbacks will be emitted, by default False.
        """
        for _field in fields(self):
            getattr(self, _field.name).emit(only_missed=only_missed)


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
        default_factory=lambda: value_callback(".", (str,), value_name="file_name")
    )
    original_data: value_callback[pd.DataFrame] = field(
        default_factory=lambda: value_callback(
            pd.DataFrame(), (pd.DataFrame,), value_name="original_data"
        )
    )
    filtered_data: value_callback[pd.DataFrame] = field(
        default_factory=lambda: value_callback(
            pd.DataFrame(), (pd.DataFrame,), value_name="filtered_data"
        )
    )
    arcos_binarization: value_callback[pd.DataFrame] = field(
        default_factory=lambda: value_callback(
            pd.DataFrame(), (pd.DataFrame,), value_name="arcos_binarization"
        )
    )
    arcos_output: value_callback[pd.DataFrame] = field(
        default_factory=lambda: value_callback(
            pd.DataFrame(), (pd.DataFrame,), value_name="arcos_output"
        )
    )
    arcos_stats: value_callback[pd.DataFrame] = field(
        default_factory=lambda: value_callback(
            pd.DataFrame(), (pd.DataFrame,), value_name="arcos_stats"
        )
    )
    columns: value_callback[columnnames] = field(
        default_factory=lambda: value_callback(
            columnnames(), (columnnames,), value_name="columns"
        )
    )
    arcos_parameters: value_callback[ArcosParameters] = field(
        default_factory=lambda: value_callback(
            ArcosParameters(), (ArcosParameters,), value_name="arcos_parameters"
        )
    )
    min_max_meas: value_callback[list] = field(
        default_factory=lambda: value_callback(
            [0.0, 0.5], (list,), value_name="min_max_meas"
        )
    )
    point_size: value_callback[float] = field(
        default_factory=lambda: value_callback(
            10.0, (float, int), value_name="point_size"
        )
    )
    selected_object_id: value_callback[int | None] = field(
        default_factory=lambda: value_callback(
            None, (int, type(None)), value_name="selected_object_id"
        )
    )
    lut: value_callback[str] = field(
        default_factory=lambda: value_callback("inferno", (str,), value_name="lut")
    )
    output_order: value_callback[str] = field(
        default_factory=lambda: value_callback(
            "txyz", (str,), value_name="output_order"
        )
    )
    min_max_tracklenght: value_callback[list] = field(
        default_factory=lambda: value_callback(
            [0, 1], (list,), value_name="min_max_tracklenght"
        )
    )

    def export_to_yaml(self, filepath: str):
        """Exports all attributes of DataStorage class to a YAML file, excluding those which are DataFrames.

        Parameters:
        filepath (str): The file path where the YAML file should be saved.
        """

        def extract_values(obj):
            """Recursive function to extract values from dataclasses and value_callback objects."""
            if isinstance(obj, value_callback):
                obj = obj.value
            if is_dataclass(obj):
                return {
                    f.name: extract_values(getattr(obj, f.name)) for f in fields(obj)
                }
            else:
                return obj

        data_dict = {
            f.name: extract_values(getattr(self, f.name))
            for f in fields(self)
            if not isinstance(getattr(self, f.name).value, pd.DataFrame)
        }

        # Writing the data dictionary to a YAML file
        with open(filepath, "w") as file:
            yaml.safe_dump(data_dict, file)

    def import_from_yaml(
        self,
        filepath: str,
        selected_attributes: Sequence[
            Literal[
                "file_name",
                "columns",
                "arcos_parameters",
                "min_max_meas",
                "point_size",
                "lut",
                "output_order",
                "min_max_tracklenght",
            ]
        ]
        | None = None,
    ):
        """Imports the parameters from a YAML file and updates the attributes of DataStorage class.

        Parameters:
        filepath (str): The file path where the YAML file is located.
        selected_attributes (Sequence[allowed_import_values] | None): A list of attributes to be imported.
            If None, all attributes will be imported. Defaults to None.
            Note: importing columns will reset all attributes.
        """
        if selected_attributes is None:
            _selected_attributes = cast(
                Sequence[
                    Literal[
                        "file_name",
                        "columns",
                        "arcos_parameters",
                        "min_max_meas",
                        "point_size",
                        "lut",
                        "output_order",
                        "min_max_tracklenght",
                    ]
                ],
                ALLOWED_SETTINGS,
            )
        else:
            _selected_attributes = selected_attributes

        # check if columns or file_name are in _selected_attributes
        if "columns" in _selected_attributes or "file_name" in _selected_attributes:
            self.reset_all_attributes()
            print("resetting all attributes")

        for attr in _selected_attributes:
            if attr not in ALLOWED_SETTINGS:
                raise ValueError(f"Cant import {attr} from YAML file.")

        self.toggle_callback_block(
            True
        )  # black all callbacks while importing to avoid unnecessary updates

        def update_attributes(obj, data_dict, skip_selected_check=True):
            """Recursive function to update attributes from a nested dictionary."""
            for key, value in data_dict.items():
                if key not in _selected_attributes and skip_selected_check:
                    continue
                attr = getattr(obj, key)
                if isinstance(attr, value_callback):
                    if is_dataclass(attr.value):
                        update_attributes(attr.value, value, skip_selected_check=False)
                    else:
                        attr.value = value
                else:
                    setattr(obj, key, value)

        with open(filepath) as file:
            data_dict = yaml.safe_load(file)

        update_attributes(self, data_dict)

        # manually trigger callbacks for all attributes that were not updated
        self.emit_callbacks(only_missed=True)
        self.toggle_callback_block(False)

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
        self.min_max_meas.value = [0, 0.5]
        self.point_size.value = 10
        self.selected_object_id.value = None
        self.lut.value = "inferno"
        self.output_order.value = "txyz"
        self.min_max_tracklenght.value = [0, 1]
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
        def recursive_toggle(obj, block):
            for _field in fields(obj):
                value_callback_field = getattr(obj, _field.name)
                if isinstance(value_callback_field, value_callback):
                    value_callback_field.toggle_callback_block(block)
                    if hasattr(value_callback_field, "value"):
                        nested_value = value_callback_field.value
                        if is_dataclass(nested_value):
                            recursive_toggle(nested_value, block)

        recursive_toggle(self, block)

    def set_callbacks_verbose(self, verbose: bool):
        def recursive_set_verbose(obj, verbose):
            for _field in fields(obj):
                value_callback_field = getattr(obj, _field.name)
                if isinstance(value_callback_field, value_callback):
                    value_callback_field.verbose = verbose
                    if hasattr(value_callback_field, "value"):
                        nested_value = value_callback_field.value
                        if is_dataclass(nested_value):
                            recursive_set_verbose(nested_value, verbose)

        recursive_set_verbose(self, verbose)

    def emit_callbacks(self, only_missed: bool = False):
        def recursive_emit(obj, only_missed):
            for _field in fields(obj):
                value_callback_field = getattr(obj, _field.name)
                if isinstance(value_callback_field, value_callback):
                    value_callback_field.emit(only_missed=only_missed)
                    if hasattr(value_callback_field, "value"):
                        nested_value = value_callback_field.value
                        if is_dataclass(nested_value):
                            recursive_emit(nested_value, only_missed)

        recursive_emit(self, only_missed)

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
