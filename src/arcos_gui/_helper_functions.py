from __future__ import annotations

from typing import Literal

import napari
import pandas as pd
from arcos_gui import _main_widget
from arcos_gui.processing import columnnames
from arcos_gui.sample_data import load_real_dataset, load_synthetic_dataset


def open_plugin(viewer: napari.Viewer):
    """Main function. Adds plugin dock widget to napari viewer.

    Parameters
    ----------
    viewer : napari.Viewer
        Napari viewer to add the plugin to.

    Returns
    -------
    plugin : _main_widget.MainWindow
        The plugin instance.
    """
    plugin: _main_widget.MainWindow
    viewer, plugin = viewer.window.add_plugin_dock_widget(
        plugin_name="arcos-gui", widget_name="ARCOS Main Widget"
    )
    return plugin


def load_sample_data(
    sample_data: Literal["synthetic", "real"] = "synthetic",
    plugin: _main_widget.MainWindow | None = None,
):
    """Load sample data into arcos-gui.

    Parameters
    ----------
    plugin : _main_widget.MainWindow | None
        If None, will try to get the last instance of the plugin (can fail if the plugin has been closed before
        and some stray reference is hanging arround).
        If not None, will use the given plugin instance. Plugin can be opened with open_plugin(viewer).
    sample_data : Literal['synthetic', 'real']
        Which sample data to load. Either synthetic or real.
    """
    if sample_data == "synthetic":
        load_synthetic_dataset(plugin=plugin)
    elif sample_data == "real":
        load_real_dataset(plugin=plugin)
    else:
        raise ValueError("sample_data must be either 'synthetic' or 'real'")


def load_dataframe(
    df: pd.DataFrame,
    frame_column: str,
    track_id_column: str | None,
    x_column: str,
    y_column: str,
    z_column: str | None,
    measurement_column: str,
    measurement_column_2: str | None,
    fov_column: str | None,
    additional_filter_column: str | None,
    measurement_math_operation: Literal[
        "Divide", "Multiply", "Add", "Subtract", None
    ] = None,
    plugin: _main_widget.MainWindow | None = None,
):
    """Load dataframe into arcos-gui. Bypasses the file loading dialog and columnpicker dialog.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to load, in a long table format where each row defines the object's
        location, time, and the measurement value.
    frame_column : str
        Name of the column in the dataframe that defines the timepoint of the measurement.
    track_id_column : str | None
        Name of the column in the dataframe that defines the track id of the object.
        If None, some functions (detrending, plotting, statistics) will not be available.
    x_column : str
        Name of the column in the dataframe that defines the x coordinate of the objects.
    y_column : str
        Name of the column in the dataframe that defines the y coordinate of the objects.
    z_column : str | None
        Name of the column in the dataframe that defines the z coordinate of the objects.
        If None, the data will be treated as 2D.
    fov_column : str | None
        Name of the column in the dataframe that defines the field of view of the objects, only
        used to filter the data.
        If None, the data will be treated as a single field of view.
    measurement_column : str
        Name of the column in the dataframe that defines the measurement value.
    measurement_column_2 : str | None
        Name of the column in the dataframe that defines the second measurement value.
        The second measurement is only used when performing a measurement math operation. Such as
        dividing the measurement by the second measurement.
    additional_filter_column : str | None
        Name of the column in the dataframe that defines the additional filter. Can be used to filter
        the data by e.g. Well ID.
    measurement_math_operation : Literal['Divide', "Multiply", "Add", "Subtract", None]
        Math operation to perform on the measurements. If None, no operation will be performed. And the
        second measurement column will be ignored.
    plugin : _main_widget.MainWindow | None
        If None, will try to get the last instance of the plugin (can fail if the plugin has been closed before
        and some stray reference is hanging arround).
        If not None, will use the given plugin instance. Plugin can be opened with open_plugin(viewer).
    """
    columns = columnnames(
        frame_column=frame_column,
        x_column=x_column,
        y_column=y_column,
        z_column=z_column,
        object_id=track_id_column,
        position_id=fov_column,
        measurement_column_1=measurement_column,
        measurement_column_2=measurement_column_2,
        additional_filter_column=additional_filter_column,
        measurement_math_operation=measurement_math_operation,
    )
    if plugin is None:
        plugin = _main_widget.MainWindow.get_last_instance()
    if not plugin:
        _plugin = open_plugin(napari.current_viewer())
    else:
        _plugin = plugin

    try:
        _plugin._input_controller.load_from_dataframe(dataframe=df, columns=columns)
    except RuntimeError:
        print("Cannot find the plugin. Opening a new one.")
        _plugin = open_plugin(napari.current_viewer())
        _plugin._input_controller.load_from_dataframe(dataframe=df, columns=columns)
    _plugin._widget.maintabwidget.setCurrentIndex(1)


