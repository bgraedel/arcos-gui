"""Sample data for arcos_gui. Will be added to the napari sample data menu."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import requests
from arcos_gui import _main_widget
from arcos_gui.processing import columnnames
from napari import current_viewer
from napari.utils.notifications import show_info
from skimage.io import imread
from tqdm import tqdm

if TYPE_CHECKING:
    import napari.viewer


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


def resolve(name, basepath=None):
    """Resolve path to file in the package directory."""
    if not basepath:
        basepath = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(basepath, name)


def download(url: str, fname: str):
    """Download file from url and save it to fname."""
    resp = requests.get(url, stream=True, timeout=10)
    curr_request = requests.head(url, timeout=10)
    if "text/html" in curr_request.headers["content-type"]:
        raise ValueError("URL is not a file")
    total = int(resp.headers.get("content-length", 0))
    with open(fname, "wb") as file, tqdm(
        desc=fname,
        total=total,
        unit="b",
        unit_scale=True,
        unit_divisor=1024,
    ) as pbar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            pbar.update(size)


def load_synthetic_dataset(plugin: _main_widget.MainWindow | None = None):
    """Load sample data into stored_variables"""
    if plugin is None:
        plugin = _main_widget.MainWindow.get_last_instance()
    if not plugin:
        _plugin = open_plugin(current_viewer())
    else:
        _plugin = plugin

    sample_data_path = str(resolve(Path("arcos_data.csv")))
    columns = columnnames(
        frame_column="t",
        position_id="None",
        object_id="id",
        x_column="x",
        y_column="y",
        z_column="None",
        measurement_column_1="m",
        measurement_column_2="None",
        additional_filter_column="None",
        measurement_math_operation="None",
        measurement_bin=None,
        measurement_resc=None,
        collid_name="collid",
        measurement_column="m",
    )

    try:
        _plugin._input_controller.load_sample_data(sample_data_path, columns)
        _plugin._layer_prop_controller.widget.LUT.setCurrentText("viridis")
    except RuntimeError:
        show_info("Cannot find the plugin, please open it first")
    return []


def load_real_dataset(
    load_image: bool = True, plugin: _main_widget.MainWindow | None = None
):
    """Load sample data and get image correspoinding to the data"""
    if plugin is None:
        plugin = _main_widget.MainWindow.get_last_instance()
    if not plugin:
        _plugin = open_plugin(current_viewer())
    else:
        _plugin = plugin
    image_url = "https://macdobry.net/ARCOS/data/MDCK_example_event.tif"
    img_path = resolve("MDCK_example_event.tif")
    if not os.path.exists(img_path) and load_image:
        try:
            show_info("Image not found: Downloading example image")
            download(image_url, img_path)
        except Exception:
            show_info("Image not found: Downloading example image failed")

    if os.path.exists(img_path):
        img = imread(img_path)
        img_data_tuple = [(img, {"name": "Example ERK Wave", "colormap": "inferno"})]
    else:
        img_data_tuple = []

    columns = columnnames(
        frame_column="t",
        position_id="None",
        object_id="id",
        x_column="x",
        y_column="y",
        z_column="None",
        measurement_column_1="m",
        measurement_column_2="None",
        additional_filter_column="None",
        measurement_math_operation="None",
        measurement_bin=None,
        measurement_resc=None,
        collid_name="collid",
        measurement_column="m",
    )
    try:
        sample_data_path = str(resolve(Path("arcos_data_2.csv")))
        _plugin._input_controller.load_sample_data(sample_data_path, columns)
    except RuntimeError:
        show_info("Cannot find the plugin, please open it first")
    return img_data_tuple
