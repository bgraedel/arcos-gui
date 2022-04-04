from magicgui import magicgui


@magicgui(
    call_button="Set Options",
    position={
        "choices": ["upper_right", "upper_left", "lower_right", "lower_left", "center"]
    },
    size={"min": 0, "max": 1000},
    x_shift={"min": -1000, "max": 1000},
    y_shift={"min": -1000, "max": 1000},
)
def timestamp_options(
    start_time=0,
    step_time=1,
    prefix="T =",
    suffix="frame",
    position="upper_left",
    size=12,
    x_shift=12,
    y_shift=0,
):
    """
    Widget to choose timestamp options from when called
    """
    timestamp_options.close()


# used as a callback function in main widget file
def show_timestamp_options():
    timestamp_options.show()


@magicgui(
    call_button=False,
    Ok={"widget_type": "PushButton"},
    frame={"choices": ["None"]},
    track_id={"choices": ["None"]},
    x_coordinates={"choices": ["None"]},
    y_coordinates={"choices": ["None"]},
    z_coordinates={"choices": ["None"]},
    measurment={"choices": ["None"]},
    field_of_view_id={"choices": ["None"]},
)
def columnpicker(
    frame="None",
    track_id="None",
    x_coordinates="None",
    y_coordinates="None",
    z_coordinates="None",
    measurment="None",
    field_of_view_id="None",
    Ok=False,
):
    """Dialog with magicgui for selecting columns"""
    columnpicker.Ok.bind(not Ok)
