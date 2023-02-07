from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Union

import numpy as np
import pandas as pd
from arcos4py import ARCOS
from arcos4py.tools import calcCollevStats, estimate_eps, filterCollev

from ._preprocessing_utils import check_for_collid_column

if TYPE_CHECKING:
    from ._data_storage import DataStorage


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
        return

    arcos_events = arcos.trackCollev(
        eps=neighbourhood_size,
        epsPrev=epsPrev,
        minClsz=min_clustersize,
        nPrev=nPrev_value,
    )
    return arcos_events


def get_eps(arcos: ARCOS, method: str, minClustersize: int):
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

    Returns
    -------
    eps : float
        eps value
    """
    methods = ["manual", "kneepoint", "mean"]
    if method not in methods:
        raise ValueError(f"Method must be one of {methods}")

    if method == "manual":
        return

    if method == "kneepoint":
        return estimate_eps(
            data=arcos.data[arcos.data[arcos.bin_col] > 0],
            method="kneepoint",
            pos_cols=arcos.posCols,
            frame_col=arcos.frame_column,
            n_neighbors=minClustersize,
            plot=False,
        )

    if method == "mean":
        return estimate_eps(
            arcos.data,
            method="mean",
            pos_cols=arcos.posCols,
            frame_col=arcos.frame_column,
            n_neighbors=minClustersize,
            plot=False,
        )


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
    df_arcos_stats = calcCollevStats().calculate(
        df_arcos_filtered, frame_col, collid_name, object_id_name, posCols
    )
    return df_arcos_stats


class arcos_wrapper:
    """Runs arcos with the current parameters defined in the ArcosWidget."""

    def __init__(
        self, data_storage_instance: DataStorage, what_to_run: set, std_out: Callable
    ):

        self.data_storage_instance = data_storage_instance
        self.what_to_run = what_to_run
        self.std_out = std_out
        self.arcos_object: Union[ARCOS, None] = None
        self.arcos_raw_output: pd.DataFrame = pd.DataFrame()
        self.data_storage_instance.filtered_data.value_changed_connect(self._new_data)

    def _new_data(self):
        # set stats to default without triggering the value_changed signal
        self.data_storage_instance.arcos_stats.value = pd.DataFrame()
        self.data_storage_instance.arcos_output.value = pd.DataFrame()
        self.data_storage_instance.arcos_binarization.value = pd.DataFrame()

    def run_arcos(
        self,
        interpolate_meas: bool,
        clip_meas: bool,
        clip_low: float,
        clip_high: float,
        smooth_k: int,
        bias_k: int,
        bias_method: str,
        polyDeg: int,
        bin_threshold: float,
        bin_peak_threshold: float,
        epsMethod: str,
        neighbourhood_size: float,
        epsPrev: float | None,
        min_clustersize: int,
        min_dur: int,
        total_event_size: int,
        nprev: int,
    ):
        # get the stored variables
        df_filtered = self.data_storage_instance.filtered_data.value
        posCols = self.data_storage_instance.columns.posCol
        meas = self.data_storage_instance.columns.measurement_column
        frame = self.data_storage_instance.columns.frame_column
        track_id_col_name = self.data_storage_instance.columns.object_id

        if "binarization" in self.what_to_run:
            if df_filtered.empty:
                self.std_out("No data loaded. Load first using the import data tab.")
                return

            self.arcos_object = init_arcos_object(
                df_in=df_filtered,
                posCols=posCols,
                measurement_name=meas,
                frame_col_name=frame,
                track_id_col_name=track_id_col_name,
            )

            self.arcos_object = binarization(
                arcos=self.arcos_object,
                interpolate_meas=interpolate_meas,
                clip_meas=clip_meas,
                clip_low=clip_low,
                clip_high=clip_high,
                smooth_k=smooth_k,
                bias_k=bias_k,
                polyDeg=polyDeg,
                bin_threshold=bin_threshold,
                bin_peak_threshold=bin_peak_threshold,
                bias_method=bias_method,
            )
            self.data_storage_instance.columns.measurement_bin = (
                self.arcos_object.bin_col
            )
            self.data_storage_instance.columns.measurement_resc = (
                self.arcos_object.resc_col
            )
            self.data_storage_instance.arcos_stats.value = pd.DataFrame()

            self.data_storage_instance.arcos_binarization = self.arcos_object.data

        if "tracking" in self.what_to_run:
            try:
                bin_col = self.data_storage_instance.columns.measurement_bin
                n_bin = self.data_storage_instance.arcos_binarization.value[
                    bin_col
                ].nunique()
            except KeyError:
                n_bin = 0
            if self.data_storage_instance.arcos_binarization is None or n_bin < 2:
                self.std_out("No Binarized Data. Adjust Binazation Parameters.")
                return

            eps = get_eps(
                arcos=self.arcos_object,
                method=epsMethod,
                minClustersize=min_clustersize,
            )

            if not eps:
                eps = neighbourhood_size
            eps = round(eps, 2)
            self.data_storage_instance.arcos_parameters.neighbourhood_size.value = eps

            self.arcos_raw_output = detect_events(
                arcos=self.arcos_object,
                neighbourhood_size=eps,
                epsPrev=epsPrev,
                min_clustersize=min_clustersize,
                nPrev_value=nprev,
            )

        if "filtering" in self.what_to_run:
            if self.arcos_raw_output.empty:
                self.std_out(
                    "No Collective Events detected. Adjust Event Detection Parameters."
                )
                return
            collid_name = "collid"
            arcos_df_filtered = filtering_arcos_events(
                detected_events_df=self.arcos_raw_output,
                frame_col_name=frame,
                collid_name=collid_name,
                track_id_col_name=track_id_col_name,
                min_dur=min_dur,
                total_event_size=total_event_size,
            )
            if arcos_df_filtered.empty:
                self.std_out(
                    "No Collective Events detected.Adjust Filtering parameters."
                )
                return
            arcos_stats = calculate_arcos_stats(
                df_arcos_filtered=arcos_df_filtered,
                frame_col=frame,
                collid_name=collid_name,
                object_id_name=track_id_col_name,
                posCols=posCols,
            )
            arcos_stats = arcos_stats.dropna()
            self.data_storage_instance.arcos_stats = arcos_stats
            self.data_storage_instance.arcos_output = arcos_df_filtered
            self.what_to_run.clear()

    def run_bin(self, **kwargs):
        initial_wtr = self.what_to_run.copy()
        self.what_to_run.clear()
        self.what_to_run.add("binarization")
        self.run_arcos(**kwargs)
        if not self.data_storage_instance.arcos_binarization.value.empty:
            self.what_to_run.add("tracking")
            self.what_to_run.add("filtering")
            return

        self.what_to_run.clear()
        for i in initial_wtr:
            self.what_to_run.add(i)
        self.std_out("No Binarized Data. Adjust Binazation Parameters.")
