from copy import deepcopy

import numpy as np
from skimage import io
from tqdm import tqdm


def resize_napari(final_shape, viewer):
    """Iterate over window until screenshot size matches given shape.
    Center the camera and set zoom to 1 (1 canvas pixel == 1 data pixel)"""
    shape = final_shape  # init with good guess
    viewer.window.resize(shape[0], shape[1])
    for i in range(80):  # nb iterations
        current_shape = viewer.screenshot().shape[:2]
        error = np.subtract(final_shape, list(current_shape))
        error = error * 0.5  # how quick should the error be reduced
        if sum(error) == 0:
            print(f"Reached final window size after {i} iterations.")
            break
        shape = [shape[0] + error[0], shape[1] + error[1]]
        viewer.window.resize(shape[1].astype(int), shape[0].astype(int) * 2)
    viewer.reset_view()
    if len(viewer.dims.range) == 3:
        rgt, rgy, rgx = deepcopy(viewer.dims.range)
    if len(viewer.dims.range) == 4:
        rgt, rgz, rgy, rgx = deepcopy(viewer.dims.range)
    # Napari uses float64 for dims
    maxx, maxy = rgx[1], rgy[1]
    zoom_factor = [final_shape[0] / maxx, final_shape[1] / maxy]
    viewer.camera.zoom = min(zoom_factor)
    viewer.screenshot()


class MovieExporter:
    def __init__(self, viewer, automatic_viewer_size, outdir, width, height):
        self.viewer = viewer
        self.automatic_viewer_size: bool = automatic_viewer_size
        self.outdir = outdir
        self.height = height
        self.width = width

    def run(self):
        self.export_image_sequence(self.viewer, self.outdir)

    def export_image_sequence(self, viewer, outdir):
        """Export a movie from a napari viewer.
        Parameters
        ----------
        viewer : napari.Viewer
            napari viewer object.
        outdir : str
            Path to output directory.
        fps : int
            Frames per second.
        """
        # Resize window to match screenshot size
        if self.automatic_viewer_size:
            resize_napari((self.width, self.height), viewer)
        # Iterate over frames
        self.iterate_over_frames(viewer, outdir)

    def iterate_over_frames(self, viewer, outdir):
        for frame in tqdm(range(int(viewer.dims.range[0][1]))):
            if len(viewer.dims.current_step) == 3:
                viewer.dims.current_step = (frame, 0, 0)
            elif len(viewer.dims.current_step) == 4:
                viewer.dims.current_step = (frame, 0, 0, 0)
            screenshot = viewer.screenshot(path=None, canvas_only=True, flash=False)
            io.imsave(
                str(outdir) + "_%03d.png" % frame, screenshot, check_contrast=False
            )
