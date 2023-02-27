"""Module for arcos wrapper functions."""

from __future__ import annotations

from time import sleep
from typing import Callable

import numpy as np
import pandas as pd
from arcos4py import ARCOS
from arcos4py.tools import calcCollevStats, estimate_eps, filterCollev
from qtpy.QtCore import QObject, Signal

from ._data_storage import arcos_parameters, columnnames
from ._preprocessing_utils import check_for_collid_column


def init_arcos_object(
    df_in: pd.DataFrame,
    posCols: list,
    measurement_name: str,
    frame_col_name: str,
    track_id_col_name: str,
):
    """
    Initialize arcos object from pandas dataframe

    Parameters
    ----------
    df_in : pd.DataFrame
        input dataframe
    posCols : list
        list of position columns
    measurement_name : str
        name of measurement column
    frame_col_name : str
        name of frame column
    track_id_col_name : str
        name of track id column
    std_out_func : Callable
        function to print to console or gui
    """

    collid_name = "collid"

    df_in = check_for_collid_column(df_in, collid_name)

    # checks if this part of the function has to be run,
    # depends on the parameters changed in arcos widget

    # create arcos object, run arcos
    arcos = ARCOS(
        data=df_in,
        posCols=posCols,
        frame_column=frame_col_name,
        id_column=track_id_col_name,
        measurement_column=measurement_name,
        clid_column=collid_name,
    )
    return arcos


def binarization(
    arcos: ARCOS,
    interpolate_meas: bool,
    clip_meas: bool,
    clip_low: float,
    clip_high: float,
    smooth_k: int,
    bias_k: int,
    bin_peak_threshold: float,
    bin_threshold: float,
    polyDeg: int,
    bias_method: str,
) -> ARCOS:
    """
    Binarize measurement data

    Parameters
    ----------
    arcos : ARCOS
        arcos object
    interpolate_meas : bool
        interpolate measurement data
    clip_meas : bool
        clip measurement data
    clip_low : float
        lower clip value
    clip_high : float
        higher clip value
    smooth_k : int
        smoothing kernel size
    bias_k : int
        bias kernel size
    bin_peak_threshold : float
        peak threshold
    bin_threshold : float
        binarization threshold
    polyDeg : int
        polynomial degree
    bias_method : str
        bias method

    Returns
    -------
    arcos_bin : ARCOS
        arcos object with binarized measurement data
    """
    # if corresponding checkbox was selected run interpolate measurments
    if interpolate_meas:
        arcos.interpolate_measurements()

    # if corresponding checkbock was selected run clip_measuremnts
    if clip_meas:
        arcos.clip_meas(
            clip_low=clip_low,
            clip_high=clip_high,
        )

    # binarize data and update ts variable
    # update from where to run
    arcos.bin_measurements(
        smoothK=smooth_k,
        biasK=bias_k,
        peakThr=bin_peak_threshold,
        binThr=bin_threshold,
        polyDeg=polyDeg,
        biasMet=bias_method,
    )

    return arcos


def detect_events(
    arcos: ARCOS,
    neighbourhood_size: float,
    epsPrev: float | None,
    min_clustersize: int,
    nPrev_value: int,
):
    """
    Detect collective events with arcos trackCollev method.

    Parameters
    ----------
    arcos : ARCOS
        arcos object
    measbin_col : str
        name of binarized measurement column
    neighbourhood_size : float
        neighbourhood size to consider for event detection
    min_clustersize : int
        minimum cluster size to consider for event detection
    nPrev_value : int
        number of previous frames to consider for event detection

    Returns
    -------
    arcos_events : pd.DataFrame
        dataframe with detected events
    """
    _bin_col = arcos.bin_col
    if 1 not in arcos.data[_bin_col].values:
        return None

    arcos_events = arcos.trackCollev(
        eps=neighbourhood_size,
        epsPrev=epsPrev,
        minClsz=min_clustersize,
        nPrev=nPrev_value,
    )
    return arcos_events


