"""Main widget of the ARCOS GUI. Contains all other widgets.

Each widget is a tab in the main widget. Creates instances of all other widgets
as well as the data storage and layermaker.
The MainWidget is the entry point for the napari plugin.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from arcos_gui.layerutils import Layermaker
from arcos_gui.processing import DataStorage
from arcos_gui.widgets import (
    ArcosController,
    BottombarController,
    ExportController,
    FilterController,
    InputdataController,
    LayerpropertiesController,
    collevPlotWidget,
    tsPlotWidget,
)
from napari.utils.notifications import show_info
from qtpy import QtWidgets, uic

if TYPE_CHECKING:
    import napari.viewer


class _MainUI(QtWidgets.QWidget):
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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup UI. Loads it from ui file."""
        uic.loadUi(self.UI_FILE, self)  # load QtDesigner .ui file


class MainWindow(QtWidgets.QWidget):
    """
    Widget allowing a user to import a csv file, filter this file,
    choose arcos parameters, choose LUT mappings aswell as shape sizes.
    """

    def __init__(self, viewer: napari.viewer.Viewer):
        """Constructs class with provided arguments."""
        super().__init__()
        self.viewer: napari.viewer.Viewer = viewer
        self.widget = _MainUI(self)
        MainWindow._instance = self
        self.setLayout(self.widget.layout())

        self.data_storage_instance = DataStorage()
        # self.data_storage_instance.set_verbose(
        #     True
        # )  # uncomment to make callbacks verbose

        self.input_controller = InputdataController(
            data_storage_instance=self.data_storage_instance,
            std_out=show_info,
            parent=self.widget,
        )
        self.filter_controller = FilterController(
            viewer=self.viewer,
            data_storage_instance=self.data_storage_instance,
            parent=self.widget,
        )
        self.arcos_widget = ArcosController(
            data_storage_instance=self.data_storage_instance,
            parent=self.widget,
        )
        self.layer_prop_controller = LayerpropertiesController(
            viewer=self.viewer,
            data_storage_instance=self.data_storage_instance,
            parent=self.widget,
        )
        self.ts_plots_widget = tsPlotWidget(self.viewer, self.data_storage_instance)
        self.collev_plots_widget = collevPlotWidget(
            self.viewer, self.data_storage_instance
        )
        self.export = ExportController(
            viewer=self.viewer,
            data_storage_instance=self.data_storage_instance,
            parent=self.widget,
        )

        self.bottom_bar = BottombarController(
            data_storage_instance=self.data_storage_instance,
            parent=self.widget,
        )

        self.layermaker = Layermaker(self.viewer, self.data_storage_instance)

        self._add_widgets()
        self._connect_signals()

    @classmethod
    def get_last_instance(cls) -> MainWindow | None:
        """Returns the last instance of this class. Returns None if no instance exists."""
        try:
            return cls._instance
        except AttributeError:
            return None

    def _connect_signals(self):
        self.data_storage_instance.arcos_binarization.value_changed_connect(
            self.layermaker.make_layers_bin
        )
        self.data_storage_instance.arcos_output.value_changed_connect(
            self.layermaker.make_layers_all
        )
        self.data_storage_instance.timestamp_parameters.value_changed_connect(
            self.layermaker.make_timestamp_layer
        )

    def _add_widgets(self):
        self.widget.inputdata_groupBox.layout().addWidget(self.input_controller.widget)
        self.widget.filter_groupBox.layout().addWidget(self.filter_controller.widget)
        self.widget.arcos_layout.addWidget(self.arcos_widget.widget)
        self.widget.layer_prop_layout.addWidget(self.layer_prop_controller.widget)
        self.widget.tsplots_layout.addWidget(self.ts_plots_widget)
        self.widget.evplots_layout.addWidget(self.collev_plots_widget)
        self.widget.export_layout.addWidget(self.export.widget)
        self.widget.bottom_bar_layout.addWidget(self.bottom_bar.widget)


if __name__ == "__main__":
    import napari

    viewer = napari.Viewer()
    win = MainWindow(viewer)
    dw = viewer.window.add_dock_widget(win, name="ARCOS", area="right")
    napari.run()
