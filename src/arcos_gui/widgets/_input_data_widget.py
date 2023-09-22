"""This module contains the InputDataWidget class.

This widget allows the user to import a csv file and choose the columns to use."""

from __future__ import annotations

from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Callable

import pandas as pd
from arcos_gui.processing import (
    DataFrameMatcher,
    DataLoader,
    preprocess_data,
    read_data_header,
)
from arcos_gui.widgets._dialog_widgets import columnpicker
from napari import viewer
from napari.layers import Labels, Tracks
from qtpy import QtCore, QtWidgets, uic
from qtpy.QtCore import Signal
from qtpy.QtGui import QIcon, QMovie

if TYPE_CHECKING:
    from arcos_gui.processing import DataStorage, columnnames

# icons
ICONS = Path(__file__).parent.parent / "_icons"


class _input_dataUI(QtWidgets.QWidget):
    filename_changed = Signal(str)
    closing = Signal()
    last_path = None

    UI_FILE = str(Path(__file__).parent.parent / "_ui" / "Input_data.ui")

    from_csv_selector: QtWidgets.QRadioButton
    from_layers_selector: QtWidgets.QRadioButton

    file_LineEdit: QtWidgets.QLineEdit
    load_data_button: QtWidgets.QPushButton
    browse_file: QtWidgets.QPushButton
    loading: QtWidgets.QLabel

    data_layer_selector_label: QtWidgets.QLabel
    data_layer_selector: QtWidgets.QListWidget

    tracks_layer_selector_label: QtWidgets.QLabel
    tracks_layer_selector: QtWidgets.QComboBox

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        uic.loadUi(self.UI_FILE, self)  # load QtDesigner .ui file
        # set text of Line edit
        self.browse_file.clicked.connect(self._browse_files)
        # set up file browser
        self.file_LineEdit.setText(".")
        # set icons
        browse_file_icon = QIcon(str(ICONS / "folder-open-line.svg"))
        self.loading_icon = QMovie(str(ICONS / "Dual Ring-1s-200px.gif"))
        self.loading_icon.setScaledSize(QtCore.QSize(40, 40))
        # self.loading.setMovie(self.loading_icon)
        self.browse_file.setIcon(browse_file_icon)
        self.load_data_button.setIcon(QIcon(self.loading_icon.currentPixmap()))
        self.loading_icon.stop()

        # set up list widget
        self.data_layer_selector.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )

        # Connect radio buttons to slots
        self.from_csv_selector.toggled.connect(self.toggle_csv_selection_widgets)
        self.from_layers_selector.toggled.connect(self.toggle_layer_selection_widgets)

        # Initialize the widgets based on the selected option
        self.toggle_csv_selection_widgets(self.from_csv_selector.isChecked())
        self.toggle_layer_selection_widgets(self.from_layers_selector.isChecked())

    def toggle_csv_selection_widgets(self, toggled):
        # Show or hide CSV-related widgets based on the toggled state
        self.file_LineEdit.setVisible(toggled)
        self.browse_file.setVisible(toggled)

        self.file_LineEdit.setEnabled(toggled)
        self.browse_file.setEnabled(toggled)

    def toggle_layer_selection_widgets(self, toggled):
        # Show or hide Layers-related widgets based on the toggled state
        self.data_layer_selector_label.setVisible(toggled)
        self.data_layer_selector.setVisible(toggled)

        self.data_layer_selector_label.setEnabled(toggled)
        self.data_layer_selector.setEnabled(toggled)

        self.tracks_layer_selector_label.setVisible(toggled)
        self.tracks_layer_selector.setVisible(toggled)

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
        self.filename_changed.emit(filename[0])

    def _set_loading_icon(self, frame=None):
        self.load_data_button.setIcon(QIcon(self.loading_icon.currentPixmap()))

    def _hide_loading_icon(self):
        self.load_data_button.setIcon(QIcon())

    def start_loading_icon(self):
        """Start loading icon animation."""
        self.loading_icon.start()
        self.loading_icon.frameChanged.connect(self._set_loading_icon)

    def stop_loading_icon(self):
        """Stop loading icon animation."""
        self.loading_icon.stop()
        self._hide_loading_icon()

    def closeEvent(self, event):
        self.closing.emit()
        event.accept()


