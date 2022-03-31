from copy import deepcopy

import matplotlib.pyplot as plt
import numpy as np
from magicgui import magicgui
from magicgui.tqdm import tqdm


def resize_napari(final_shape, viewer):
    """Iterate over window until screenshot size matches given shape.
    Center the camera and set zoom to 1 (1 canvas pixel == 1 data pixel)"""
    shape = final_shape  # init with good guess
    viewer.window.resize(shape[0].astype(int), shape[1].astype(int))
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


@magicgui(
    call_button=False,
    label={"widget_type": "Label"},
    Abort={"widget_type": "PushButton"},
    labels=False,
)
def iterate_over_frames(viewer, temp_dir, label="Exporting Frames", Abort=False):
    for frame in tqdm(range(int(viewer.dims.range[0][1]))):
        if not iterate_over_frames.visible:
            break
        if len(viewer.dims.current_step) == 3:
            viewer.dims.current_step = (frame, 0, 0)
        elif len(viewer.dims.current_step) == 4:
            viewer.dims.current_step = (frame, 0, 0, 0)
        screenshot = viewer.screenshot(path=None, canvas_only=True, flash=False)
        fig = plt.figure(frameon=False, dpi=300)
        ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
        fig.add_axes(ax)
        ax.imshow(screenshot)
        ax.axis("off")
        plt.savefig(
            str(temp_dir) + "_%03d.png" % frame, bbox_inches="tight", pad_inches=0
        )
        plt.close()


@iterate_over_frames.Abort.changed.connect
def abort_export():
    iterate_over_frames.close()
