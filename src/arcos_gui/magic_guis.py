import operator

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


OPERATOR_DICTIONARY = {
    "Divide": (operator.truediv, "Measurement_Ratio"),
    "Multiply": (operator.mul, "Measurement_Product"),
    "Add": (operator.add, "Measurement_Sum"),
    "Subtract": (operator.sub, "Measurement_Difference"),
}
measurement_math_options = list(OPERATOR_DICTIONARY.keys())
measurement_math_options.append("None")


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
    additional_filter={"choices": ["None"]},
    second_measurment={"choices": ["None"], "visible": False},
    measurement_math={
        "widget_type": "RadioButtons",
        "orientation": "horizontal",
        "choices": measurement_math_options,
        "label": "Math on first and \n second measurement:",
    },
)
def columnpicker(
    frame="None",
    track_id="None",
    x_coordinates="None",
    y_coordinates="None",
    z_coordinates="None",
    measurment="None",
    second_measurment="None",
    field_of_view_id="None",
    additional_filter="None",
    measurement_math="None",
    Ok=False,
):
    """Dialog with magicgui for selecting columns"""
    columnpicker.Ok.bind(not Ok)


def toggle_visible_second_measurment():
    curr_value = columnpicker.measurement_math.value
    if curr_value in ["None", "1/X"]:
        columnpicker.second_measurment.hide()
    else:
        columnpicker.second_measurment.show()