class InputdataController:
    """Widget to import a csv file and choose the columns to use."""

    def __init__(
        self,
        data_storage_instance: DataStorage,
        std_out: Callable,
        viewer: viewer,
        parent=None,
    ):
        self.widget = _input_dataUI(parent)
        self.picker = columnpicker(self.widget)
        self.viewer = viewer

        self.data_storage_instance = data_storage_instance
        self.std_out = std_out

        self._connect_signals()
        self._update_labels_layers_list()
        self._update_tracks_layers_list()

    def _connect_signals(self):
        """Connects signals and slots."""
        self.widget.filename_changed.connect(self._update_filename)
        self.widget.load_data_button.clicked.connect(self._load_data)
        self.widget.closing.connect(self.closeEvent)
        self.viewer.layers.selection.events.changed.connect(self._on_selection)
        self.data_storage_instance.file_name.value_changed.connect(
            self._update_filename_from_datastorage
        )

    def _on_selection(self, event=None):
        num_labels_in_viewer = len(
            [label for label in self.viewer.layers if isinstance(label, Labels)]
        )
        if num_labels_in_viewer != self.widget.data_layer_selector.size():
            self._update_labels_layers_list()
            self._update_tracks_layers_list()

    def _update_filename(self, filename):
        """Updates the filename in the data storage instance."""
        self.data_storage_instance.file_name.value = filename

    def _update_filename_from_datastorage(self):
        """Updates the filename in the widget from the data storage instance."""
        self.data_storage_instance.file_name.toggle_callback_block(True)
        self.widget.file_LineEdit.setText(self.data_storage_instance.file_name.value)
        self.data_storage_instance.file_name.toggle_callback_block(False)

    def load_sample_data(self, path, columns):
        """Loads sample data from a given path and sets the column names.

        Parameters
        ----------
        path : str
            Path to the sample data file.
        columns : columnames instance
            Instance of the columnames class.
        """
        self.widget.from_csv_selector.setChecked(True)
        self.widget.file_LineEdit.setText(path)
        self.data_storage_instance.columns.value = columns
        self.widget.load_data_button.click()
        self.data_storage_instance.file_name.value = path

    def load_from_dataframe(self, dataframe: pd.DataFrame, columns: columnnames | None):
        """Loads data from a dataframe into the plugin.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            Dataframe to load.
        columns : columnnames instance, optional
            Instance of the columnames class. If None the columnpicker will be opened.
        """
        if columns is None:
            self._open_columnpicker_from_dataframe(dataframe)
            return

        self._set_datastorage_to_default()
        self.data_storage_instance.columns.value = columns

        out_meas_name, dataframe_processed = preprocess_data(
            dataframe, self.data_storage_instance.columns.value
        )
        # set new measurmement name and data
        self.data_storage_instance.columns.value.measurement_column = out_meas_name
        self.data_storage_instance.original_data.value = dataframe_processed

    def _load_data(self):
        if self.widget.from_csv_selector.isChecked():
            self._open_columnpicker_from_csv()
        elif self.widget.from_layers_selector.isChecked():
            self._open_from_layers()
        else:
            raise ValueError("No data source selected")

    def _open_columnpicker_from_csv(self):
        """Opens a columnpicker window."""
        extension = [".csv", ".csv.gz"]
        csv_file = self.widget.file_LineEdit.text()
        if not csv_file.endswith(tuple(extension)):
            self.std_out("File type not supported")
            return
        if not Path(csv_file).exists():
            self.std_out("File does not exist")
            return
        csv_file = self.widget.file_LineEdit.text()
        columns, delimiter_value = read_data_header(csv_file)
        old_picked_columns = (
            self.data_storage_instance.columns.value.pickablepickable_columns_names
        )
        self.picker = columnpicker(
            parent=self.widget,
            columnames_instance=self.data_storage_instance.columns.value,
        )

        self.picker.set_column_names(columns)
        self._set_choices_names_from_previous(self.picker, old_picked_columns)
        self.picker.show()
        self._run_data_loading(csv_file, delimiter_value)

    def _open_columnpicker_from_dataframe(self, df: pd.DataFrame):
        self.picker = columnpicker(
            parent=self.widget,
            columnames_instance=self.data_storage_instance.columns.value,
        )

        self.picker.accepted.connect(partial(self._succesfully_loaded, df))

        self.picker.set_column_names(df.columns)
        old_picked_columns = (
            self.data_storage_instance.columns.value.pickablepickable_columns_names
        )
        self._set_choices_names_from_previous(self.picker, old_picked_columns)
        self.picker.show()

    def _open_columnpicker_from_layers(self, df: pd.DataFrame):
        self.picker = columnpicker(
            parent=self.widget,
            columnames_instance=self.data_storage_instance.columns.value,
        )

        self.picker.accepted.connect(partial(self._succesfully_loaded_from_layer, df))
        self.picker.set_column_names(df.columns)

        if self.widget.tracks_layer_selector.currentText() != "None":
            self.picker.track_id.addItem(
                "From napari tracks layer", "From napari tracks layer"
            )
            self.picker.track_id.setCurrentText("From napari tracks layer")

        old_picked_columns = (
            self.data_storage_instance.columns.value.pickablepickable_columns_names
        )
        self._set_choices_names_from_previous(self.picker, old_picked_columns)
        self.picker.show()

    def _open_from_layers(self):
        df = self._convert_selected_layer_properties_to_dataframe()
        if df is None:
            return
        self._open_columnpicker_from_layers(df)

    def _update_labels_layers_list(self):
        selected_labels = self._get_selected_labels_layers()
        self._available_labels = []
        self.widget.data_layer_selector.clear()
        for layer in self.viewer.layers:
            if isinstance(layer, (Labels)):
                item = QtWidgets.QListWidgetItem(layer.name)
                self._available_labels.append(layer)
                self.widget.data_layer_selector.addItem(item)
                if layer in selected_labels:
                    item.setSelected(True)

    def _update_tracks_layers_list(self):
        selected_tracks = self._get_selected_tracks_layers()
        self._available_tracks = ["None"]
        self.widget.tracks_layer_selector.clear()
        self.widget.tracks_layer_selector.addItem("None", None)
        for layer in self.viewer.layers:
            if isinstance(layer, (Tracks)):
                self._available_tracks.append(layer)
                self.widget.tracks_layer_selector.addItem(layer.name)
                if layer in selected_tracks:
                    self.widget.tracks_layer_selector.setCurrentText(layer.name)

    def _get_selected_labels_layers(self):
        selected_labels = []
        for i in range(self.widget.data_layer_selector.count()):
            item = self.widget.data_layer_selector.item(i)
            if item.isSelected():
                selected_labels.append(self._available_labels[i])
        return selected_labels

    def _get_selected_tracks_layers(self):
        selected_tracks = []
        for i in range(self.widget.tracks_layer_selector.count()):
            if self.widget.tracks_layer_selector.itemText(i) != "None":
                selected_tracks.append(self._available_tracks[i])
        return selected_tracks

    def _convert_selected_layer_properties_to_dataframe(self):
        selected_layer = self._get_selected_labels_layers()
        if len(selected_layer) == 0:
            self.std_out("No labels layer selected, select at least one labels layer")
            return
        if not any(isinstance(layer, Labels) for layer in selected_layer):
            self.std_out("No labels layer selected, select at least one labels layer")
            return
        if len(selected_layer) == 1 and selected_layer[0].properties:
            return pd.DataFrame(selected_layer[0].properties)

        merged_df = None
        for idx, label in enumerate(selected_layer):
            properties = label.properties
            if properties:  # Check if properties dictionary is not empty
                df = pd.DataFrame(properties)
                if not all(lf in df.columns for lf in ["label", "frame"]):
                    self.std_out(
                        f"'label' and/ or 'frame' property missing for labels layer {label.name}"
                    )
                    return

                # Rename coordinate columns with appended label name
                label_name = label.name
                df.rename(
                    columns=lambda col: f"{col}_{label_name}"
                    if col not in ["label", "frame"]
                    else col,
                    inplace=True,
                )

                # Merge the data frames on label ID
                if merged_df is None:
                    merged_df = df
                else:
                    merged_df = pd.merge(merged_df, df, on=["label", "frame"])

        if merged_df is None:
            self.std_out("No properties found")
            return

        return merged_df

    def _convert_selected_tracks_layer_data_to_dataframe(self):
        selected_layer = self._get_selected_tracks_layers()
        if selected_layer[0].data.shape[1] == 4:
            df = pd.DataFrame(
                selected_layer[0].data,
                columns=[
                    self.data_storage_instance.columns.value.object_id,
                    self.data_storage_instance.columns.value.frame_column,
                    self.data_storage_instance.columns.value.y_column,
                    self.data_storage_instance.columns.value.x_column,
                ],
            )
        elif selected_layer[0].data.shape[1] == 5:
            df = pd.DataFrame(
                selected_layer[0].data,
                columns=[
                    self.data_storage_instance.columns.value.object_id,
                    self.data_storage_instance.columns.value.frame_column,
                    str(self.data_storage_instance.columns.value.z_column),
                    self.data_storage_instance.columns.value.y_column,
                    self.data_storage_instance.columns.value.x_column,
                ],
            )
            if self.data_storage_instance.columns.value.z_column is None:
                df = df.drop(
                    columns=[str(self.data_storage_instance.columns.value.z_column)]
                )
        else:
            raise ValueError("Track layer has wrong shape")

        return df

    def _set_choices_names_from_previous(self, picker: columnpicker, col_names):
        """Sets the column names from the previous loaded data."""
        settable_columns = picker.settable_columns
        for ui_element, column_name in zip(settable_columns, col_names):
            all_items = [ui_element.itemText(i) for i in range(ui_element.count())]
            if column_name in all_items:
                ui_element.setCurrentText(column_name)

    def _run_data_loading(self, filename, delimiter=None):
        # self.loading_thread = QThread(self.widget)
        self.loading_worker = DataLoader(
            filename,
            delimiter,
            wait_for_columnpicker=True,
        )
        self.picker.rejected.connect(self._abort_loading_worker)
        self.picker.accepted.connect(self._set_loading_worker_columnpicker)

        self.widget.start_loading_icon()
        self.loading_worker.new_data.connect(self._succesfully_loaded)
        self.loading_worker.aborted.connect(self._loading_aborted)
        self.loading_worker.finished.connect(self.widget.stop_loading_icon)
        self.widget.load_data_button.setEnabled(False)
        self.widget.load_data_button.setText("")
        self.loading_worker.start()

    def closeEvent(self):
        if self.picker.isVisible():
            self.picker.close()
        try:
            self.loading_thread.quit()
            self.loading_thread.deleteLater()
            self.loading_thread.wait(1000)
        except (AttributeError, RuntimeError):
            pass
        try:
            self.matching_thread.quit()
            self.matching_thread.deleteLater()
            self.matching_thread.wait(1000)
        except (AttributeError, RuntimeError):
            pass

    def _set_loading_worker_columnpicker(self):
        self.loading_worker.wait_for_columnpicker = False

    def _abort_loading_worker(self):
        self.loading_worker.wait_for_columnpicker = False
        self.loading_worker.abort_loading = True

    def _succesfully_loaded(self, dataframe: pd.DataFrame):
        """Updates the data storage with the loaded data."""
        self._set_datastorage_to_default()
        self.data_storage_instance.columns.value = self.picker.as_columnames_object

        out_meas_name, dataframe_processed = preprocess_data(
            dataframe, self.data_storage_instance.columns.value
        )

        # set new measurmement name and data
        self.data_storage_instance.columns.value.measurement_column = out_meas_name
        self.data_storage_instance.original_data.value = dataframe_processed

    def _run_dataframe_matching(self, df1, df2, frame_col, coord_cols1):
        """Start the DataFrameMatcher in a separate thread."""
        self.matching_worker = DataFrameMatcher(
            df1, df2, frame_col=frame_col, coord_cols1=coord_cols1
        )

        # Connect signals and slots
        self.matching_worker.matched.connect(self._on_matching_success)
        self.matching_worker.aborted.connect(self._matching_aborted)

        self.widget.start_loading_icon()
        self.matching_worker.finished.connect(self.widget.stop_loading_icon)
        self.matching_worker.start()

    def _on_matching_success(self, matched_df):
        """Handle the successful completion of the DataFrameMatcher operation."""
        # Continue the processing from where you left off in _succesfully_loaded_from_layer
        out_meas_name, dataframe_processed = preprocess_data(
            matched_df, self.data_storage_instance.columns.value
        )

        # set new measurement name and data
        self.data_storage_instance.columns.value.measurement_column = out_meas_name
        self.data_storage_instance.original_data.value = dataframe_processed

    def _matching_aborted(self, error):
        """Handle the DataFrameMatcher operation abort."""
        self.std_out(f"Loading aborted by error: {error}")
        print(error)

    def _succesfully_loaded_from_layer(self, dataframe: pd.DataFrame):
        """Updates the data storage with the loaded data."""
        self._set_datastorage_to_default()
        self.data_storage_instance.columns.value = self.picker.as_columnames_object
        if (
            self.data_storage_instance.columns.value.object_id
            == "From napari tracks layer"
        ):
            self.data_storage_instance.columns.value.object_id = "track_id"

            tracks_df = self._convert_selected_tracks_layer_data_to_dataframe()
            if self.data_storage_instance.columns.value.z_column:
                coords = [
                    self.data_storage_instance.columns.value.z_column,
                    self.data_storage_instance.columns.value.y_column,
                    self.data_storage_instance.columns.value.x_column,
                ]
            else:
                coords = [
                    self.data_storage_instance.columns.value.y_column,
                    self.data_storage_instance.columns.value.x_column,
                ]

            # Start the DataFrame matching in a separate thread
            self._run_dataframe_matching(
                dataframe,
                tracks_df,
                self.data_storage_instance.columns.value.frame_column,
                coords,
            )

        else:
            self._on_matching_success(dataframe)

    def _loading_aborted(self, err_code):
        """If the loading of the data is aborted, the data storage is not updated."""
        self.widget.load_data_button.setEnabled(True)
        self.widget.load_data_button.setText("Load Data")
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

    def _set_datastorage_to_default(self):
        self.data_storage_instance.reset_relevant_attributes(trigger_callback=False)
