from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from arcos_gui.processing import DataLoader, DataPreprocessor, read_data_header
from arcos_gui.tools import ARCOS_LAYERS, remove_layers_after_columnpicker
from arcos_gui.widgets import columnpicker
from napari.utils.notifications import show_info
from qtpy import QtCore, QtWidgets, uic
from qtpy.QtCore import QThread
from qtpy.QtGui import QIcon, QMovie

if TYPE_CHECKING:
    import pandas as pd
    from arcos_gui.processing import data_storage
    from napari.viewer import Viewer

# icons
ICONS = Path(__file__).parent.parent / "_icons"


class _input_dataUI:
    UI_FILE = str(Path(__file__).parent.parent / "_ui" / "Input_data.ui")

    file_LineEdit: QtWidgets.QLineEdit
    open_file_button: QtWidgets.QPushButton
    browse_file: QtWidgets.QPushButton
    loading: QtWidgets.QLabel

    def setup_ui(self):
        uic.loadUi(self.UI_FILE, self)  # load QtDesigner .ui file
        # set text of Line edit
        self.file_LineEdit.setText(".")
        # set icons
        browse_file_icon = QIcon(str(ICONS / "folder-open-line.svg"))
        self.loading_icon = QMovie(str(ICONS / "Spinner-1s-200px.gif"))
        self.loading_icon.setScaledSize(QtCore.QSize(40, 40))
        # self.loading.setMovie(self.loading_icon)
        self.browse_file.setIcon(browse_file_icon)
        self.open_file_button.setIcon(QIcon(self.loading_icon.currentPixmap()))
        self.loading_icon.stop()

    def set_loading_icon(self, frame=None):
        self.open_file_button.setIcon(QIcon(self.loading_icon.currentPixmap()))

    def hide_loading_icon(self):
        self.open_file_button.setIcon(QIcon())

    def start_loading_icon(self):
        self.loading_icon.start()
        self.loading_icon.frameChanged.connect(self.set_loading_icon)

    def stop_loading_icon(self):
        self.loading_icon.stop()
        self.hide_loading_icon()


class InputDataWidget(QtWidgets.QWidget, _input_dataUI):
    def __init__(
        self, viewer: Viewer, data_storage_instance: data_storage, parent=None
    ):
        self.viewer = viewer
        self.data_storage_instance = data_storage_instance
        super().__init__(parent)
        self.setup_ui()

        # set up file browser
        self.browse_file.clicked.connect(self._browse_files)

        # set up column picker
        self.open_file_button.clicked.connect(self._open_columnpicker)

    def _browse_files(self):
        """Opens a filedialog and saves path as a string in self.filename"""
        self.filename = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load CSV file", str(Path.home()), "csv(*.csv);; csv.gz(*.csv.gz);;"
        )
        self.file_LineEdit.setText(self.filename[0])

    def _open_columnpicker(self):
        """Opens a columnpicker window."""
        extension = [".csv", ".csv.gz"]
        csv_file = self.file_LineEdit.text()
        if not csv_file.endswith(tuple(extension)):
            show_info("Not a csv file")
            return
        csv_file = self.file_LineEdit.text()
        columns, delimiter_value = read_data_header(csv_file)
        old_picked_columns = (
            self.data_storage_instance.columns.pickablepickable_columns_names
        )
        self.picker = columnpicker(
            parent=self.parent(), columnames_instance=self.data_storage_instance.columns
        )

        self.picker.set_column_names(columns)
        self._set_choices_names_from_previous(self.picker, old_picked_columns)
        self.picker.show()
        self.run_data_loading(csv_file, delimiter_value)

    def _set_choices_names_from_previous(self, picker: columnpicker, col_names):
        """Sets the column names from the previous loaded data."""
        for ui_element, column_name in zip(picker.settable_columns, col_names):
            AllItems = [ui_element.itemText(i) for i in range(ui_element.count())]
            if column_name in AllItems:
                ui_element.setCurrentText(column_name)

    def run_data_loading(self, filename, delimiter=None):
        self.loading_thread = QThread()
        self.loading_worker = DataLoader(filename, delimiter)
        self.start_loading_icon()
        self.loading_worker.moveToThread(self.loading_thread)
        # Connect signals and slots
        # this signal ensures that if a user closes the columnpicker window with X
        # the loaded data is not updated in the data storage object and layers are not deleted
        # aswell as the columnnames are not updated

        self.loading_thread.started.connect(self.loading_worker.run)
        self.loading_worker.finished.connect(self.loading_thread.quit)
        self.loading_worker.finished.connect(self.loading_worker.deleteLater)
        self.loading_thread.finished.connect(self.loading_thread.deleteLater)

        self.loading_worker.new_data.connect(self.run_data_preprocessing)

        self.loading_thread.start()
        self.open_file_button.setEnabled(False)

        # Final resets
        self.loading_thread.finished.connect(self.stop_loading_icon)
        # self.thread.finished.connect(self.stop_loading_icon)
        self.loading_thread.finished.connect(
            lambda: print(self.data_storage_instance.columns)
        )

    def run_data_preprocessing(self, loaded_data: pd.DataFrame):
        self.proprocessing_thread = QThread()
        self.preprocessing_worker = DataPreprocessor(
            loaded_data, self.picker, self.data_storage_instance
        )

        self.preprocessing_worker.moveToThread(self.proprocessing_thread)
        self.preprocessing_worker.finished.connect(self.proprocessing_thread.quit)
        self.preprocessing_worker.finished.connect(
            self.preprocessing_worker.deleteLater
        )
        self.proprocessing_thread.finished.connect(
            self.proprocessing_thread.deleteLater
        )

        self.proprocessing_thread.started.connect(self.preprocessing_worker.run)
        self.proprocessing_thread.start()

        self.preprocessing_worker.new_data.connect(self.succesfully_loaded)
        self.preprocessing_worker.aborted.connect(self.loading_aborted)

    def succesfully_loaded(self, dataframe: pd.DataFrame, measuremt_name: str):
        """Updates the data storage with the loaded data."""
        self._remove_old_layers()
        self._set_datastorage_to_default()
        self.data_storage_instance.columns = self.picker.as_columnames_object
        self.data_storage_instance.columns.measurement_column = measuremt_name
        self.data_storage_instance.original_data.value = dataframe

    def loading_aborted(self, err_code):
        """If the loading of the data is aborted, the data storage is not updated."""
        self.open_file_button.setEnabled(True)
        if err_code == 0:
            return
        if err_code == 1:
            show_info("Loading aborted")
            return
        elif err_code == 2:
            show_info("Loading aborted by error, no columns selected")
            return

    def _remove_old_layers(self):
        remove_layers_after_columnpicker(self.viewer, ARCOS_LAYERS.values())

    def _set_datastorage_to_default(self):
        self.data_storage_instance.reset_relevant_attributes(trigger_callback=False)


if __name__ == "__main__":
    import sys

    from arcos_gui.processing import data_storage  # noqa: F811
    from napari.viewer import Viewer  # noqa: F811

    viewer = Viewer()

    app = QtWidgets.QApplication(sys.argv)
    widget = InputDataWidget(viewer, data_storage())
    widget.show()
    sys.exit(app.exec_())
