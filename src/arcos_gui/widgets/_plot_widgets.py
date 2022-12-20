from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import napari
from arcos_gui.tools import CollevPlotter, NoodlePlot, TimeSeriesPlots
from qtpy import QtCore, QtWidgets
from qtpy.QtGui import QIcon

if TYPE_CHECKING:
    from arcos_gui.processing import DataStorage


class DataPlot(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tsplot_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.tsplot_layout)


# icons
ICONS = Path(__file__).parent.parent / "_icons"

# still need to rewrite actual plots to be a bit nicer


class tsPlotWidget(QtWidgets.QWidget):
    def __init__(
        self,
        viewer: napari.viewer.Viewer,
        data_storage_instance: DataStorage,
        parent=None,
    ):
        super().__init__(parent)
        self.viewer = viewer
        self._data_storage_instance = data_storage_instance
        self.timeseriesplot = TimeSeriesPlots(parent=self)
        self.plot_dialog_data = DataPlot(parent=self)
        self._add_plot_widgets()
        self._add_icon()
        self._data_storage_instance.original_data.value_changed_connect(
            self._on_data_update
        )
        self._data_storage_instance.arcos_binarization.value_changed_connect(
            self._on_data_update
        )
        self._data_storage_instance.selected_object_id.value_changed_connect(
            self._on_data_update
        )

    def _on_data_update(self):
        self._on_data_clear()
        df_orig = self._data_storage_instance.original_data.value
        df_bin = self._data_storage_instance.arcos_binarization.value
        frame_col = self._data_storage_instance.columns.frame_column
        object_id_col = self._data_storage_instance.columns.object_id
        measurement_col = self._data_storage_instance.columns.measurement_column
        x_coord_col = self._data_storage_instance.columns.x_column
        y_coord_col = self._data_storage_instance.columns.y_column
        measurement_resc_col = self._data_storage_instance.columns.measurement_resc
        object_id_number = self._data_storage_instance.selected_object_id.value
        self.timeseriesplot.update_plot(
            df_orig,
            df_bin,
            frame_col,
            object_id_col,
            x_coord_col,
            y_coord_col,
            measurement_col,
            measurement_resc_col,
            object_id_number,
        )

    def _on_data_clear(self):
        self.timeseriesplot._data_clear()

    def _add_icon(self):
        expand_plot_icon = QIcon(str(ICONS / "enlarge_window.png"))
        self.expand_plot.setIcon(expand_plot_icon)
        self.expand_plot.setMaximumSize(30, 30)

    def _open_data_plot(self):
        self.plot_dialog_data.closeEvent = self._close_plot
        self.plot_dialog_data.tsplot_layout.addWidget(self.timeseriesplot)
        self.plot_dialog_data.show()
        self.timeseriesplot_groupbox.hide()

    def _close_plot(self, event):
        self.timeseriesplot_groupbox.layout().removeWidget(self.expand_plot)
        self.tsplot_layout.addWidget(self.timeseriesplot, alignment=QtCore.Qt.AlignTop)
        self.timeseriesplot_groupbox.layout().addWidget(
            self.expand_plot, alignment=QtCore.Qt.AlignRight
        )
        self.timeseriesplot_groupbox.show()

    def _add_plot_widgets(self):
        self.timeseriesplot_groupbox = QtWidgets.QGroupBox("Time Series Plot")
        self.widget_layout = QtWidgets.QVBoxLayout()
        self.tsplot_layout = QtWidgets.QVBoxLayout()
        self.expand_plot = QtWidgets.QPushButton()
        self.timeseriesplot_groupbox.setLayout(self.tsplot_layout)
        self.setLayout(self.widget_layout)
        self.tsplot_layout.addWidget(self.timeseriesplot)
        self.widget_layout.addWidget(self.timeseriesplot_groupbox)
        self.timeseriesplot_groupbox.layout().addWidget(
            self.expand_plot, alignment=QtCore.Qt.AlignRight
        )
        self.expand_plot.clicked.connect(self._open_data_plot)


