from dataclasses import dataclass, field

import pandas as pd
from arcos_gui.arcos_module import ARCOS
from napari.utils.colormaps import AVAILABLE_COLORMAPS


# class to store and retrive a number of variables
@dataclass
class data_storage:
    data: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    dataframe: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    layer_names: list = field(default_factory=lambda: [])
    data_merged: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    arcos: ARCOS = None  # type: ignore
    arcos_what_to_run: list = field(default_factory=lambda: ["all"])
    ts_data: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    colormaps = list(AVAILABLE_COLORMAPS)
    current_position = None
    positions = "None"
    min_max = (0, 1)
    lut = "RdYlBu_r"

    def __post_init__(self):
        self.colormaps.append("RdYlBu_r")

    def update_what_to_run(self, to_update: str):
        if to_update not in self.arcos_what_to_run:
            self.arcos_what_to_run.append(to_update)

    def clear_what_to_run(self):
        self.arcos_what_to_run.clear()
