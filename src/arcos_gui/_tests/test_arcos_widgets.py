import pytest
from skimage import data
from arcos_gui._arcos_widgets import add_timestamp, export_data, filepicker, show_output_csv_folder, output_movie_folder, show_output_movie_folder, output_csv_folder
from arcos_gui.magic_guis import timestamp_options
import pandas as pd
from pandas.testing import assert_frame_equal
from os import sep, path

@pytest.fixture
def data_frame():
    col_2= list(range(5,10))
    col_2.extend(list(range(10,5,-1)))
    d= {'time' : [1 for i in range(0,10)], 'X': list(range(0,10)), 'Y': col_2, 'collid': [1 for i in range(0,10)]}
    df = pd.DataFrame(data=d)
    
    return df

def test_add_timestamp(make_napari_viewer):
    viewer = make_napari_viewer(block_plugin_discovery=False)
    viewer.add_image(data.binary_blobs(length=10, blob_size_fraction=0.2, n_dim=3), name = "Image")
    timestamp_options.prefix.value = "Time= "
    mywidget = add_timestamp()
    viewer.window.add_dock_widget(mywidget)
    mywidget()
    assert viewer.layers['Timestamp']

def test_export_data_widget_csv_no_data(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    mywidget = export_data()
    viewer.window.add_dock_widget(mywidget)
    show_output_csv_folder()
    output_csv_folder()
    catptured = capsys.readouterr()
    assert catptured.out == 'INFO: No data to export, run arcos first\n'

def test_export_data_widget_csv_data(make_napari_viewer, tmp_path, data_frame):
    arcos_dir = str(tmp_path)
    viewer = make_napari_viewer()
    mywidget = export_data()
    viewer.window.add_dock_widget(mywidget)
    show_output_csv_folder()
    output_csv_folder.filename.value = arcos_dir
    output_csv_folder(arcos_data=data_frame)
    file = arcos_dir+sep+"arcos_data.csv"
    df = pd.read_csv(file, index_col=0)
    assert_frame_equal(df,data_frame)

def test_export_data_widget_images_no_data(make_napari_viewer,capsys):
    viewer = make_napari_viewer()
    mywidget = export_data()
    viewer.window.add_dock_widget(mywidget)
    show_output_movie_folder()
    output_movie_folder()
    catptured = capsys.readouterr()
    assert catptured.out == 'INFO: No data to export, run arcos first\n'

def test_export_data_widget_images_data(make_napari_viewer,tmp_path):
    viewer = make_napari_viewer()
    image_1 = viewer.add_image(data.binary_blobs(length=1, blob_size_fraction=0.2, n_dim=3))
    arcos_dir = str(tmp_path)
    mywidget = export_data()
    viewer.window.add_dock_widget(mywidget)
    show_output_movie_folder()
    output_movie_folder.filename.value = arcos_dir
    output_movie_folder()
    file = arcos_dir+sep+"arcos_000.png"
    assert path.isfile(file)

def test_filepicker():
    ...