def load_dataframe_with_columnpicker(df, plugin: _main_widget.MainWindow | None = None):
    """Load dataframe into arcos-gui. Opens a columnpicker dialog to select the columns.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe to load, in a long table format where each row defines the object's
        location, time, and the measurement value.
        plugin : _main_widget.MainWindow | None
        If None, will try to get the last instance of the plugin (can fail if the plugin has been closed before and
        some stray reference is hanging arround).
        If not None, will use the given plugin instance. Plugin can be opened with open_plugin(viewer).
    """
    plugin = _main_widget.MainWindow.get_last_instance()
    if not plugin:
        _plugin = open_plugin(napari.current_viewer())
    else:
        _plugin = plugin

    try:
        _plugin._input_controller.load_from_dataframe(df, columns=None)
    except RuntimeError:
        print("Cannot find the plugin. Opening a new one.")
        _plugin = open_plugin(napari.current_viewer())
        _plugin._input_controller.load_from_dataframe_with_columnpicker(df)


def filter_data(
    track_length: tuple[int, int] | None = None,
    fov_id: str | None = None,
    additional_filter: str | None = None,
    plugin: _main_widget.MainWindow | None = None,
):
    """Filter data by track length and track id.

    Parameters
    ----------
    track_length : tuple[int, int] | None
        Tuple of minimum and maximum track length.
    fov_id : str | None
        Field of view id to filter by. If None,
        assumes that the data is from a single field of view.
    additional_filter : str | None
        Additional filter to filter by. If None,
        assumes that the data is not filtered by an additional filter.
    plugin : _main_widget.MainWindow | None
        If None, will try to get the last instance of the plugin (can fail if the plugin has been closed before
        and some stray reference is hanging arround).
        If not None, will use the given plugin instance. Plugin can be opened with open_plugin(viewer).

    """
    if plugin is None:
        plugin = _main_widget.MainWindow.get_last_instance()
    if not plugin:
        _plugin = open_plugin(napari.current_viewer())
    else:
        _plugin = plugin

    try:
        if fov_id is not None:
            _plugin._filter_controller.widget.position.setCurrentText(fov_id)
        if additional_filter is not None:
            _plugin._filter_controller.widget.additional_filter_combobox.setCurrentText(
                additional_filter
            )
        if track_length is not None:
            _plugin._filter_controller.widget.min_tracklength_spinbox.setValue(
                track_length[0]
            )
            _plugin._filter_controller.widget.max_tracklength_spinbox.setValue(
                track_length[1]
            )
    except RuntimeError:
        raise RuntimeError(
            "Cannot find the plugin. Either specify a plugin or open one."
        )

    _plugin._filter_controller.widget.filter_input_data.click()


