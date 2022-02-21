from copy import deepcopy

from arcos_gui import export_movie
from skimage import data


def test_resize_napari(make_napari_viewer, qtbot):
    viewer = make_napari_viewer()
    viewer.add_image(data.binary_blobs(length=10, blob_size_fraction=0.2, n_dim=3))
    rgt, rgy, rgx = deepcopy(viewer.dims.range)
    maxx, maxy = rgx[1], rgy[1]
    export_movie.resize_napari([maxx, maxy], viewer)
    viewer.close()


def test_iterate_over_frames(make_napari_viewer, qtbot):
    viewer = make_napari_viewer()
    export_movie.iterate_over_frames(viewer, ".")
    viewer.close()
