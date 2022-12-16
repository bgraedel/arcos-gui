from __future__ import annotations

import csv
import gzip
import time
from typing import TYPE_CHECKING, Callable, Union

if TYPE_CHECKING:
    from arcos_gui.processing import data_storage
    from arcos_gui.widgets import columnpicker

import pandas as pd
from arcos_gui.tools import OPERATOR_DICTIONARY
from qtpy.QtCore import QObject, Signal


def subtract_timeoffset(data, frame_col):
    """Method to subtract the timeoffset in the frame column of data"""
    data[frame_col] -= min(data[frame_col])
    return data


def calculate_measurment(
    data: pd.DataFrame,
    operation: str,
    in_meas_1_name: str,
    in_meas_2_name: str,
    op_dict: dict,
):
    """Perform operation on the two measurement columns.

    Calcualates new column that will be used to detect collective events.
    Operation is determined in the columnpicker dialog and loaded from
    the OPERATOR_DICTIONARY.


    Parameters
    ----------
    data : pd.DataFrame
        Input data
    operation : str
        Operation to perform on the two measurement columns
    in_meas_1_name : str
        Name of the first measurement column
    in_meas_2_name : str
        Name of the second measurement column
    op_dict : dict
        Dictionary containing the operations to perform on the two measurement columns
    """
    data_in = data.copy()
    if operation in op_dict.keys():
        out_meas_name = op_dict[operation][1]
        data_in[out_meas_name] = op_dict[operation][0](
            data[in_meas_1_name], data[in_meas_2_name]
        )

    else:
        out_meas_name = in_meas_1_name
    return out_meas_name, data_in


def get_tracklengths(df: pd.DataFrame, field_of_view_id: str, track_id: str) -> tuple:
    """
    Groups filtered data by track_id and
    returns minimum and maximum tracklenght.
    Updates min and max tracklenght in
    the widget spinbox and sliders.

    Parameters
    ----------
    df : pd.DataFrame
        Input data
    field_of_view_id : str
        Name of the field of view column
    track_id : str
        Name of the track id column

    Returns
    -------
    min_tracklength : int
        Minimum tracklenght
    max_tracklength : int
        Maximum tracklenght
    """
    if df.empty:
        return 0, 0

    if field_of_view_id != "None":
        track_lenths = df.groupby(
            [
                field_of_view_id,
                track_id,
            ]
        ).size()
    else:
        track_lenths = df.groupby([track_id]).size()
    minmax = (min(track_lenths), max(track_lenths))
    return minmax