def run_binarization_only(
    bias_method: Literal["none", "runmed", "lm"],
    smooth_k: int,
    bias_k: int,
    polyDeg: int,
    bin_peak_threshold: float,
    bin_threshold: float,
    interpolate: bool = True,
    clip: bool = False,
    clip_range: tuple[float, float] = (0.01, 0.99),
    plugin: _main_widget.MainWindow | None = None,
):
    """Run binarization only. Bypasses the binarization dialog.

    Parameters
    ----------
    bias_method : Literal['none', 'runmed', 'lm']
        Method to use for detrending.
    smooth_k : int
        Size of the local short-range smoothing kernel.
    bias_k : int
        Size of the global long-range smoothing kernel.
    polyDeg : int
        Degree of the polynomial to use for bias correction. Used only when bias_method is 'lm'.
    bin_peak_threshold : float
        Threshold above which trajectories are rescaled.
    bin_threshold : float
        Threshold to use for binarization.
    interpolate : bool
        Whether to interpolate the data before binarization.
    clip : bool
        Whether to clip the data before binarization.
    clip_range : tuple[float, float]
        Range to clip the data to. Used only when clip is True.
    plugin : _main_widget.MainWindow | None
        If None, will try to get the last instance of the plugin (can fail if the plugin has been closed before and
        some stray reference is hanging arround).
        If not None, will use the given plugin instance. Plugin can be opened with open_plugin(viewer).
    """
    if plugin is None:
        plugin = _main_widget.MainWindow.get_last_instance()
    if not plugin:
        _plugin = open_plugin(napari.current_viewer())
    else:
        _plugin = plugin

    try:
        _plugin._arcos_widget.widget.bias_method.setCurrentText(bias_method)
        _plugin._arcos_widget.widget.smooth_k.setValue(smooth_k)
        _plugin._arcos_widget.widget.bias_k.setValue(bias_k)
        _plugin._arcos_widget.widget.polyDeg.setValue(polyDeg)
        _plugin._arcos_widget.widget.bin_peak_threshold.setValue(bin_peak_threshold)
        _plugin._arcos_widget.widget.bin_threshold.setValue(bin_threshold)
        _plugin._arcos_widget.widget.interpolate_meas.setChecked(interpolate)
        _plugin._arcos_widget.widget.clip_meas.setChecked(clip)
        _plugin._arcos_widget.widget.clip_low.setValue(clip_range[0])
        _plugin._arcos_widget.widget.clip_high.setValue(clip_range[1])

        _plugin._arcos_widget.widget.run_binarization_only.click()
    except RuntimeError:
        raise RuntimeError(
            "Cannot find the plugin. Either specify a plugin or open one."
        )


