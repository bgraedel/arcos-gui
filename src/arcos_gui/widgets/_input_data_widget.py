"""This module contains the InputDataWidget class.

This widget allows the user to import a csv file and choose the columns to use."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

from arcos_gui.processing import DataLoader, read_data_header
from qtpy import QtCore, QtWidgets, uic
from qtpy.QtCore import QThread
from qtpy.QtGui import QIcon, QMovie

from ._dialog_widgets import columnpicker

if TYPE_CHECKING:
    import pandas as pd
    from arcos_gui.processing import DataStorage

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
        self.loading_icon = QMovie(str(ICONS / "Dual Ring-1s-200px.gif"))
        self.loading_icon.setScaledSize(QtCore.QSize(40, 40))
        # self.loading.setMovie(self.loading_icon)
        self.browse_file.setIcon(browse_file_icon)
        self.open_file_button.setIcon(QIcon(self.loading_icon.currentPixmap()))
        self.loading_icon.stop()

    def _set_loading_icon(self, frame=None):
        self.open_file_button.setIcon(QIcon(self.loading_icon.currentPixmap()))

    def _hide_loading_icon(self):
        self.open_file_button.setIcon(QIcon())

    def start_loading_icon(self):
        """Start loading icon animation."""
        self.loading_icon.start()
        self.loading_icon.frameChanged.connect(self._set_loading_icon)

    def stop_loading_icon(self):
        """Stop loading icon animation."""
        self.loading_icon.stop()
        self._hide_loading_icon()


class InputDataWidget(QtWidgets.QWidget, _input_dataUI):
    """Widget to import a csv file and choose the columns to use."""

    def __init__(
        self, data_storage_instance: DataStorage, std_out: Callable, parent=None
    ):
        self.data_storage_instance = data_storage_instance
        super().__init__(parent)
        self.setup_ui()
        self.std_out = std_out
        self.picker = columnpicker(self)
        self.last_path = None

        # set up file browser
        self.browse_file.clicked.connect(self._browse_files)

        # set up column picker
        self.open_file_button.clicked.connect(self._open_columnpicker)

    def _browse_files(self):
        """Opens a filedialog and saves path as a string in self.filename"""
        if self.last_path is None:
            self.last_path = str(Path.home())
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Load CSV file",
            str(self.last_path),
            "csv(*.csv);; csv.gz(*.csv.gz);;",
        )
        self.last_path = str(Path(filename[0]).parent)
        if filename[0] == "":
            return
        self.file_LineEdit.setText(filename[0])
        self.data_storage_instance.file_name = filename[0]

    def load_sample_data(self, path, columns):
        """Loads sample data from a given path and sets the column names.

        Parameters
        ----------
        path : str
            Path to the sample data file.
        columns : columnames instance
            Instance of the columnames class.
        """
        self.file_LineEdit.setText(path)
        self.data_storage_instance.columns = columns
        self.open_file_button.click()
        self.data_storage_instance.file_name = path

    def _open_columnpicker(self):
        """Opens a columnpicker window."""
        extension = [".csv", ".csv.gz"]
        csv_file = self.file_LineEdit.text()
        if not csv_file.endswith(tuple(extension)):
            self.std_out("File type not supported")
            return
        if not Path(csv_file).exists():
            self.std_out("File does not exist")
            return
        csv_file = self.file_LineEdit.text()
        columns, delimiter_value = read_data_header(csv_file)
        old_picked_columns = (
            self.data_storage_instance.columns.pickablepickable_columns_names
        )
        self.picker = columnpicker(
            parent=self, columnames_instance=self.data_storage_instance.columns
        )

        self.picker.set_column_names(columns)
        self._set_choices_names_from_previous(self.picker, old_picked_columns)
        self.picker.show()
        self._run_data_loading(csv_file, delimiter_value)

    def _set_choices_names_from_previous(self, picker: columnpicker, col_names):
        """Sets the column names from the previous loaded data."""
        for ui_element, column_name in zip(picker.settable_columns, col_names):
            all_items = [ui_element.itemText(i) for i in range(ui_element.count())]
            if column_name in all_items:
                ui_element.setCurrentText(column_name)

    def _run_data_loading(self, filename, delimiter=None):
        self.loading_thread = QThread(self)
        self.loading_worker = DataLoader(
            filename, delimiter, wait_for_columnpicker=True
        )
        self.picker.rejected.connect(self._abort_loading_worker)
        self.picker.accepted.connect(self._set_loading_worker_columns)

        self.start_loading_icon()
        self.loading_worker.moveToThread(self.loading_thread)
        # Connect signals and slots
        # this signal ensures that if a user closes the columnpicker window with X
        # the loaded data is not updated in the data storage object and layers are not deleted
        # aswell as the columnnames are not updated
        self.loading_worker.new_data.connect(self._succesfully_loaded)
        self.loading_worker.aborted.connect(self._loading_aborted)

        self.loading_thread.started.connect(self.loading_worker.run)

        self.loading_worker.finished.connect(self.stop_loading_icon)
        self.loading_worker.finished.connect(self.loading_thread.quit)
        self.loading_worker.finished.connect(self.loading_worker.deleteLater)
        self.loading_thread.finished.connect(self.loading_thread.deleteLater)
        self.loading_thread.start()
        # self.loading_worker.loading_finished.connect(lambda: print("loading finished"))
        # self.loading_thread.finished.connect(lambda: print("thread finished"))
        self.open_file_button.setEnabled(False)
        self.open_file_button.setText("")

    def closeEvent(self, event):
        if self.picker.isVisible():
            self.picker.close()
            self.loading_thread.quit()
            self.loading_thread.wait(1000)
        event.accept()

    def _set_loading_worker_columns(self):
        self.loading_worker.op = self.picker.measurement_math.currentText()
        self.loading_worker.meas_1 = self.picker.measurement.currentText()
        self.loading_worker.meas_2 = self.picker.second_measurement.currentText()
        self.loading_worker.wait_for_columnpicker = False

    def _abort_loading_worker(self):
        self.loading_worker.wait_for_columnpicker = False
        self.loading_worker.abort_loading = True

    def _succesfully_loaded(self, dataframe: pd.DataFrame, measuremt_name: str):
        """Updates the data storage with the loaded data."""
        self._set_datastorage_to_default()
        self.data_storage_instance.columns = self.picker.as_columnames_object
        self.data_storage_instance.columns.measurement_column = measuremt_name
        self.data_storage_instance.original_data.value = dataframe

    def _loading_aborted(self, err_code):
        """If the loading of the data is aborted, the data storage is not updated."""
        self.open_file_button.setEnabled(True)
        self.open_file_button.setText("Load Data")
        if err_code == 0:
            return
        if err_code == 1:
            self.std_out("Loading aborted")
            return
        if err_code == 2:
            self.std_out("Loading aborted by error")
            return
        self.std_out(f"Loading aborted by error: {err_code}")
        print(err_code)
        return

    def _set_datastorage_to_default(self):
        self.data_storage_instance.reset_relevant_attributes(trigger_callback=False)


if __name__ == "__main__":
    import sys

    from arcos_gui.processing import DataStorage  # noqa: F811

    app = QtWidgets.QApplication(sys.argv)
    widget = InputDataWidget(DataStorage(), print)
    widget.show()
    sys.exit(app.exec_())