def get_eps(arcos: ARCOS, method: str, minClustersize: int, current_eps: float):
    """
    Estimate eps value for arcos trackCollev method.

    Parameters
    ----------
    arcos : ARCOS
        arcos object
    method : str
        method to estimate eps value
    minClustersize : int
        minimum cluster size to consider for event detection
    current_eps : float | None
        current eps value, will be returned if method is manual

    Returns
    -------
    eps : float
        eps value
    """
    methods = ["manual", "kneepoint", "mean"]
    if method not in methods:
        raise ValueError(f"Method must be one of {methods}")

    if method == "kneepoint":
        eps = estimate_eps(
            data=arcos.data[arcos.data[arcos.bin_col] > 0],
            method="kneepoint",
            pos_cols=arcos.posCols,
            frame_col=arcos.frame_column,
            n_neighbors=minClustersize,
            plot=False,
        )
        return round(eps, 2)

    if method == "mean":
        eps = estimate_eps(
            arcos.data,
            method="mean",
            pos_cols=arcos.posCols,
            frame_col=arcos.frame_column,
            n_neighbors=minClustersize,
            plot=False,
        )
        return round(eps, 2)
    return round(current_eps, 2)


def filtering_arcos_events(
    detected_events_df: pd.DataFrame,
    frame_col_name: str,
    collid_name: str,
    track_id_col_name: str,
    min_dur: int,
    total_event_size: int,
):
    """
    Filter detected events with arcos filterCollev method.

    Parameters
    ----------
    original_df : pd.DataFrame
        original dataframe
    detected_events_df : pd.DataFrame
        dataframe with detected events
    frame_col_name : str
        name of frame column
    collid_name : str
        name of collid column
    track_id_col_name : str
        name of track id column
    min_dur : int
        minimum duration of events
    total_event_size : int
        minimum size of events

    Returns
    -------
    filtered_events_df : pd.DataFrame
        dataframe with filtered events
    """
    filterer = filterCollev(
        data=detected_events_df,
        frame_column=frame_col_name,
        collid_column=collid_name,
        obj_id_column=track_id_col_name,
    )
    arcos_filtered = filterer.filter(
        coll_duration=min_dur,
        coll_total_size=total_event_size,
    )

    # makes filtered collids sequential
    clid_np = arcos_filtered[collid_name].to_numpy()
    clids_sorted_i = np.argsort(clid_np)
    clids_reverse_i = np.argsort(clids_sorted_i)
    clid_np_sorted = clid_np[(clids_sorted_i)]
    grouped_array_clids = np.split(
        clid_np_sorted,
        np.unique(clid_np_sorted, axis=0, return_index=True)[1][1:],
    )
    seq_colids = np.concatenate(
        [np.repeat(i, value.shape[0]) for i, value in enumerate(grouped_array_clids)],
        axis=0,
    )[clids_reverse_i]
    seq_colids_from_one = np.add(seq_colids, 1)
    arcos_filtered = arcos_filtered.copy()
    arcos_filtered.loc[:, collid_name] = seq_colids_from_one

    return arcos_filtered


def calculate_arcos_stats(
    df_arcos_filtered: pd.DataFrame,
    frame_col: str,
    collid_name: str,
    object_id_name: str,
    posCols: list,
):
    """Wrapper for calcCollevStats().

    Parameters
    ----------
    df_arcos_filtered : pd.DataFrame
        dataframe with filtered events
    frame_col : str
        name of frame column
    collid_name : str
        name of collid column
    object_id_col_name : str
        name of object id column
    posCols : list
        list of position columns

    Returns
    -------
    df_arcos_stats : pd.DataFrame
        dataframe with statistics for each event
    """
    df_arcos_stats = calcCollevStats().calculate(
        df_arcos_filtered, frame_col, collid_name, object_id_name, posCols
    )
    return df_arcos_stats


