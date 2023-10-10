"""Module for arcos wrapper functions."""

from __future__ import annotations

import os
import warnings
from itertools import product
from pathlib import Path
from typing import Callable

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from arcos4py import ARCOS
from arcos4py.plotting import NoodlePlot, statsPlots
from arcos4py.tools import (
    calculate_statistics,
    calculate_statistics_per_frame,
    estimate_eps,
    filterCollev,
)
from arcos4py.tools._detect_events import DataFrameTracker, Linker
from arcos_gui.processing._data_storage import ArcosParameters, columnnames
from arcos_gui.processing._preprocessing_utils import (
    calculate_measurement,
    check_for_collid_column,
    create_file_names,
    create_output_folders,
    filter_data,
)
from arcos_gui.tools import AVAILABLE_OPTIONS_FOR_BATCH, OPERATOR_DICTIONARY
from napari.qt.threading import WorkerBase, WorkerBaseSignals
from qtpy.QtCore import Signal


class customARCOS(ARCOS):
    """Custom ARCOS class with replaced trackCollev method.

    The trackCollev method is replaced with a custom version that emits a signal
    for progress updates. This signal is connected to the ArcosWidget, which
    updates the progress bar. The custom trackCollev method also checks for the
    abort_requested flag and aborts the tracking if it is set to True.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.abort_requested = False
        self.progress_update = None

    def trackCollev(
        self,
        eps: float = 1,
        epsPrev: float | None = None,
        minClsz: int = 1,
        nPrev: int = 1,
        clusteringMethod: str = "dbscan",
        linkingMethod: str = "nearest",
        minSamples: int | None = None,
    ) -> pd.DataFrame:
        linker = Linker(
            eps=eps,
            epsPrev=epsPrev,
            minClSz=minClsz,
            minSamples=minSamples,
            clusteringMethod=clusteringMethod,
            linkingMethod=linkingMethod,
            nPrev=nPrev,
            predictor=False,
            nJobs=1,
        )
        tracker = DataFrameTracker(
            linker=linker,
            coordinates_column=self.posCols,
            frame_column=self.frame_column,
            id_column=self.id_column,
            bin_meas_column=self.bin_col,
            collid_column=self.clid_column,
        )
        df_list = []

        total = self.data[self.frame_column].nunique()

        if self.progress_update:
            self.progress_update.emit("total", total)

        for timepoint in tracker.track(self.data):
            if self.abort_requested:
                self.abort_requested = False
                return pd.DataFrame()
            df_list.append(timepoint)

            if self.progress_update:
                self.progress_update.emit("update", 1)

        if self.progress_update:
            self.progress_update.emit("reset", 0)

        df_out = pd.concat(df_list, axis=0)

        return df_out.query(f"{self.clid_column} != -1").reset_index(drop=True)


def empty_std_out(*args, **kwargs):
    pass


def init_arcos_object(
    df_in: pd.DataFrame,
    posCols: list,
    measurement_name: str,
    frame_col_name: str,
    track_id_col_name: str,
    progress_update_signal: Signal | None = None,
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
    arcos = customARCOS(
        data=df_in,
        posCols=posCols,
        frame_column=frame_col_name,
        id_column=track_id_col_name,
        measurement_column=measurement_name,
        clid_column=collid_name,
    )
    arcos.progress_update = progress_update_signal
    return arcos


def binarization(
    arcos: customARCOS,
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
) -> customARCOS:
    """
    Binarize measurement data

    Parameters
    ----------
    arcos : customARCOS
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
    arcos_bin : customARCOS
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
    arcos: customARCOS,
    neighbourhood_size: float,
    epsPrev: float | None,
    min_clustersize: int,
    nPrev_value: int,
):
    """
    Detect collective events with arcos trackCollev method.

    Parameters
    ----------
    arcos : customARCOS
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


def get_eps(arcos: customARCOS, method: str, minClustersize: int, current_eps: float):
    """
    Estimate eps value for arcos trackCollev method.

    Parameters
    ----------
    arcos : customARCOS
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
            data=arcos.data[arcos.data[arcos.bin_col] == 1],
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
    if track_id_col_name:
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
    else:
        # filter dataframe by duraiton of events
        detect_events_df = detected_events_df.copy()
        detect_events_df["duration"] = detect_events_df.groupby(
            [frame_col_name, collid_name]
        )[frame_col_name].transform("count")
        arcos_filtered = detect_events_df[detect_events_df["duration"] >= min_dur]
        arcos_filtered = arcos_filtered.drop(columns=["duration"])

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
    df_arcos_stats = calculate_statistics(
        df_arcos_filtered, frame_col, collid_name, object_id_name, posCols
    )
    return df_arcos_stats