def filter_data(
    df_in: pd.DataFrame,
    field_of_view_id_name: str,
    frame_name: str,
    track_id_name: str,
    measurement_name: str,
    additional_filter_column_name: str,
    posCols: list,
    fov_val: Union[int, float, str],
    additional_filter_value: Union[int, float, str],
    min_tracklength_value: int,
    max_tracklength_value: int,
    frame_interval: float,
    st_out: Callable,
):
    """Used to filter the input data to contain a single position.
    If selected in the columpicker dialog, an additional filter option
    is displayed.
    Filter options also include minimum and maximum tracklength.

    Parameters
    ----------
    df_in : pd.DataFrame
        Input data
    pos_val : Union[int, float, str]
        Position value to filter for
    additional_filter_value : Union[int, float, str]
        Additional filter value
    min_tracklength_value : int
        Minimum tracklenght
    max_tracklength_value : int
        Maximum tracklenght
    field_of_view_id_name : str
        Name of the field of view column
    frame_name : str
        Name of the frame column
    track_id_name : str
        Name of the track id column
    measurement_name : str
        Name of the measurement column
    additional_filter_column_name : str
        Name of the additional filter column
    st_out : Callable
        Output functoin i.e. print() or show_info from Napari
    posCols : list
        List containing all position names
    frame_interval : float
        Frame interval
    """
    # gets raw data read in by arcos_widget from stored_variables object
    # and columns from columnpicker value
    in_data = process_input(
        df=df_in,
        field_of_view_column=field_of_view_id_name,
        frame_column=frame_name,
        pos_columns=posCols,
        track_id_column=track_id_name,
        measurement_column=measurement_name,
    )

    if df_in.empty or field_of_view_id_name == measurement_name:
        st_out("No data loaded, or not loaded correctly")
        return None, None, None

    # if the position column was not chosen in columnpicker,
    # dont filter by position
    if field_of_view_id_name != "None":
        # filter by position
        if len(df_in[field_of_view_id_name].unique()) > 1:
            # hast to be done before .filter_tracklenght otherwise code could break
            # if track ids are not unique to positions
            in_data.filter_position(fov_val)

    if additional_filter_column_name != "None":
        in_data.filter_second_column(
            additional_filter_column_name,
            additional_filter_value,
        )

    # filter by tracklenght
    in_data.filter_tracklength(
        min_tracklength_value,
        max_tracklength_value,
    )
    # option to set frame interval
    in_data.frame_interval(frame_interval)

    filtered_data = in_data.return_pd_df()

    # get min and max values
    if filtered_data.empty:
        st_out("No data loaded, or not loaded correctly")
        return None, None, None
    max_meas = max(filtered_data[measurement_name])
    min_meas = min(filtered_data[measurement_name])
    st_out("Data Filtered!")
    return filtered_data, max_meas, min_meas


def check_for_collid_column(data: pd.DataFrame, collid_column="collid", suffix="old"):
    """If collid_column is present in input data,
    add suffix to prevent dataframe merge conflic."""
    if collid_column in data.columns:
        data.rename(columns={collid_column: f"{collid_column}_{suffix}"}, inplace=True)
    return data


def preprocess_data(
    df: pd.DataFrame, frame_col: str, op: str, meas_1: str, meas_2: str, op_dict: dict
):
    try:
        df = subtract_timeoffset(df, frame_col)
    except KeyError as err:
        raise KeyError(
            f"Frame column not set properly, has to be int or float.\
                Set column is {frame_col} and available columns are {df.columns}"
        ) from err
    except TypeError as err:
        raise TypeError(
            f"Frame column not set properly, has to be int or float.\
                Set column is {frame_col} and available columns are {df.columns}"
        ) from err
    try:
        return calculate_measurment(df, op, meas_1, meas_2, op_dict)
    except KeyError as err:
        raise KeyError(
            f"Measurement columns not set properly, has to be int or float.\
                Set column is {meas_1} and {meas_2} and available columns are {df.columns}"
        ) from err
    except TypeError:
        raise TypeError(
            f"Measurement columns not set properly, has to be int or float.\
                set column is {meas_1} and {meas_2} and available columns are {df.columns}"
        )
    except ValueError as err:
        raise ValueError(
            f"Measurement columns not set properly, has to be int or float.\
                Set column is {meas_1} and {meas_2} and available columns are {df.columns}"
        ) from err


def get_delimiter(file_path: str, bytes=4096):
    sniffer = csv.Sniffer()
    if file_path.endswith(".csv"):
        with open(file_path) as f:
            data = f.read(bytes)
            delimiter = sniffer.sniff(data).delimiter
    if file_path.endswith("csv.gz"):
        with gzip.open(file_path, mode="rt") as f:
            data = f.read(bytes)
            delimiter = sniffer.sniff(data).delimiter
    return delimiter


def read_data_header(filename: str):
    delimiter_value = get_delimiter(filename)
    if filename.endswith(".csv"):
        with open(filename) as f:
            d_reader = csv.DictReader(f, delimiter=delimiter_value)
            # get fieldnames from DictReader object and store in list
            headers = d_reader.fieldnames
    if filename.endswith("csv.gz"):
        with gzip.open(filename, mode="rt") as f:
            d_reader = csv.DictReader(f, delimiter=delimiter_value)
            # get fieldnames from DictReader object and store in list
            headers = d_reader.fieldnames
    return headers, delimiter_value


