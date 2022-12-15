from pathlib import Path

import napari
from arcos_gui._arcos_widget import ArcosWidget
from arcos_gui._exporting_widget import ExportWidget
from arcos_gui._filter_widget import FilterDataWidget
from arcos_gui._input_data_widget import InputDataWidget
from arcos_gui._layer_maker import Layermaker
from arcos_gui._plot_widgets import collevplot_widget, tsplot_widget
from arcos_gui._visualization_settings_widget import LayerPropertiesWidget
from arcos_gui.temp_data_storage import data_storage
from qtpy import QtWidgets, uic

# from arcos_gui._plot_widget import PlotWidget


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
        self.setup_ui()

        self.data_storage_instance = data_storage()

        self.input_data_widget = InputDataWidget(
            viewer=self.viewer,
            data_storage_instance=self.data_storage_instance,
            parent=self,
        )
        self.filter_data_widget = FilterDataWidget(
            data_storage_instance=self.data_storage_instance, parent=self
        )
        self.arcos_widget = ArcosWidget(
            data_storage_instance=self.data_storage_instance, parent=self
        )
        self.layer_prop_widget = LayerPropertiesWidget(
            viewer=self.viewer,
            data_storage_instance=self.data_storage_instance,
            parent=self,
        )
        self.ts_plots_widget = tsplot_widget(self.viewer, self.data_storage_instance)
        self.collev_plots_widget = collevplot_widget(
            self.viewer, self.data_storage_instance
        )
        self.export_widget = ExportWidget(
            viewer=self.viewer,
            data_storage_instance=self.data_storage_instance,
            parent=self,
        )

        self.layermaker = Layermaker(self.viewer, self.data_storage_instance)

        self._add_widgets()

        self._connect_signals()

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


if __name__ == "__main__":
    pass

    from napari import Viewer

    viewer = Viewer()
    win = MainWindow(viewer)
    dw = viewer.window.add_dock_widget(win, name="ARCOS", area="right")
    napari.run()