class arcos_worker_base_signals(WorkerBaseSignals):
    binarization_finished = Signal(tuple)
    tracking_finished = Signal()
    new_arcos_output = Signal(tuple)
    new_eps = Signal(float)
    started = Signal()
    finished = Signal()
    aborted = Signal(object)
    arcos_progress_update = Signal(str, int)


class arcos_worker(WorkerBase):
    """Runs arcos with the current parameters defined in the ArcosWidget.

    Updates the data storage with the results. what_to_run is a set of strings
    indicating what to run. The strings correspond to specific steps in the
    arcos pipeline. The steps are:
        - 'binarization': initializes a new customARCOS object and runs the binarization.
        - 'tracking': runs the event detection.
        - 'filtering': runs the event filtering.
    """

    def __init__(
        self,
        what_to_run: set,
        std_out: Callable,
        arcos_parameters: ArcosParameters = ArcosParameters(),
        columns: columnnames = columnnames(),
        filtered_data: pd.DataFrame = pd.DataFrame(),
        arcos_object: customARCOS | None = None,
        arcos_raw_output: pd.DataFrame | None = None,
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
        """
        super().__init__(SignalsClass=arcos_worker_base_signals)
        self.what_to_run = what_to_run
        self.std_out = std_out
        self.arcos_parameters: ArcosParameters = arcos_parameters
        self.columns: columnnames = columns
        self.filtered_data: pd.DataFrame = filtered_data
        if arcos_object is None:
            arcos_object = init_arcos_object(
                df_in=pd.DataFrame(columns=["x", "t", "m", "id"]),
                posCols=["x"],
                frame_col_name="t",
                track_id_col_name="id",
                measurement_name="m",
                progress_update_signal=self.arcos_progress_update,
            )
        else:
            # attatch progress signal to arcos object if the arcos object is not None
            arcos_object.progress_update = self.arcos_progress_update

        self.arcos_object: customARCOS = arcos_object

        if arcos_raw_output is None:
            arcos_raw_output = pd.DataFrame(
                columns=["t", "id", "collid", "x", "y", "m"], data=[]
            )
        self.arcos_raw_output: pd.DataFrame = arcos_raw_output

    def quit(self) -> None:
        """Quit the worker. Sets the abort_requested flag to True.
        Reimplemented so that it also sets the arcos_abort_requested flag to True.
        """
        self._abort_requested = True
        self.arcos_object.abort_requested = True
        super().quit()

    def run_binarization(self):
        if self.filtered_data.empty:
            self.std_out("No data loaded. Load first using the import data tab.")
            self.abort_requested = True
            return
        self.started.emit()

        if self.abort_requested:
            return
        self.arcos_object = init_arcos_object(
            df_in=self.filtered_data,
            posCols=self.columns.posCol,
            measurement_name=self.columns.measurement_column,
            frame_col_name=self.columns.frame_column,
            track_id_col_name=self.columns.object_id,
            progress_update_signal=self.arcos_progress_update,
        )
        if self.abort_requested:
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
        if self.abort_requested:
            return
        self.binarization_finished.emit(
            (
                self.arcos_object.bin_col,
                self.arcos_object.resc_col,
                self.arcos_object.data,
            )
        )
        self.columns.measurement_bin = self.arcos_object.bin_col
        self.columns.measurement_resc = self.arcos_object.resc_col
        self.what_to_run.remove("binarization")

    def run_tracking(self):
        try:
            bin_col = self.columns.measurement_bin
            n_bin = self.arcos_object.data[bin_col].nunique()

        except KeyError:
            n_bin = 0
        if n_bin < 2:
            self.std_out("No Binarized Data. Adjust Binazation Parameters.")
            self.abort_requested = True
            return

        if self.abort_requested:
            return

        eps = get_eps(
            arcos=self.arcos_object,
            method=self.arcos_parameters.eps_method.value,
            minClustersize=self.arcos_parameters.min_clustersize.value,
            current_eps=self.arcos_parameters.neighbourhood_size.value,
        )

        if self.abort_requested:
            return

        self.new_eps.emit(eps)

        self.arcos_raw_output = detect_events(
            arcos=self.arcos_object,
            neighbourhood_size=eps,
            epsPrev=self.arcos_parameters.epsPrev.value,
            min_clustersize=self.arcos_parameters.min_clustersize.value,
            nPrev_value=self.arcos_parameters.nprev.value,
        )
        if self.abort_requested:
            return
        self.tracking_finished.emit()
        self.what_to_run.remove("tracking")

    def run_filtering(self):
        if self.arcos_raw_output.empty:
            self.std_out(
                "No Collective Events detected. Adjust Event Detection Parameters."
            )
            self.abort_requested = True
            return

        collid_name = "collid"
        if self.abort_requested:
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
            self.std_out("No Collective Events detected.Adjust Filtering parameters.")
            self.abort_requested = True
            return
        if self.abort_requested:
            return
        arcos_stats = calculate_arcos_stats(
            df_arcos_filtered=arcos_df_filtered,
            frame_col=self.columns.frame_column,
            collid_name=collid_name,
            object_id_name=self.columns.object_id,
            posCols=self.columns.posCol,
        )
        arcos_stats = arcos_stats.dropna()
        if self.abort_requested:
            return
        self.new_arcos_output.emit((arcos_df_filtered, arcos_stats))
        self.what_to_run.clear()

    def run(
        self,
    ):
        """Run arcos with input parameters.

        Runs only or only from as far as specified in the what_to_run set.
        """
        self.started.emit()

        try:
            if "binarization" in self.what_to_run and not self.abort_requested:
                self.run_binarization()

            if "tracking" in self.what_to_run and not self.abort_requested:
                self.run_tracking()

            if "filtering" in self.what_to_run and not self.abort_requested:
                self.run_filtering()

        except Exception as e:
            self.errored.emit(e)

        finally:
            self.finished.emit()


class TemporaryMatplotlibBackend:
    def __init__(self, backend="Agg"):
        self.temp_backend = backend
        self.original_backend = matplotlib.get_backend()

    def __enter__(self):
        plt.switch_backend(self.temp_backend)

    def __exit__(self, *args):
        plt.switch_backend(self.original_backend)


class BatchProcessorSignals(WorkerBaseSignals):
    finished = Signal()
    progress_update_files = Signal()
    progress_update_filters = Signal()
    new_total_files = Signal(int)
    new_total_filters = Signal(int)
    aborted = Signal()


class BatchProcessor(WorkerBase):
    """Runs Arcos in batch mode with the current parameters defined in the ArcosWidget."""

    def __init__(
        self,
        input_path: str,
        arcos_parameters: ArcosParameters,
        columnames: columnnames,
        min_tracklength: int,
        max_tracklength: int,
        what_to_export: list[str],
    ):
        super().__init__(SignalsClass=BatchProcessorSignals)
        self.input_path = input_path
        self.arcos_parameters = arcos_parameters
        self.columnames = columnames
        self.min_track_length = min_tracklength
        self.max_track_length = max_tracklength
        self.what_to_export = what_to_export

    def _create_fileendings_list(self):
        """Create a list o file endings for the files to be exported."""
        fileendings = []
        corresponding_fileendings = [".csv", ".csv", ".csv", ".svg", ".svg"]
        for option in self.what_to_export:
            if option in AVAILABLE_OPTIONS_FOR_BATCH:
                # get index of option in AVAILABLE_OPTIONS_FOR_BATCH
                index = AVAILABLE_OPTIONS_FOR_BATCH.index(option)
                # get corresponding file ending
                file_ending = corresponding_fileendings[index]
                # add file ending to list
                fileendings.append(file_ending)
        return fileendings

    def run_arcos_batch(self, df):
        """Run arcos with input parameters.

        Runs only or only from as far as specified in the what_to_run set.
        """
        arcos = init_arcos_object(
            df,
            self.columnames.posCol,
            self.columnames.measurement_column,
            self.columnames.frame_column,
            self.columnames.object_id,
        )
        arcos = binarization(
            arcos=arcos,
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
        eps = get_eps(
            arcos=arcos,
            method=self.arcos_parameters.eps_method.value,
            minClustersize=self.arcos_parameters.min_clustersize.value,
            current_eps=self.arcos_parameters.neighbourhood_size.value,
        )
        arcos_raw_output = detect_events(
            arcos=arcos,
            neighbourhood_size=eps,
            epsPrev=self.arcos_parameters.epsPrev.value,
            min_clustersize=self.arcos_parameters.min_clustersize.value,
            nPrev_value=self.arcos_parameters.nprev.value,
        )
        arcos_df_filtered = filtering_arcos_events(
            detected_events_df=arcos_raw_output,
            frame_col_name=self.columnames.frame_column,
            collid_name="collid",
            track_id_col_name=self.columnames.object_id,
            min_dur=self.arcos_parameters.min_dur.value,
            total_event_size=self.arcos_parameters.total_event_size.value,
        )
        if arcos_df_filtered.empty:
            return arcos_df_filtered, pd.DataFrame()

        arcos_stats = calculate_arcos_stats(
            df_arcos_filtered=arcos_df_filtered,
            frame_col=self.columnames.frame_column,
            collid_name="collid",
            object_id_name=self.columnames.object_id,
            posCols=self.columnames.posCol,
        )
        arcos_stats = arcos_stats.dropna()

        return arcos_df_filtered, arcos_stats

    def run(self):
        """Run arcos with input parameters.

        Runs only or only from as far as specified in the what_to_run set.
        """
        self.started.emit()
        try:
            summary_stats = summary_stats = {
                key: []
                for key in [
                    "file",
                    "fov",
                    "additional_filter",
                    "event_count",
                    "avg_total_size",
                    "avg_total_size_std",
                    "avg_duration",
                    "avg_duration_std",
                ]
            }  # noqa E501
            with TemporaryMatplotlibBackend("Agg"):
                # check that what_to_export
                if not self.what_to_export:
                    self.errored.emit(ValueError("No export selected"))
                    return

                print(f"Exporting {self.what_to_export}")

                # check that there are only valid export options
                valid_export_options = AVAILABLE_OPTIONS_FOR_BATCH
                for option in self.what_to_export:
                    if option not in valid_export_options:
                        self.errored.emit(ValueError(f"Invalid export option {option}"))
                        return

                # remove statsplot and noodleplot from what_to_export if no object id is given
                if self.columnames.object_id is None:
                    self.what_to_export = [
                        option
                        for option in self.what_to_export
                        if option not in ["statsplot", "noodleplot"]
                    ]
                    print("No object id given. Skipping statsplot and noodleplot.")

                file_list = [
                    os.path.join(self.input_path, file)
                    for file in os.listdir(self.input_path)
                    if file.endswith(".csv") or file.endswith(".csv.gz")
                ]
                self.new_total_files.emit(len(file_list))

                base_path, _ = create_output_folders(
                    self.input_path, self.what_to_export
                )
                for file in file_list:
                    if self.abort_requested:
                        self.aborted.emit()
                        break

                    pth = Path(file)

                    file_name = pth.with_suffix("").stem
                    print(f"Processing file {file_name}")
                    df = pd.read_csv(file, engine="pyarrow")

                    meas_col, df = calculate_measurement(
                        data=df,
                        operation=self.columnames.measurement_math_operation,
                        in_meas_1_name=self.columnames.measurement_column_1,
                        in_meas_2_name=self.columnames.measurement_column_2,
                        op_dict=OPERATOR_DICTIONARY,
                    )
                    self.columnames.measurement_column = meas_col

                    if self.columnames.position_id is not None:
                        position_ids = df[self.columnames.position_id].unique()
                    else:
                        position_ids = [None]

                    if self.columnames.additional_filter_column is not None:
                        additional_filters = df[
                            self.columnames.additional_filter_column
                        ].unique()
                    else:
                        additional_filters = [None]

                    iterator_fov_filter = list(
                        product(position_ids, additional_filters)
                    )
                    self.new_total_filters.emit(len(iterator_fov_filter))

                    for fov, additional_filter in iterator_fov_filter:
                        if self.abort_requested:
                            self.aborted.emit()
                            break

                        # add new row to summary stats
                        for key in summary_stats.keys():
                            summary_stats[key].append(pd.NA)

                        # update general stats that should be present for all iterations
                        summary_stats["file"][-1] = file_name
                        summary_stats["fov"][-1] = fov if fov is not None else pd.NA
                        summary_stats["additional_filter"][-1] = (
                            additional_filter
                            if additional_filter is not None
                            else pd.NA
                        )

                        df_filtered = filter_data(
                            df_in=df,
                            field_of_view_id_name=self.columnames.position_id,
                            frame_name=self.columnames.frame_column,
                            track_id_name=self.columnames.object_id,
                            measurement_name=self.columnames.measurement_column,
                            additional_filter_column_name=self.columnames.additional_filter_column,
                            posCols=self.columnames.posCol,
                            fov_val=fov,
                            additional_filter_value=additional_filter,
                            min_tracklength_value=self.min_track_length,
                            max_tracklength_value=self.max_track_length,
                            frame_interval=1,
                            st_out=empty_std_out,
                        )[0]
                        if df_filtered.empty:
                            # set event count to 0, rest is already set to nan
                            summary_stats["event_count"][-1] = 0

                            position_id_str = (
                                f"{self.columnames.position_id}:{fov}"
                                if self.columnames.position_id is not None
                                and fov is not None
                                else ""
                            )
                            additional_filter_str = (
                                f"{self.columnames.additional_filter_column}:{additional_filter}"
                                if self.columnames.additional_filter_column is not None
                                and additional_filter is not None
                                else ""
                            )
                            connector = (
                                " and "
                                if position_id_str and additional_filter_str
                                else ""
                            )
                            for_str = (
                                "for "
                                if position_id_str or additional_filter_str
                                else ""
                            )
                            error_message = f"No data for file {file} {for_str}{position_id_str}{connector}{additional_filter_str}"  # noqa E501
                            self.progress_update_filters.emit()
                            print(error_message)
                            continue

                        posx = self.columnames.posCol[0]
                        posy = self.columnames.posCol[1]
                        if len(self.columnames.posCol) == 2:
                            posz = None
                        else:
                            posz = self.columnames.posCol[2]

                        arcos_df_filtered, arcos_stats = self.run_arcos_batch(
                            df_filtered
                        )

                        if arcos_df_filtered.empty:
                            # set event count to 0, rest is already set to nan
                            summary_stats["event_count"][-1] = 0

                            print(
                                f"No events detected for file {file} filters fov:{fov} additional:{additional_filter}"
                            )  # noqa E501
                            self.progress_update_filters.emit()
                            continue

                        # update summary stats
                        summary_stats["event_count"][-1] = arcos_stats[
                            "collid"
                        ].nunique()
                        summary_stats["avg_total_size"][-1] = arcos_stats[
                            "total_size"
                        ].mean()
                        summary_stats["avg_total_size_std"][-1] = arcos_stats[
                            "total_size"
                        ].std()
                        summary_stats["avg_duration"][-1] = arcos_stats[
                            "duration"
                        ].mean()
                        summary_stats["avg_duration_std"][-1] = arcos_stats[
                            "duration"
                        ].std()

                        out_file_name = create_file_names(
                            base_path,
                            file_name,
                            self.what_to_export,
                            self._create_fileendings_list(),
                            fov,
                            additional_filter,
                            self.columnames.position_id,
                            self.columnames.additional_filter_column,
                        )
                        if "arcos_output" in self.what_to_export:
                            arcos_df_filtered.to_csv(
                                out_file_name["arcos_output"],
                                index=False,
                            )
                        if "arcos_stats" in self.what_to_export:
                            arcos_stats.to_csv(
                                out_file_name["arcos_stats"],
                                index=False,
                            )
                        if "per_frame_statistics" in self.what_to_export:
                            arcos_stats_per_frame = calculate_statistics_per_frame(
                                data=arcos_df_filtered,
                                frame_column=self.columnames.frame_column,
                                collid_column="collid",
                                pos_columns=self.columnames.posCol,
                            )
                            arcos_stats_per_frame.to_csv(
                                out_file_name["per_frame_statistics"],
                                index=False,
                            )

                        if "statsplot" in self.what_to_export:
                            # seaborn future warning is annoying
                            with warnings.catch_warnings():
                                warnings.simplefilter(
                                    action="ignore", category=FutureWarning
                                )
                                arcos_stats_plot = statsPlots(arcos_stats)
                                arcos_stats_plot.plot_events_duration(
                                    "total_size", "duration"
                                )
                                plt.savefig(out_file_name["statsplot"])
                                plt.close()

                        if "noodleplot" in self.what_to_export:
                            noodle_plot = NoodlePlot(
                                df=arcos_df_filtered,
                                colev=self.columnames.collid_name,
                                trackid=self.columnames.object_id,
                                frame=self.columnames.frame_column,
                                posx=posx,
                                posy=posy,
                                posz=posz,
                            )

                            noodle_plot.plot(posx)
                            plt.savefig(out_file_name["noodleplot"])
                            plt.close()

                        self.progress_update_filters.emit()

                    self.progress_update_files.emit()

            summary_stats_df = pd.DataFrame(summary_stats).round(4)
            # drop rows with all nan
            summary_stats_df = summary_stats_df.dropna(how="all", axis=1)
            summary_stats_df.to_csv(
                os.path.join(base_path, "per_file_summary.csv"),
                index=False,
                na_rep="NA",
            )

        except Exception as e:
            self.errored.emit(e)
        finally:
            self.finished.emit()
