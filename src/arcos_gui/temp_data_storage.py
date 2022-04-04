import pandas as pd
from arcos4py import ARCOS
from napari.utils.colormaps import AVAILABLE_COLORMAPS


# store and retrive a number of variables
class data_storage:
    def __init__(self):
        self.layer_names: list = []
        self.data_merged: pd.DataFrame = pd.DataFrame()
        self.arcos: ARCOS = None  # type: ignore
        self.ts_data: pd.DataFrame = pd.DataFrame()
        self.colormaps = list(AVAILABLE_COLORMAPS)
        self.current_position = None
        self.positions = "None"
        self.min_max = (0, 1)
        self.lut = "RdYlBu_r"
        self.colormaps.append("RdYlBu_r")
        self._callbacks = []

    @property
    def filename_for_sample_data(self):
        return self._value

    @filename_for_sample_data.setter
    def filename_for_sample_data(self, new_value):
        self._filename_for_sample_data = new_value
        self._notify_observers(new_value)

    def _notify_observers(self, new_value):
        for callback in self._callbacks:
            callback(new_value)

    def register_callback(self, callback):
        self._callbacks.append(callback)
