from dataclasses import dataclass, field
import pandas as pd
from napari.utils.colormaps import AVAILABLE_COLORMAPS


# class to store and retrive a number of variables
@dataclass
class data_storage:
    data: pd.DataFrame() = None
    dataframe: pd.DataFrame() = None
    layer_names: list = field(default_factory=lambda : [])
    data_merged: pd.DataFrame() = None
    arcos: object = None
    arcos_what_to_run: list = field(default_factory=lambda : ["all"])
    ts_data: pd.DataFrame() = None
    colormaps = list(AVAILABLE_COLORMAPS)
    current_position = None
    positions = "None"
    min_max = (0,1)
    lut = "RdYlBu_r"

    def __post_init__(self):
        self.colormaps.append("RdYlBu_r")

    def update_current_pos(self, updated_pos):
        self.current_position = updated_pos

    def update_data(self, data_to_update):
        self.data = data_to_update

    def update_dataframe(self, dataframe_to_update):
        self.dataframe = dataframe_to_update

    def update_data_merged(self, merged_data):
        self.data_merged = merged_data

    def update_arcos_object(self, arcos_object):
        self.arcos = arcos_object

    def update_ts_data(self, ts_data):
        self.ts_data = ts_data

    def update_what_to_run(self, to_update: str):
        if to_update not in self.arcos_what_to_run:
            self.arcos_what_to_run.append(to_update)

    def clear_what_to_run(self):
        self.arcos_what_to_run.clear()

    def append_layer_names(self, layer_name_to_update):
        self.layer_names.append(layer_name_to_update)

    def remove_layer_names(self, layer_name_to_remove):
        self.layer_names.remove(layer_name_to_remove)

    def update_positions_list(self, positions):
        self.positions = positions

    def update_color_min_max(self, min_max: tuple):
        self.min_max = min_max
    
    def update_lut(self, lut):
        self.lut = lut

    def get_lut(self):
        return self.lut

    def get_color_min_max(self):
        return self.min_max

    def get_positions_list(self):
        return self.positions

    def get_current_pos(self):
        return self.current_position

    def get_arcos_object(self):
        return self.arcos

    def get_ts_data(self):
        return self.ts_data

    def get_data(self):
        return self.data

    def get_dataframe(self):
        return self.dataframe

    def get_data_merged(self):
        return self.data_merged

    def get_what_to_run(self):
        return self.arcos_what_to_run

    def get_layer_names(self):
        return self.layer_names

    def get_colormaps(self):
        return self.colormaps