def run_arcos(
    bias_method: Literal["none", "runmed", "lm"],
    smooth_k: int,
    bias_k: int,
    polyDeg: int,
    bin_peak_threshold: float,
    bin_threshold: float,
    interpolate: bool = True,
    clip: bool = False,
    clip_range: tuple[float, float] = (0.01, 0.99),
    eps_estimation: Literal["median", "kneepoint", "manual"] = "manual",
    eps: float = 0.1,
    eps_prev: float | None = None,
    min_clustersize: int = 3,
    min_duration: int = 3,
    min_event_size: int = 3,
    add_convex_hull: bool = True,
    plugin: _main_widget.MainWindow | None = None,
):
    """Run ARCoS. Bypasses the ARCoS dialog.

    Parameters
    ----------
    bias_method : Literal['none', 'runmed', 'lm']
        Method to use for detrending.
    smooth_k : int
        Size of the local short-range smoothing kernel.
    bias_k : int
        Size of the global long-range smoothing kernel.
    polyDeg : int
        Degree of the polynomial to use for bias correction. Used only when bias_method is 'lm'.
    bin_peak_threshold : float
        Threshold above which trajectories are rescaled.
    bin_threshold : float
        Threshold to use for binarization.
    interpolate : bool
        Whether to interpolate the data before binarization.
    clip : bool
        Whether to clip the data before binarization.
    clip_range : tuple[float, float]
        Range to clip the data to. Used only when clip is True.
    eps_estimation : Literal['median', 'kneepoint', 'manual']
        Method to use for estimating the epsilon parameter for DBSCAN.
    eps : float
        Epsilon parameter for DBSCAN. Used only when eps_estimation is 'manual'.
    eps_prev : float
        Distance to link clusters between frames. if None, uses eps.
    min_clustersize : int
        Minimum number of points in a cluster.
    min_duration : int
        Minimum number of frames for a cluster to be considered an event. Otherwise,
        it is filtered out.
    min_event_size : int
        Minimum number of points in an event. Otherwise, it is filtered out.
        Works only if a track_id column is present in the data.
    add_convex_hull : bool
        Whether to add a convex hull around the events.
    plugin : _main_widget.MainWindow | None
        If None, will try to get the last instance of the plugin (can fail if the plugin has been closed before and
        some stray reference is hanging arround).
        If not None, will use the given plugin instance. Plugin can be opened with open_plugin(viewer).
    """
    if plugin is None:
        plugin = _main_widget.MainWindow.get_last_instance()
    if not plugin:
        _plugin = open_plugin(napari.current_viewer())
    else:
        _plugin = plugin

    try:
        _plugin._arcos_widget._update_what_to_run_all()
    except RuntimeError:
        raise RuntimeError(
            "Cannot find the plugin. Either specify a plugin or open one."
        )
    _plugin._arcos_widget.widget.bias_method.setCurrentText(bias_method)
    _plugin._arcos_widget.widget.smooth_k.setValue(smooth_k)
    _plugin._arcos_widget.widget.bias_k.setValue(bias_k)
    _plugin._arcos_widget.widget.polyDeg.setValue(polyDeg)
    _plugin._arcos_widget.widget.bin_peak_threshold.setValue(bin_peak_threshold)
    _plugin._arcos_widget.widget.bin_threshold.setValue(bin_threshold)
    _plugin._arcos_widget.widget.interpolate_meas.setChecked(interpolate)
    _plugin._arcos_widget.widget.clip_meas.setChecked(clip)
    _plugin._arcos_widget.widget.clip_low.setValue(clip_range[0])
    _plugin._arcos_widget.widget.clip_high.setValue(clip_range[1])
    _plugin._arcos_widget.widget.eps_estimation_combobox.setCurrentText(eps_estimation)
    _plugin._arcos_widget.widget.neighbourhood_size.setValue(eps)
    if eps_prev is not None:
        _plugin._arcos_widget.widget.Cluster_linking_dist_checkbox.setChecked(True)
        _plugin._arcos_widget.widget.epsPrev_spinbox.setValue(eps_prev)
    else:
        _plugin._arcos_widget.widget.Cluster_linking_dist_checkbox.setChecked(False)

    _plugin._arcos_widget.widget.min_clustersize.setValue(min_clustersize)
    _plugin._arcos_widget.widget.min_dur.setValue(min_duration)
    _plugin._arcos_widget.widget.total_event_size.setValue(min_event_size)
    _plugin._arcos_widget.widget.add_convex_hull_checkbox.setChecked(add_convex_hull)

    _plugin._arcos_widget.widget.update_arcos.click()


def get_arcos_output(plugin: _main_widget.MainWindow | None = None):
    """Get the ARCoS output dataframe.

    Parameters
    ----------
    plugin : _main_widget.MainWindow | None
        If None, will try to get the last instance of the plugin (can fail if the plugin has been closed before and
        some stray reference is hanging arround).
        If not None, will use the given plugin instance. Plugin can be opened with open_plugin(viewer).

    Returns
    -------
    df : pd.DataFrame
        Dataframe with the ARCoS output.
    stats : pd.DataFrame
        Dataframe with summary statistics of the ARCOS output.
    """
    if plugin is None:
        plugin = _main_widget.MainWindow.get_last_instance()
    if not plugin:
        _plugin = open_plugin(napari.current_viewer())
    else:
        _plugin = plugin

    try:
        return _plugin.data.arcos_output.value, _plugin.data.arcos_stats.value
    except RuntimeError:
        raise RuntimeError(
            "Cannot find the plugin. Either specify a plugin or open one."
        )


def get_current_arcos_plugin():
    """Get the current ARCOS plugin instance.

    Returns
    -------
    plugin : _main_widget.MainWindow
        The plugin instance.
    """
    plugin = _main_widget.MainWindow.get_last_instance()
    if not plugin:
        plugin = open_plugin(napari.current_viewer())
    return plugin
