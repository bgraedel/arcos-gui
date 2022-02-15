from magicgui import magicgui

@magicgui(call_button="Set Options", position = {"choices": ['upper_right', 'upper_left', 'lower_right', 'lower_left', 'center']}, size = {"min": 0, "max": 1000}, x_shift = {"min": -1000, "max": 1000}, y_shift = {"min": -1000, "max": 1000}) 
def timestamp_options(start_time=0, step_time=1, prefix='T = ', suffix=' frame', position='upper_left', size=12, x_shift=0, y_shift=0):
    timestamp_options.close()

def show_timestamp_options():
    timestamp_options.show() 


"""Dialog with magicgui for selecting columns"""
@magicgui(Ok = {"widget_type": "PushButton"}, 
        frame={"choices": ["None"]}, 
        track_id = {"choices":["None"]},
        x_coordinates={"choices": ["None"]}, 
        y_coordinates = {"choices":["None"]},
        measurment={"choices": ["None"]}, 
        field_of_view_id = {"choices":["None"]},
        dicCols = {"visible": False},
        auto_call=True)
def columnpicker(frame= "None", 
                track_id = "None",
                x_coordinates = "None",
                y_coordinates = "None",
                measurment = "None",
                field_of_view_id = "None", 
                Ok = False, 
                dicCols: dict = {'frame': "None", 
                'x_coordinates': "None", 
                'y_coordinates': "None",
                'track_id': "None",
                'measurment': "None",
                'field_of_view_id': "None"}):
    pass

