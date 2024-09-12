from __future__ import annotations

import os
import tempfile

from arcos_gui.tools._image_sequence_export import MovieExporter
from skimage.data import brain


def test_movie_exporter(make_napari_viewer):
    viewer = make_napari_viewer()
    viewer.add_image(brain())
    with tempfile.TemporaryDirectory() as tmpdir:
        export_path = os.path.join(tmpdir)
        exporter = MovieExporter(viewer, export_path)
        exporter.run("png", 12, 1, "test_movie")
        filelist = os.listdir(os.path.join(tmpdir, "test_movie"))
        for f in filelist[:]:
            if not (f.endswith(".png")):
                filelist.remove(f)
        assert filelist[0].endswith(".png")
