from __future__ import annotations

import os
from pathlib import Path

import requests
from arcos_gui import __main__, _main_widget
from arcos_gui.processing import columnnames
from napari import current_viewer
from napari.utils.notifications import show_info
from skimage.io import imread
from tqdm import tqdm


def resolve(name, basepath=None):
    if not basepath:
        basepath = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(basepath, name)


def download(url: str, fname: str):
    resp = requests.get(url, stream=True)
    r = requests.head(url)
    if "text/html" in r.headers["content-type"]:
        raise ValueError("URL is not a file")
    total = int(resp.headers.get("content-length", 0))
    with open(fname, "wb") as file, tqdm(
        desc=fname,
        total=total,
        unit="b",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


def load_synthetic_dataset():
    """Load sample data into stored_variables"""
    widget = _main_widget.MainWindow.get_last_instance()
    if not widget:
        widget = __main__.main(current_viewer())
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
        measurement_math_operatoin="None",
        measurement_bin=None,
        measurement_resc=None,
        collid_name="collid",
        measurement_column="m",
    )

    widget.input_data_widget.load_sample_data(sample_data_path, columns)
    widget.layer_prop_widget.LUT.setCurrentText("viridis")
    return []


def load_real_dataset(load_image: bool = True):
    """Load sample data and get image correspoinding to the data"""
    widget = _main_widget.MainWindow.get_last_instance()
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

    if not widget:
        widget = __main__.main(current_viewer())
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
        measurement_math_operatoin="None",
        measurement_bin=None,
        measurement_resc=None,
        collid_name="collid",
        measurement_column="m",
    )
    sample_data_path = str(resolve(Path("arcos_data_2.csv")))
    widget.input_data_widget.load_sample_data(sample_data_path, columns)
    # data = np.random.rand(64, 64)
    return img_data_tuple