class collevPlotWidget(QtWidgets.QWidget):
    def __init__(
        self,
        viewer: napari.viewer.Viewer,
        data_storage_instance: DataStorage,
        parent=None,
    ):
        super().__init__(parent)
        self.viewer = viewer
        self._data_storage_instance = data_storage_instance
        self.collevplot = CollevPlotter(self.viewer, parent=self)
        self.noodle_plot = NoodlePlot(self.viewer, parent=self)
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.collevplot, "Collev Plot")
        self.tab_widget.addTab(self.noodle_plot, "Noodle Plot")
        self.plot_dialog_collev = DataPlot(parent=self)
        self._add_plot_widgets()
        self._add_icon()

        self._data_storage_instance.arcos_binarization.value_changed_connect(
            self._data_clear
        )
        self._data_storage_instance.arcos_output.value_changed_connect(
            self._on_data_update
        )
        self._data_storage_instance.original_data.value_changed_connect(
            self._data_clear
        )
        self.tab_widget.setCurrentIndex(1)

    def _on_data_update(self):
        frame_col = self._data_storage_instance.columns.frame_column
        oid_col = self._data_storage_instance.columns.object_id
        x_coord = self._data_storage_instance.columns.x_column
        y_coord = self._data_storage_instance.columns.y_column
        z_coord = self._data_storage_instance.columns.z_column
        point_size = self._data_storage_instance.point_size
        arcos_data = self._data_storage_instance.arcos_output.value.copy()
        self.collevplot.update_plot(
            frame_col, oid_col, x_coord, y_coord, z_coord, arcos_data, point_size
        )
        self.noodle_plot.update_plot(
            frame_col, oid_col, x_coord, y_coord, z_coord, arcos_data, point_size
        )

    def _data_clear(self):
        self.collevplot.clear_plot()
        self.noodle_plot.clear_plot()

    def _open_plot(self):
        self.plot_dialog_collev.closeEvent = self._close_plot
        self.plot_dialog_collev.tsplot_layout.addWidget(self.tab_widget)
        self.plot_dialog_collev.show()
        self.collevplot_goupbox.hide()

    def _close_plot(self, event):
        self.collevplot_goupbox.layout().removeWidget(self.expand_plot)
        self.evplot_layout.addWidget(self.tab_widget, alignment=QtCore.Qt.AlignTop)
        self.collevplot_goupbox.layout().addWidget(
            self.expand_plot, alignment=QtCore.Qt.AlignRight
        )
        self.collevplot_goupbox.show()

    def _add_plot_widgets(self):
        self.collevplot_goupbox = QtWidgets.QGroupBox("Event Plot")
        self.widget_layout = QtWidgets.QVBoxLayout()
        self.evplot_layout = QtWidgets.QVBoxLayout()
        self.expand_plot = QtWidgets.QPushButton()
        self.collevplot_goupbox.setLayout(self.evplot_layout)
        self.widget_layout.addWidget(self.collevplot_goupbox)
        self.collevplot_goupbox.layout().addWidget(self.tab_widget)
        self.collevplot_goupbox.layout().addWidget(
            self.expand_plot, alignment=QtCore.Qt.AlignRight
        )
        self.expand_plot.clicked.connect(self._open_plot)
        self.setLayout(self.widget_layout)

    def _add_icon(self):
        expand_plot_icon = QIcon(str(ICONS / "enlarge_window.png"))
        self.expand_plot.setIcon(expand_plot_icon)
        self.expand_plot.setMaximumSize(30, 30)


if __name__ == "__main__":
    import sys

    from arcos_gui.processing import DataStorage  # noqa: F811

    viewer = napari.Viewer()
    app = QtWidgets.QApplication(sys.argv)
    ds = DataStorage()
    window = collevPlotWidget(viewer, ds)
    window.show()
    sys.exit(app.exec_())
