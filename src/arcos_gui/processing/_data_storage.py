from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union

import pandas as pd
from napari.utils.colormaps import AVAILABLE_COLORMAPS


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
            self.position_id,
            self.object_id,
            self.x_column,
            self.y_column,
            self.z_column,
            self.measurement_column_1,
            self.measurement_column_2,
            self.additional_filter_column,
            self.measurement_math_operatoin,
        ]

    @property
    def posCol_list(self):
        """returns a ist of position columns depending on wether a z coordinate column wsa selected or not."""
        if self.z_column != "None":
            posCols = [self.x_column, self.y_column, self.z_column]
            return posCols
        return [self.x_column, self.y_column]

    @property
    def coordinate_columns(self):
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


@dataclass
class arcos_parameters:
    """Stores the parameters for the arcos algorithm that can be set in the arcos widget"""

    interpolate_meas: bool = False
    clip_meas: bool = False
    clip_low: float = 0.0
    clip_high: float = 0.0
    smooth_k: int = 0
    bias_k: int = 0
    bias_method: str = "None"
    polyDeg: int = 0
    bin_threshold: float = 0.0
    bin_peak_threshold: float = 0.0
    neighbourhood_size: float = 0.0
    min_clustersize: float = 0.0
    nprev_spinbox: int = 0
    min_dur: int = 0
    total_event_size: int = 0

    @property
    def as_dataframe(self):
        """creates a dataframe from the arcos parameters"""
        df = pd.DataFrame(
            columns=["parameter", "value"],
            data=[
                ["interpolate_meas", self.interpolate_meas],
                ["clip_meas", self.clip_meas],
                ["clip_low", self.clip_low],
                ["clip_high", self.clip_high],
                ["smooth_k", self.smooth_k],
                ["bias_k", self.bias_k],
                ["bias_method", self.bias_method],
                ["polyDeg", self.polyDeg],
                ["bin_threshold", self.bin_threshold],
                ["bin_peak_threshold", self.bin_peak_threshold],
                ["neighbourhood_size", self.neighbourhood_size],
                ["min_clustersize", self.min_clustersize],
                ["nprev_spinbox", self.nprev_spinbox],
                ["min_dur", self.min_dur],
                ["total_event_size", self.total_event_size],
            ],
        )
        df["value"] = df["value"].astype(str)
        return df


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
class data_frame_storage:
    _value: pd.DataFrame = field(default_factory=pd.DataFrame)
    _callbacks: list = field(default_factory=list)
    verbous = False

    @property
    def value(self):
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
        self._callbacks.append(callback)

    def unregister_callback(self, callback):
        self._callbacks.remove(callback)

    def __repr__(self):
        return repr(self._value)


@dataclass
class value_calback:
    _value: Union[int, str, None]
    _callbacks: list = field(default_factory=list)
    verbous = False

    @property
    def value(self):
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
        self._callbacks.append(callback)

    def unregister_callback(self, callback):
        self._callbacks.remove(callback)

    def __repr__(self):
        return repr(self._value)


