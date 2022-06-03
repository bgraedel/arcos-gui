import operator

from magicgui import magicgui

OPERATOR_DICTIONARY = {
    "Divide": (operator.truediv, "Measurement_Ratio"),
    "Multiply": (operator.mul, "Measurement_Product"),
    "Add": (operator.add, "Measurement_Sum"),
    "Subtract": (operator.sub, "Measurement_Difference"),
}

measurement_math_options = list(OPERATOR_DICTIONARY.keys())
measurement_math_options.append("None")


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
    Ok={"widget_type": "PushButton", "tooltip": "Press to load data"},
    frame={
        "choices": ["None"],
        "label": "Frame Column:",
        "tooltip": "Select frame column in input data",
    },
    track_id={
        "choices": ["None"],
        "label": "Object id Column:",
        "tooltip": "Select column representing object track ids in input data",  # noqa: E501
    },
    x_coordinates={
        "choices": ["None"],
        "label": "X Coordinate Column:",
        "tooltip": "Select x coordinate column in input data",
    },
    y_coordinates={
        "choices": ["None"],
        "label": "Y Coordinate Column:",
        "tooltip": "Select y coordinate column in input data",
    },
    z_coordinates={
        "choices": ["None"],
        "label": "Z Coordinate Column:",
        "tooltip": "Select z coordinate column in input data, select None if column does not exist",  # noqa: E501
    },
    measurment={
        "choices": ["None"],
        "label": "Measurement Column:",
        "tooltip": "Select measurement column in input data",
    },
    field_of_view_id={
        "choices": ["None"],
        "label": "Field of View/Position Column:",
        "tooltip": "Select fov column in input data, select None if column does not exist",  # noqa: E501
    },
    additional_filter={
        "choices": ["None"],
        "label": "Additional Filter Column:",
        "tooltip": "Select additional filter column, for example Well of a wellplate, select None if column does not exist",  # noqa: E501
    },
    second_measurment={
        "choices": ["None"],
        "label": "Second Measurement Column:",
        "visible": False,
        "tooltip": "Select second measurement",
    },
    measurement_math={
        "widget_type": "RadioButtons",
        "orientation": "horizontal",
        "choices": measurement_math_options,
        "label": "Math on first and \n second measurement:",
        "tooltip": "Choose operation to calculate the measurment to be used in arcos calculation on first and second measurement",  # noqa: E501
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
