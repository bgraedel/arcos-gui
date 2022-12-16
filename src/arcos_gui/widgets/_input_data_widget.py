from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from arcos_gui.processing import DataLoader, read_data_header
from arcos_gui.tools import remove_layers_after_columnpicker
from arcos_gui.tools._config import ARCOS_LAYERS
from arcos_gui.widgets import columnpicker
from napari.utils.notifications import show_info
from qtpy import QtCore, QtWidgets, uic
from qtpy.QtCore import QThread
from qtpy.QtGui import QIcon, QMovie

if TYPE_CHECKING:
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
        self._load_csv_data(delimiter_value, self.picker)

    def _set_choices_names_from_previous(self, picker: columnpicker, col_names):
        """Sets the column names from the previous loaded data."""
        for ui_element, column_name in zip(picker.settable_columns, col_names):
            AllItems = [ui_element.itemText(i) for i in range(ui_element.count())]
            if column_name in AllItems:
                ui_element.setCurrentText(column_name)

    def _load_csv_data(self, delimiter, picker):
        """Loads data from a csv file and stores it in the data storage."""
        # not sure if this is the best way to do it the idea is to load csv files in the background
        # while the user is selecting columns. Maybe re-write some part here.
        csv_file = self.file_LineEdit.text()
        self.run_data_loading(picker, csv_file, delimiter)

    def run_data_loading(self, picker: columnpicker, filename, delimiter=None):
        self.thread = QThread()
        self.worker = DataLoader(
            picker, self.data_storage_instance, filename, delimiter
        )
        self.start_loading_icon()
        self.worker.moveToThread(self.thread)
        # Connect signals and slots
        # this signal ensures that if a user closes the columnpicker window with X
        # the loaded data is not updated in the data storage object and layers are not deleted
        # aswell as the columnnames are not updated
        self.worker.new_data.connect(self._set_datastorage_to_default)
        self.worker.new_data.connect(self._remove_old_layers)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

        # Final resets
        self.open_file_button.setEnabled(False)
        self.thread.finished.connect(lambda: self.open_file_button.setEnabled(True))
        self.thread.finished.connect(self.stop_loading_icon)

        self.thread.finished.connect(lambda: print(self.data_storage_instance.columns))

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
