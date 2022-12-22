from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from arcos_gui.processing import timestamp_parameters
from arcos_gui.tools import MovieExporter
from arcos_gui.widgets import timestamp_options
from napari.utils.notifications import show_info
from qtpy import QtWidgets, uic
from qtpy.QtGui import QIcon

if TYPE_CHECKING:
    import napari.viewer
    from arcos_gui.processing import DataStorage

# icons
ICONS = Path(__file__).parent.parent / "_icons"


class _exportwidget:
    UI_FILE = str(Path(__file__).parent.parent / "_ui" / "export_widget.ui")

    # The UI_FILE above contains these objects:

    browse_file_data: QtWidgets.QPushButton
    file_LineEdit_data: QtWidgets.QLineEdit
    base_name_LineEdit_data: QtWidgets.QLineEdit
    data_export_button: QtWidgets.QPushButton
    param_export_button: QtWidgets.QPushButton
    stats_export_button: QtWidgets.QPushButton

    browse_file_img: QtWidgets.QPushButton
    file_LineEdit_img: QtWidgets.QLineEdit
    base_name_LineEdit_img: QtWidgets.QLineEdit
    img_seq_export_button: QtWidgets.QPushButton
    automatic_size_img: QtWidgets.QCheckBox
    spinBox_height_img: QtWidgets.QSpinBox
    spinBox_width_img: QtWidgets.QSpinBox
    add_timestamp_button: QtWidgets.QPushButton

    def setup_ui(self):
        uic.loadUi(self.UI_FILE, self)  # load QtDesigner .ui file
        self.browse_file_icon = QIcon(str(ICONS / "folder-open-line.svg"))
        self.browse_file_data.setIcon(self.browse_file_icon)
        self.browse_file_img.setIcon(self.browse_file_icon)


class ExportWidget(QtWidgets.QWidget, _exportwidget):
    def __init__(
        self,
        viewer: napari.viewer.Viewer,
        data_storage_instance: DataStorage,
        parent=None,
    ):
        super().__init__(parent)
        self.setup_ui()
        self.viewer = viewer
        self._data_storage_instance = data_storage_instance
        self.current_date = self._get_current_date()
        self._connect_callbacks()

    def _get_current_date(self):
        now = datetime.now()
        return now.strftime("%Y%m%d")

    def _export_arcos_data(self):
        if self._data_storage_instance.arcos_output.value.empty:
            show_info("No data to export, run arcos first")
        else:
            path = Path(self.file_LineEdit_data.text())
            output_name = f"{self.current_date}_{self.base_name_LineEdit_data.text()}_arcos_output.csv"
            outpath = os.path.join(path, output_name)
            self._data_storage_instance.arcos_output.value.to_csv(outpath, index=False)
            show_info(f"wrote csv file to {outpath}")

    def _export_arcos_stats(self):
        if self._data_storage_instance.arcos_stats.value.empty:
            show_info("No data to export, run arcos first")
        else:
            path = Path(self.file_LineEdit_data.text())
            output_name = f"{self.current_date}_{self.base_name_LineEdit_data.text()}_arcos_stats.csv"
            outpath = os.path.join(path, output_name)
            self._data_storage_instance.arcos_stats.value.to_csv(outpath, index=False)
            show_info(f"wrote csv file to {outpath}")

    def _export_arcos_params(self):
        if self._data_storage_instance.arcos_output.value.empty:
            show_info("No data to export, run arcos first")
        else:
            path = Path(self.file_LineEdit_data.text())
            output_name = f"{self.current_date}_{self.base_name_LineEdit_data.text()}_arcos_params.csv"
            outpath = os.path.join(path, output_name)
            self._data_storage_instance.arcos_parameters.as_dataframe.to_csv(
                outpath, index=False
            )
            show_info(f"wrote csv file to {outpath}")

    def _export_image_series(self):
        if self.viewer.layers == []:
            show_info("No layers to export")
        else:
            path = Path(self.file_LineEdit_img.text())
            output_name = (
                f"{self.current_date}_{self.base_name_LineEdit_img.text()}_arcos_output"
            )
            outpath = os.path.join(path, output_name)
            MovieExporter(
                self.viewer,
                self.automatic_size_img.isChecked(),
                outpath,
                self.spinBox_width_img.value(),
                self.spinBox_height_img.value(),
            ).run()

    def _browse_file_data(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", os.getcwd()
        )
        self.file_LineEdit_data.setText(path)

    def _browse_file_img(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory", os.getcwd()
        )
        self.file_LineEdit_img.setText(path)

    def _add_timestamp(self):
        self.ts_dialog = timestamp_options(self.parent())
        self.ts_dialog.set_options.clicked.connect(self._set_timestamp_options)
        self.ts_dialog.show()

    def _set_timestamp_options(self):
        start_time = self.ts_dialog.start_time.value()
        step_time = self.ts_dialog.step_time.value()
        prefix = self.ts_dialog.prefix.text()
        suffix = self.ts_dialog.suffix.text()
        position = self.ts_dialog.position.currentText()
        size = self.ts_dialog.ts_size.value()
        x_shift = self.ts_dialog.x_shift.value()
        y_shift = self.ts_dialog.y_shift.value()
        self._data_storage_instance.timestamp_parameters = timestamp_parameters(
            start_time,
            step_time,
            prefix,
            suffix,
            position,
            size,
            x_shift,
            y_shift,
        )

    def _connect_callbacks(self):
        self.browse_file_data.clicked.connect(self._browse_file_data)
        self.data_export_button.clicked.connect(self._export_arcos_data)
        self.stats_export_button.clicked.connect(self._export_arcos_stats)
        self.param_export_button.clicked.connect(self._export_arcos_params)
        self.browse_file_img.clicked.connect(self._browse_file_img)
        self.img_seq_export_button.clicked.connect(self._export_image_series)
        self.add_timestamp_button.clicked.connect(self._add_timestamp)


if __name__ == "__main__":
    import sys

    from arcos_gui.processing import DataStorage  # noqa: F811
    from napari import Viewer

    viewer = Viewer()

    app = QtWidgets.QApplication(sys.argv)
    ds = DataStorage()
    window = ExportWidget(viewer, ds)
    ds.timestamp_parameters.value_changed_connect(
        lambda: print(ds.timestamp_parameters)
    )
    window.show()
    sys.exit(app.exec_())