class DataStorage:
    """Stores data for the GUI."""

    def __init__(self):
        self._original_data: data_frame_storage = data_frame_storage(pd.DataFrame())
        self._filtered_data: data_frame_storage = data_frame_storage(pd.DataFrame())
        self._arcos_binarization: data_frame_storage = data_frame_storage(
            pd.DataFrame()
        )
        self._arcos_output: data_frame_storage = data_frame_storage(pd.DataFrame())
        self._arcos_stats: data_frame_storage = data_frame_storage(pd.DataFrame())
        self._columns: columnnames = columnnames()
        self._arcos_parameters: arcos_parameters = arcos_parameters()
        self.min_max_meas: tuple = (0, 0.5)
        self.colormaps = list(AVAILABLE_COLORMAPS)
        self.point_size = 10
        self._selected_object_id: value_calback = value_calback(None)
        self.lut = "inferno"
        self._filename_for_sample_data: value_calback(None) = value_calback(None)
        self._timestamp_parameters: value_calback = value_calback(
            timestamp_parameters()
        )
        self.verbous = False

    def reset_all_attributes(self, trigger_callback=False):
        if trigger_callback:
            self._original_data.value = pd.DataFrame()
            self._filtered_data.value = pd.DataFrame()
            self._arcos_binarization.value = pd.DataFrame()
            self._arcos_output.value = pd.DataFrame()
            self._arcos_stats.value = pd.DataFrame()
            self._columns = columnnames()
            self._arcos_parameters = arcos_parameters()
            self.min_max_meas = (0, 0.5)
            self.colormaps = list(AVAILABLE_COLORMAPS)
            self.point_size = 10
            self._selected_object_id.value = None
            self.lut = "inferno"
            self._filename_for_sample_data.value = None
            self._timestamp_parameters.value = timestamp_parameters()
            self.verbous = False
        else:
            self._original_data._value = pd.DataFrame()
            self._filtered_data._value = pd.DataFrame()
            self._arcos_binarization._value = pd.DataFrame()
            self._arcos_output._value = pd.DataFrame()
            self._arcos_stats._value = pd.DataFrame()
            self._columns = columnnames()
            self._arcos_parameters = arcos_parameters()
            self.min_max_meas = (0, 0.5)
            self.colormaps = list(AVAILABLE_COLORMAPS)
            self.point_size = 10
            self._selected_object_id._value = None
            self.lut = "inferno"
            self._filename_for_sample_data._value = None
            self._timestamp_parameters._value = timestamp_parameters()
            self.verbous = False

    def reset_relevant_attributes(self, trigger_callback=False):
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
        self.verbous = False
        self._original_data.verbous = False
        self._filtered_data.verbous = False
        self._arcos_binarization.verbous = False
        self._arcos_output.verbous = False
        self._arcos_stats.verbous = False
        self._selected_object_id.verbous = False
        self._filename_for_sample_data.verbous = False
        self._timestamp_parameters.verbous = False

    def make_verbose(self):
        self.verbous = True
        self._original_data.verbous = True
        self._filtered_data.verbous = True
        self._arcos_binarization.verbous = True
        self._arcos_output.verbous = True
        self._arcos_stats.verbous = True
        self._selected_object_id.verbous = True
        self._filename_for_sample_data.verbous = True
        self._timestamp_parameters.verbous = True

    @property
    def filename_for_sample_data(self):
        return self._filename_for_sample_data

    @filename_for_sample_data.setter
    def filename_for_sample_data(self, value):
        self._filename_for_sample_data.value = value

    @property
    def original_data(self):
        return self._original_data

    @original_data.setter
    def original_data(self, value):
        self._original_data.value = value

    @property
    def filtered_data(self):
        return self._filtered_data

    @filtered_data.setter
    def filtered_data(self, value):
        self._filtered_data.value = value

    @property
    def arcos_output(self):
        return self._arcos_output

    @arcos_output.setter
    def arcos_output(self, value):
        self._arcos_output.value = value

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, value):
        if not isinstance(value, columnnames):
            raise ValueError(f"columns must be of type {columnnames}")
        self._columns = value

    @property
    def arcos_stats(self):
        return self._arcos_stats

    @arcos_stats.setter
    def arcos_stats(self, value):
        self._arcos_stats.value = value

    @property
    def arcos_binarization(self):
        return self._arcos_binarization

    @arcos_binarization.setter
    def arcos_binarization(self, value):
        self._arcos_binarization.value = value

    @property
    def selected_object_id(self):
        return self._selected_object_id

    @selected_object_id.setter
    def selected_object_id(self, value):
        self._selected_object_id.value = value

    @property
    def arcos_parameters(self):
        return self._arcos_parameters

    @arcos_parameters.setter
    def arcos_parameters(self, value):
        if not isinstance(value, arcos_parameters):
            raise ValueError(f"Data must be of type {arcos_parameters}")
        self._arcos_parameters = value

    @property
    def timestamp_parameters(self):
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


if __name__ == "__main__":
    ds = DataStorage()
    ds.timestamp_parameters.value_changed_connect(
        lambda: print("original data changed")
    )
    print(ds.filtered_data.value.empty)
    # # ds.load_data("C:/Users/benig/test.csv")
    # print(ds.columns)
    # print(ds.original_data)
