"""Main widget of the ARCOS GUI. Contains all other widgets.

Each widget is a tab in the main widget. Creates instances of all other widgets
as well as the data storage and layermaker.
The MainWidget is the entry point for the napari plugin.
"""
from __future__ import annotations

import weakref
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
    maintabwidget: QtWidgets.QTabWidget

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

    _instance = None

    def __init__(self, viewer: napari.viewer.Viewer, parent=None):
        """Constructs class with provided arguments."""
        super().__init__(parent=parent)
        self.viewer: napari.viewer.Viewer = viewer
        self._widget = _MainUI(self)
        MainWindow._instance = weakref.ref(self)

        self.setLayout(self._widget.layout())

        self.data = DataStorage()
        # self.data_storage_instance.set_verbose(
        #     True
        # )  # uncomment to make callbacks verbose

        self._input_controller = InputdataController(
            data_storage_instance=self.data,
            std_out=show_info,
            viewer=self.viewer,
            parent=self,
        )
        self._filter_controller = FilterController(
            viewer=self.viewer,
            data_storage_instance=self.data,
            parent=self,
        )
        self._arcos_widget = ArcosController(
            data_storage_instance=self.data,
            parent=self,
        )
        self._layer_prop_controller = LayerpropertiesController(
            viewer=self.viewer,
            data_storage_instance=self.data,
            parent=self,
        )
        self._ts_plots_widget = tsPlotWidget(self.viewer, self.data, self)
        self._collev_plots_widget = collevPlotWidget(self.viewer, self.data, self)
        self._export = ExportController(
            viewer=self.viewer,
            data_storage_instance=self.data,
            parent=self,
        )

        self._bottom_bar = BottombarController(
            data_storage_instance=self.data,
            parent=self._widget,
        )

        self._layermaker = Layermaker(self.viewer, self.data)
        self._add_widgets()
        self._connect_signals()

    @classmethod
    def get_last_instance(cls) -> MainWindow | None:
        """Returns the last instance of this class. Returns None if no instance exists."""
        instance = cls._instance() if callable(cls._instance) else None

        if instance:
            try:
                instance._widget.maintabwidget.currentIndex()
                return instance
            except (AttributeError, RuntimeError):
                # The Qt object is no longer valid
                del cls._instance

        return None

    def _connect_signals(self):
        self.data.arcos_binarization.value_changed.connect(
            self._layermaker.make_layers_bin
        )
        self.data.arcos_output.value_changed.connect(self._layermaker.make_layers_all)

    def _add_widgets(self):
        self._widget.inputdata_groupBox.layout().addWidget(
            self._input_controller.widget
        )
        self._widget.filter_groupBox.layout().addWidget(self._filter_controller.widget)
        self._widget.arcos_layout.addWidget(self._arcos_widget.widget)
        self._widget.layer_prop_layout.addWidget(self._layer_prop_controller.widget)
        self._widget.tsplots_layout.addWidget(self._ts_plots_widget)
        self._widget.evplots_layout.addWidget(self._collev_plots_widget)
        self._widget.export_layout.addWidget(self._export.widget)
        self._widget.bottom_bar_layout.addWidget(self._bottom_bar.widget)


if __name__ == "__main__":
    import napari

    viewer = napari.Viewer()
    win = MainWindow(viewer)
    dw = viewer.window.add_dock_widget(win, name="ARCOS", area="right")
    napari.run()