class process_input:
    def __init__(
        self,
        field_of_view_column: str,
        frame_column: str,
        pos_columns: list,
        track_id_column: str,
        measurement_column: str,
        csv_file=None,
        df=None,
    ):

        self.field_of_view_column = field_of_view_column
        self.frame_column = frame_column
        self.pos_columns = pos_columns
        self.measurment_column = measurement_column
        self.track_id_column = track_id_column

        if df is not None:
            self.df = df
        else:
            self.csv_file = csv_file
            self.df = None

    def filter_position(self, fov_to_select=None, return_dataframe=False):
        if fov_to_select is not None:
            self.df = self.df.loc[
                self.df.loc[:, self.field_of_view_column] == fov_to_select
            ].copy(deep=True)
        if return_dataframe:
            return self.df

    def filter_second_column(
        self, column=None, value_to_select=None, return_dataframe=False
    ):
        if value_to_select is not None:
            self.df = self.df.loc[self.df.loc[:, column] == value_to_select].copy(
                deep=True
            )
        if return_dataframe:
            return self.df

        # filter_tracklenght works only if previously filtered by pos
        # or if track_ids dont overlapp between fov

    def filter_tracklength(self, min, max, return_dataframe=False):
        track_length = self.df.groupby(self.track_id_column).size()
        track_length_filtered = track_length.between(min, max)
        track_length_filtered_names = track_length_filtered[track_length_filtered].index
        self.df = self.df.loc[
            self.df.loc[:, self.track_id_column].isin(track_length_filtered_names)
        ].copy(deep=True)
        if return_dataframe:
            return self.df

    def rescale_measurment(self, rescale_factor: int, return_dataframe=False):
        """
        rescales measurment column by factor passed in as argument
        """
        self.df[self.measurment_column] = (
            rescale_factor * self.df[self.measurment_column]
        )
        if return_dataframe:
            return self.df

    def frame_interval(self, factor):
        if factor > 1:
            self.df[self.frame_column] = self.df[self.frame_column] / factor

    def return_pd_df(self):
        return self.df


class DataLoader(QObject):
    finished = Signal()
    new_data = Signal()

    def __init__(
        self,
        columnpicker_instance: columnpicker,
        stored_data_instance: data_storage,
        filepath: str,
        delimiter: str,
        parent=None,
    ):
        super().__init__(parent)
        self.stored_data_instance = stored_data_instance
        self.columnpicker_instance = columnpicker_instance
        self.filepath = filepath
        self.delimiter = delimiter

    def run(self):
        """Long-running task."""
        self.load_data(self.filepath, self.delimiter)

        self.finished.emit()

    def load_data(self, filepath, delimiter=None):
        """Loads data from a csv file and stores it in the data storage."""
        if delimiter:
            df = pd.read_csv(filepath, delimiter=delimiter)
        else:
            df = pd.read_csv(filepath)
        while self.columnpicker_instance.isVisible():
            time.sleep(0.1)

        if not self.columnpicker_instance.ok_pressed:
            return None, None

        self.new_data.emit()

        frame_col = self.stored_data_instance.columns.frame_column
        op = self.stored_data_instance.columns.measurement_math_operatoin
        in_meas1 = self.stored_data_instance.columns.measurement_column_1
        in_meas2 = self.stored_data_instance.columns.measurement_column_2

        meas_name, df = preprocess_data(
            df, frame_col, op, in_meas1, in_meas2, OPERATOR_DICTIONARY
        )
        # carefull this has to be in the order like below otherwise the subsequent callbacks will
        # start before the measurement column is set to the proper value since it listens for changes in the
        # original data

        self.stored_data_instance.columns.measurement_column = meas_name
        self.stored_data_instance.original_data = df