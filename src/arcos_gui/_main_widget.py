from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from arcos_gui.layerutils import Layermaker
from arcos_gui.processing import DataStorage
from arcos_gui.widgets import (
    ArcosWidget,
    BottomBarWidget,
    ExportWidget,
    FilterDataWidget,
    InputDataWidget,
    LayerPropertiesWidget,
    collevPlotWidget,
    tsPlotWidget,
)
from qtpy import QtWidgets, uic

if TYPE_CHECKING:
    import napari.viewer


class _MainUI:
    UI_FILE = str(Path(__file__).parent / "_ui" / "main_widget.ui")

    # The UI_FILE above contains these objects:
    tabWidget: QtWidgets.QTabWidget

    filter_groupBox: QtWidgets.QGroupBox
    inputdata_groupBox: QtWidgets.QGroupBox
    arcos_layout: QtWidgets.QVBoxLayout
    layer_prop_layout: QtWidgets.QVBoxLayout
    export_layout: QtWidgets.QVBoxLayout

    evplots_layout: QtWidgets.QVBoxLayout
    tsplots_layout: QtWidgets.QVBoxLayout

    bottom_bar_layout: QtWidgets.QVBoxLayout

    nbr_collev_display: QtWidgets.QLCDNumber
    help_button: QtWidgets.QPushButton

    def setup_ui(self):
        uic.loadUi(self.UI_FILE, self)  # load QtDesigner .ui file


class MainWindow(QtWidgets.QWidget, _MainUI):
    """
    Widget allowing a user to import a csv file, filter this file,
    choose arcos parameters, choose LUT mappings aswell as shape sizes.
    """

    def __init__(self, viewer: napari.viewer.Viewer, remote=True):
        """Constructs class with provided arguments."""
        super().__init__()
        self.viewer: napari.viewer.Viewer = viewer
        MainWindow._instance = self
        self.setup_ui()

        self.data_storage_instance = DataStorage()
        # self.data_storage_instance.make_verbose()  # uncomment to make callbacks verbose

        self.input_data_widget = InputDataWidget(
            data_storage_instance=self.data_storage_instance,
            parent=self,
        )
        self.filter_data_widget = FilterDataWidget(
            viewer=self.viewer,
            data_storage_instance=self.data_storage_instance,
            parent=self,
        )
        self.arcos_widget = ArcosWidget(
            data_storage_instance=self.data_storage_instance, parent=self
        )
        self.layer_prop_widget = LayerPropertiesWidget(
            viewer=self.viewer,
            data_storage_instance=self.data_storage_instance,
            parent=self,
        )
        self.ts_plots_widget = tsPlotWidget(self.viewer, self.data_storage_instance)
        self.collev_plots_widget = collevPlotWidget(
            self.viewer, self.data_storage_instance
        )
        self.export_widget = ExportWidget(
            viewer=self.viewer,
            data_storage_instance=self.data_storage_instance,
            parent=self,
        )

        self.bottom_bar_widget = BottomBarWidget(
            data_storage_instance=self.data_storage_instance,
            parent=self,
        )

        self.layermaker = Layermaker(self.viewer, self.data_storage_instance)

        self._add_widgets()

        self._connect_signals()

    @classmethod
    def get_last_instance(cls) -> MainWindow | None:
        try:
            return cls._instance
        except AttributeError:
            return None

    def _connect_signals(self):
        self.data_storage_instance.arcos_binarization.value_changed_connect(
            lambda: self.layermaker.make_layers_bin()
        )
        self.data_storage_instance.arcos_output.value_changed_connect(
            lambda: self.layermaker.make_layers_all()
        )
        self.data_storage_instance.timestamp_parameters.value_changed_connect(
            lambda: self.layermaker.make_timestamp_layer()
        )

    def _add_widgets(self):
        self.inputdata_groupBox.layout().addWidget(self.input_data_widget)
        self.filter_groupBox.layout().addWidget(self.filter_data_widget)
        self.arcos_layout.addWidget(self.arcos_widget)
        self.layer_prop_layout.addWidget(self.layer_prop_widget)
        self.tsplots_layout.addWidget(self.ts_plots_widget)
        self.evplots_layout.addWidget(self.collev_plots_widget)
        self.export_layout.addWidget(self.export_widget)
        self.bottom_bar_layout.addWidget(self.bottom_bar_widget)


if __name__ == "__main__":
    import napari

    viewer = napari.Viewer()
    win = MainWindow(viewer)
    dw = viewer.window.add_dock_widget(win, name="ARCOS", area="right")
    napari.run()
