import pandas as pd
from arcos_gui.arcos_module import ARCOS
from napari.utils.colormaps import AVAILABLE_COLORMAPS


# class to store and retrive a number of variables
class data_storage:
    def __init__(self):
        self._callbacks: list = []
        self.data: pd.DataFrame = pd.DataFrame()
        self._dataframe: pd.DataFrame = pd.DataFrame()
        self.layer_names: list = []
        self.data_merged: pd.DataFrame = pd.DataFrame()
        self.arcos: ARCOS = None  # type: ignore
        self.arcos_what_to_run: list = ["all"]
        self.ts_data: pd.DataFrame = pd.DataFrame()
        self.colormaps = list(AVAILABLE_COLORMAPS)
        self.current_position = None
        self.positions = "None"
        self.min_max = (0, 1)
        self.lut = "RdYlBu_r"

        self.colormaps.append("RdYlBu_r")

    def update_what_to_run(self, to_update: str):
        if to_update not in self.arcos_what_to_run:
            self.arcos_what_to_run.append(to_update)

    def clear_what_to_run(self):
        self.arcos_what_to_run.clear()

    @property
    def dataframe(self):
        return self._dataframe

    @dataframe.setter
    def dataframe(self, new_dataframe):
        self._dataframe = new_dataframe
        self._notify_observers()

    def _notify_observers(self):
        for callback in self._callbacks:
            callback()

    def register_callback(self, callback):
        self._callbacks.append(callback)