class arcos_worker(QObject):
    """Runs arcos with the current parameters defined in the ArcosWidget.

    Updates the data storage with the results. what_to_run is a set of strings
    indicating what to run. The strings correspond to specific steps in the
    arcos pipeline. The steps are:
        - 'binarization': initializes a new ARCOS object and runs the binarization.
        - 'tracking': runs the event detection.
        - 'filtering': runs the event filtering.
    """

    binarization_finished = Signal(tuple)
    tracking_finished = Signal()
    new_arcos_output = Signal(tuple)
    new_eps = Signal(float)
    started = Signal()
    finished = Signal()
    aborted = Signal(object)
    arcos_parameters = arcos_parameters()
    columns = columnnames()
    filtered_data: pd.DataFrame = pd.DataFrame()
    parameters_updated_flag = False
    aborted_flag = False
    idle_flag = True

    def __init__(
        self,
        what_to_run: set,
        std_out: Callable,
        wait_for_parameter_update: bool = False,
        parent=None,
    ):
        """Constructor.

        Parameters
        ----------
        what_to_run : set
            set of strings indicating what to run
        std_out : Callable
            function to print to the console
        wait_for_parameter_update : bool, optional
            if True, the worker will wait for the parameters to be updated before running
        parent : QObject, optional
        """
        super().__init__(parent)
        self.what_to_run = what_to_run
        self.std_out = std_out
        self.arcos_object: ARCOS = ARCOS(
            pd.DataFrame(columns=["x", "t", "m", "id"]),
            posCols=["x"],
            frame_column="t",
            id_column="id",
            measurement_column="m",
        )
        self.arcos_raw_output: pd.DataFrame = pd.DataFrame()
        self.wait_for_parameter_update = wait_for_parameter_update
        if wait_for_parameter_update:
            self._connect_parameters_updated()

    def _connect_parameters_updated(self):
        self.arcos_parameters.interpolate_meas.value_changed_connect(
            self.set_parameters_updated_flag
        )
        self.arcos_parameters.clip_meas.value_changed_connect(
            self.set_parameters_updated_flag
        )
        self.arcos_parameters.clip_low.value_changed_connect(
            self.set_parameters_updated_flag
        )
        self.arcos_parameters.clip_high.value_changed_connect(
            self.set_parameters_updated_flag
        )
        self.arcos_parameters.bias_method.value_changed_connect(
            self.set_parameters_updated_flag
        )
        self.arcos_parameters.smooth_k.value_changed_connect(
            self.set_parameters_updated_flag
        )
        self.arcos_parameters.bias_k.value_changed_connect(
            self.set_parameters_updated_flag
        )
        self.arcos_parameters.polyDeg.value_changed_connect(
            self.set_parameters_updated_flag
        )
        self.arcos_parameters.bin_threshold.value_changed_connect(
            self.set_parameters_updated_flag
        )
        self.arcos_parameters.bin_peak_threshold.value_changed_connect(
            self.set_parameters_updated_flag
        )
        self.arcos_parameters.neighbourhood_size.value_changed_connect(
            self.set_parameters_updated_flag
        )
        self.arcos_parameters.eps_method.value_changed_connect(
            self.set_parameters_updated_flag
        )
        self.arcos_parameters.epsPrev.value_changed_connect(
            self.set_parameters_updated_flag
        )
        self.arcos_parameters.min_clustersize.value_changed_connect(
            self.set_parameters_updated_flag
        )
        self.arcos_parameters.nprev.value_changed_connect(
            self.set_parameters_updated_flag
        )
        self.arcos_parameters.min_dur.value_changed_connect(
            self.set_parameters_updated_flag
        )
        self.arcos_parameters.total_event_size.value_changed_connect(
            self.set_parameters_updated_flag
        )
        self.arcos_parameters.min_clustersize.value_changed_connect(
            self.set_parameters_updated_flag
        )

    def set_parameters_updated_flag(self, val: bool = True):
        """Set the idle flag.

        Parameters
        ----------
        val : bool
            value to set the idle flag to
        """
        if not isinstance(val, bool):
            raise TypeError("val must be a bool")

        self.parameters_updated_flag = val

    def run_binarization(self):
        try:
            if self.filtered_data.empty:
                self.std_out("No data loaded. Load first using the import data tab.")
                self.aborted_flag = True
                return
            self.started.emit()

            if self.aborted_flag:
                return
            self.arcos_object = init_arcos_object(
                df_in=self.filtered_data,
                posCols=self.columns.posCol,
                measurement_name=self.columns.measurement_column,
                frame_col_name=self.columns.frame_column,
                track_id_col_name=self.columns.object_id,
            )
            if self.aborted_flag:
                return

            self.arcos_object = binarization(
                arcos=self.arcos_object,
                interpolate_meas=self.arcos_parameters.interpolate_meas.value,
                clip_meas=self.arcos_parameters.clip_meas.value,
                clip_low=self.arcos_parameters.clip_low.value,
                clip_high=self.arcos_parameters.clip_high.value,
                smooth_k=self.arcos_parameters.smooth_k.value,
                bias_k=self.arcos_parameters.bias_k.value,
                polyDeg=self.arcos_parameters.polyDeg.value,
                bin_threshold=self.arcos_parameters.bin_threshold.value,
                bin_peak_threshold=self.arcos_parameters.bin_peak_threshold.value,
                bias_method=self.arcos_parameters.bias_method.value,
            )
            if self.aborted_flag:
                return
            self.binarization_finished.emit(
                (
                    self.arcos_object.bin_col,
                    self.arcos_object.resc_col,
                    self.arcos_object.data,
                )
            )
            self.what_to_run.remove("binarization")

        except Exception as e:
            # print(f"Error in binarization: {e}")
            self.aborted_flag = True
            self.aborted.emit(e)

    def run_tracking(self):
        try:
            bin_col = self.columns.measurement_bin
            n_bin = self.arcos_object.data[bin_col].nunique()
        except KeyError:
            n_bin = 0
        if n_bin < 2:
            self.std_out("No Binarized Data. Adjust Binazation Parameters.")
            self.aborted_flag = True
            return
        self.started.emit()
        try:
            if self.aborted_flag:
                return

            # print("Calculating eps...")
            eps = get_eps(
                arcos=self.arcos_object,
                method=self.arcos_parameters.eps_method.value,
                minClustersize=self.arcos_parameters.min_clustersize.value,
                current_eps=self.arcos_parameters.neighbourhood_size.value,
            )
            # print(f"eps = {eps}")

            if self.aborted_flag:
                return

            self.new_eps.emit(eps)

            self.arcos_raw_output = detect_events(
                arcos=self.arcos_object,
                neighbourhood_size=eps,
                epsPrev=self.arcos_parameters.epsPrev.value,
                min_clustersize=self.arcos_parameters.min_clustersize.value,
                nPrev_value=self.arcos_parameters.nprev.value,
            )
            if self.aborted_flag:
                return
            self.tracking_finished.emit()
            self.what_to_run.remove("tracking")

        except Exception as e:
            # print(f"Error in tracking: {e}")
            self.aborted_flag = True
            self.aborted.emit(e)

    def run_filtering(self):
        try:
            if self.arcos_raw_output.empty:
                self.std_out(
                    "No Collective Events detected. Adjust Event Detection Parameters."
                )
                self.aborted_flag = True
                return

            collid_name = "collid"
            if self.aborted_flag:
                return
            arcos_df_filtered = filtering_arcos_events(
                detected_events_df=self.arcos_raw_output,
                frame_col_name=self.columns.frame_column,
                collid_name=collid_name,
                track_id_col_name=self.columns.object_id,
                min_dur=self.arcos_parameters.min_dur.value,
                total_event_size=self.arcos_parameters.total_event_size.value,
            )
            if arcos_df_filtered.empty:
                self.std_out(
                    "No Collective Events detected.Adjust Filtering parameters."
                )
                self.aborted_flag = True
                return
            if self.aborted_flag:
                return
            arcos_stats = calculate_arcos_stats(
                df_arcos_filtered=arcos_df_filtered,
                frame_col=self.columns.frame_column,
                collid_name=collid_name,
                object_id_name=self.columns.object_id,
                posCols=self.columns.posCol,
            )
            arcos_stats = arcos_stats.dropna()
            if self.aborted_flag:
                return
            self.new_arcos_output.emit((arcos_df_filtered, arcos_stats))
            self.what_to_run.clear()
        except Exception as e:
            # print(f"Error in filtering: {e}")
            self.aborted_flag = True
            self.aborted.emit(e)

    def run_arcos(
        self,
    ):
        """Run arcos with input parameters.

        Runs only or only from as far as specified in the what_to_run set.
        """
        self.idle_flag = False
        self.aborted_flag = False
        # needed to avoid conditions where the parameters are updated after
        # the worker has started. Flag is set from the arcos widget in the main thread.
        while not self.parameters_updated_flag and self.wait_for_parameter_update:
            sleep(0.1)

        if "binarization" in self.what_to_run and not self.aborted_flag:
            self.run_binarization()

        if "tracking" in self.what_to_run and not self.aborted_flag:
            self.run_tracking()

        if "filtering" in self.what_to_run and not self.aborted_flag:
            self.run_filtering()

        self.parameters_updated_flag = False
        self.finished.emit()
        self.idle_flag = True

    def run_bin(self):
        """Run the binarizatoin only. Same as run_arcos but with only binarization."""
        initial_wtr = self.what_to_run.copy()
        self.what_to_run.clear()
        self.what_to_run.add("binarization")
        self.run_arcos()

        if not self.arcos_object.data.empty:
            self.what_to_run.add("tracking")
            self.what_to_run.add("filtering")
            return
        self.what_to_run.clear()
        for i in initial_wtr:
            self.what_to_run.add(i)
        self.std_out("No Binarized Data. Adjust Binazation Parameters.")
