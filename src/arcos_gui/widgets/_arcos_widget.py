"""Widget to set arcos parameters and run arcos algorithm."""

from __future__ import annotations

import traceback
from dataclasses import fields
from pathlib import Path
from typing import TYPE_CHECKING

from arcos_gui.processing import arcos_worker
from arcos_gui.tools import OutputOrderValidator
from napari.utils import progress
from napari.utils.notifications import show_info
from qtpy import QtWidgets, uic
from qtpy.QtCore import QSize, QTimer, Signal
from qtpy.QtGui import QIcon, QMovie, QValidator

if TYPE_CHECKING:
    from arcos_gui.processing import DataStorage

# icons
ICONS = Path(__file__).parent.parent / "_icons"


class _arcosWidget(QtWidgets.QWidget):
    closing = Signal()
    UI_FILE = str(Path(__file__).parent.parent / "_ui" / "ARCOS_widget.ui")

    # The UI_FILE above contains these objects:

    clip_low_label: QtWidgets.QLabel
    clip_high_label: QtWidgets.QLabel
    intervale_type_label: QtWidgets.QLabel
    bias_method_label: QtWidgets.QLabel
    smooth_k_label: QtWidgets.QLabel
    bias_k_label: QtWidgets.QLabel
    polyDeg_label: QtWidgets.QLabel
    bin_peak_threshold_label: QtWidgets.QLabel
    bin_threshold_label: QtWidgets.QLabel
    neighbourhood_label: QtWidgets.QLabel
    min_clustersize_label: QtWidgets.QLabel
    nprev_spinbox: QtWidgets.QSpinBox
    nprev_label: QtWidgets.QLabel
    min_dur_label: QtWidgets.QLabel
    tot_size_label: QtWidgets.QLabel

    interpolate_meas: QtWidgets.QCheckBox
    clip_meas: QtWidgets.QCheckBox
    clip_low: QtWidgets.QDoubleSpinBox
    clip_high: QtWidgets.QDoubleSpinBox

    bin_advanced_options: QtWidgets.QCheckBox
    bias_method: QtWidgets.QComboBox
    smooth_k: QtWidgets.QSpinBox
    bias_k: QtWidgets.QSpinBox
    polyDeg: QtWidgets.QSpinBox
    bin_peak_threshold: QtWidgets.QDoubleSpinBox
    bin_threshold: QtWidgets.QDoubleSpinBox

    detect_advance_options: QtWidgets.QCheckBox
    eps_estimation_label: QtWidgets.QLabel
    eps_estimation_combobox: QtWidgets.QComboBox
    neighbourhood_size: QtWidgets.QDoubleSpinBox
    Cluster_linking_dist_checkbox: QtWidgets.QCheckBox
    epsPrev_spinbox: QtWidgets.QDoubleSpinBox
    min_clustersize: QtWidgets.QSpinBox
    min_dur: QtWidgets.QSpinBox
    total_event_size: QtWidgets.QSpinBox
    update_arcos: QtWidgets.QPushButton
    run_binarization_only: QtWidgets.QPushButton
    arcos_group: QtWidgets.QGroupBox
    clip_frame: QtWidgets.QFrame
    add_all_cells_checkbox: QtWidgets.QCheckBox
    add_bin_cells_checkbox: QtWidgets.QCheckBox
    add_convex_hull_checkbox: QtWidgets.QCheckBox
    output_order: QtWidgets.QLineEdit
    output_order_label: QtWidgets.QLabel
    loading_label: QtWidgets.QLabel

    cancel_button: QtWidgets.QPushButton

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup UI. Loads it from ui file."""
        uic.loadUi(self.UI_FILE, self)  # load QtDesigner .ui file
        self.loading_icon = QMovie(str(ICONS / "Dual Ring-1s-200px.gif"))
        self.loading_icon.setScaledSize(QSize(40, 40))
        self.loading_label.setMovie(self.loading_icon)
        self.loading_icon.start()
        # self.loading_icon.stop()
        self.loading_label.hide()
        self.cancel_button.setStyleSheet("background-color : #7C0A02; color : white")
        self.cancel_button.hide()
        self._set_advanced_state_dict()
        self._setup_timer()
        self._connect_ui_callbacks()
        self._init_callbacks_visible_arcosparameters()
        self._set_default_visible()
        self.updateValidator(None)

    def _set_advanced_state_dict(self):
        self.set_default_bin_state_dict()
        self._set_detect_advanced_state_dict()

    def set_default_bin_state_dict(self):
        self.bias_met_advanced_state = {
            "bias_method": self.bias_method.currentText(),
            "smoothK": self.smooth_k.value(),
        }

    def _set_detect_advanced_state_dict(self):
        self.detect_advanced_state = {
            "eps": self.neighbourhood_size.value(),
            "auto_eps": self.eps_estimation_combobox.currentText(),
            "cluter_linking_dist_check": self.Cluster_linking_dist_checkbox.isChecked(),
            "epsPrev": self.epsPrev_spinbox.value(),
            "nPrev": self.nprev_spinbox.value(),
        }

    def _connect_ui_callbacks(self):
        self.output_order.textChanged.connect(self._onTextChanged)
        self.bin_advanced_options.stateChanged.connect(
            self._bin_advanced_options_toggle
        )
        self.detect_advance_options.stateChanged.connect(
            self._detect_advanced_options_toggle
        )
        self.eps_estimation_combobox.currentIndexChanged.connect(
            self._eps_estimation_toggle
        )
        self.Cluster_linking_dist_checkbox.stateChanged.connect(self._epsPrev_toggle)

    def _onTextChanged(self, text):
        validator = self.output_order.validator()
        if validator:
            state, _, _ = validator.validate(text.lower(), len(text))
            if state == QValidator.Acceptable:
                self.update_arcos.setEnabled(True)
                self.run_binarization_only.setEnabled(True)
                self.output_order.setStyleSheet("")
            elif state == QValidator.Intermediate or state == QValidator.Invalid:
                color = "#f6989d"  # light red
                self.update_arcos.setEnabled(False)
                self.run_binarization_only.setEnabled(False)
                self.output_order.setStyleSheet(
                    "QLineEdit { background-color: %s; color: black }" % color
                )

    def updateValidator(self, vColsCore: list[str] | None = None):
        if vColsCore is None:
            vColsCore = ["t", "x", "y"]
        validator = OutputOrderValidator(vColsCore, self.output_order)
        self.output_order.setValidator(validator)
        if len(vColsCore) == 3:
            self.output_order.setText("tyx")
        elif len(vColsCore) == 4:
            self.output_order.setText("tzyx")

    def _set_default_visible(self):
        """Method that sets the default visible widgets in the main window."""
        self.clip_meas.setChecked(False)
        self._toggle_bias_method_parameter_visibility()
        self._bin_advanced_options_toggle()
        self._detect_advanced_options_toggle()
        self._epsPrev_toggle()
        self._eps_estimation_toggle()

    def _bin_advanced_options_toggle(self):
        checked = self.bin_advanced_options.isChecked()
        if checked:
            self.bias_method.setCurrentText(self.bias_met_advanced_state["bias_method"])
            self.smooth_k.setValue(self.bias_met_advanced_state["smoothK"])
        else:
            self.bias_met_advanced_state["bias_method"] = self.bias_method.currentText()
            self.bias_met_advanced_state["smoothK"] = self.smooth_k.value()
            self.smooth_k.setValue(3)
            self.bias_method.setCurrentText("none")
            self.bias_method.currentIndexChanged.emit(0)

        self._toggle_bias_method_parameter_visibility()

    def _detect_advanced_options_toggle(self):
        checked = self.detect_advance_options.isChecked()
        self.eps_estimation_label.setVisible(checked)
        self.eps_estimation_combobox.setVisible(checked)
        self.neighbourhood_label.setVisible(checked)
        self.neighbourhood_size.setVisible(checked)
        self.Cluster_linking_dist_checkbox.setVisible(checked)
        self.epsPrev_spinbox.setVisible(checked)
        self.nprev_label.setVisible(checked)
        self.nprev_spinbox.setVisible(checked)
        if checked:
            self.eps_estimation_combobox.setCurrentText(
                self.detect_advanced_state["auto_eps"]
            )
            self.neighbourhood_size.setValue(self.detect_advanced_state["eps"])
            self.Cluster_linking_dist_checkbox.setChecked(
                self.detect_advanced_state["cluter_linking_dist_check"]
            )
            self.epsPrev_spinbox.setValue(self.detect_advanced_state["epsPrev"])
            self.nprev_spinbox.setValue(self.detect_advanced_state["nPrev"])
        else:
            self.detect_advanced_state = {
                "eps": self.neighbourhood_size.value(),
                "auto_eps": self.eps_estimation_combobox.currentText(),
                "cluter_linking_dist_check": self.Cluster_linking_dist_checkbox.isChecked(),
                "epsPrev": self.epsPrev_spinbox.value(),
                "nPrev": self.nprev_spinbox.value(),
            }
            self.eps_estimation_combobox.setCurrentText("mean")
            self.Cluster_linking_dist_checkbox.setChecked(False)
            self.nprev_spinbox.setValue(1)

    def _eps_estimation_toggle(self):
        eps_method = self.eps_estimation_combobox.currentText()
        if eps_method == "manual":
            self.neighbourhood_size.setEnabled(True)
            self.neighbourhood_size.setButtonSymbols(
                QtWidgets.QAbstractSpinBox.UpDownArrows
            )
        else:
            self.neighbourhood_size.setEnabled(False)
            self.neighbourhood_size.setButtonSymbols(
                QtWidgets.QAbstractSpinBox.NoButtons
            )

    def _epsPrev_toggle(self):
        checked = self.Cluster_linking_dist_checkbox.isChecked()
        self.epsPrev_spinbox.setEnabled(checked)
        if checked:
            self.neighbourhood_size.valueChanged.disconnect(
                self._update_epsPrev_from_eps
            )
            self.epsPrev_spinbox.setButtonSymbols(
                QtWidgets.QAbstractSpinBox.UpDownArrows
            )
        else:
            self._update_epsPrev_from_eps()
            self.neighbourhood_size.valueChanged.connect(self._update_epsPrev_from_eps)
            self.epsPrev_spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)

    def _update_epsPrev_from_eps(self):
        self.epsPrev_spinbox.setValue(self.neighbourhood_size.value())

    def _toggle_bias_method_parameter_visibility(self):
        """
        based on the seleciton of bias method:
        shows or hides the appropriate options in the main window.
        """
        advanced_checked = self.bin_advanced_options.isChecked()
        self.smooth_k.setVisible(advanced_checked)
        self.smooth_k_label.setVisible(advanced_checked)
        self.bias_method.setVisible(advanced_checked)
        self.bias_method_label.setVisible(advanced_checked)

        if self.bias_method.currentText() == "runmed":
            self.polyDeg.setVisible(False)
            self.polyDeg_label.setVisible(False)
            self.bias_k.setVisible(True)
            self.bias_k_label.setVisible(True)
            self.bin_peak_threshold.setVisible(True)
            self.bin_peak_threshold_label.setVisible(True)
            self.bin_threshold.setVisible(True)
            self.bin_threshold_label.setVisible(True)

        if self.bias_method.currentText() == "lm":
            self.polyDeg.setVisible(True)
            self.polyDeg_label.setVisible(True)
            self.bias_k.setVisible(False)
            self.bias_k_label.setVisible(False)
            self.bin_peak_threshold.setVisible(True)
            self.bin_peak_threshold_label.setVisible(True)
            self.bin_threshold.setVisible(True)
            self.bin_threshold_label.setVisible(True)

        if self.bias_method.currentText() == "none":
            self.polyDeg.setVisible(False)
            self.polyDeg_label.setVisible(False)
            self.bias_k.setVisible(False)
            self.bias_k_label.setVisible(False)
            self.bin_peak_threshold.setVisible(False)
            self.bin_peak_threshold_label.setVisible(False)
            self.bin_threshold.setVisible(True)
            self.bin_threshold_label.setVisible(True)

    def toggle_bias_method_enable(self, enabled: bool):
        """Toggle the enable of the bias method groupbox."""
        self.bias_method.setEnabled(enabled)
        self.bias_method_label.setEnabled(enabled)
        self.smooth_k.setEnabled(enabled)
        self.smooth_k_label.setEnabled(enabled)
        self.polyDeg.setEnabled(enabled)
        self.polyDeg_label.setEnabled(enabled)
        self.bias_k.setEnabled(enabled)
        self.bias_k_label.setEnabled(enabled)
        self.bin_peak_threshold.setEnabled(enabled)
        self.bin_peak_threshold_label.setEnabled(enabled)

    def toggle_tracklenght_filter_enable(self, enabled: bool):
        self.total_event_size.setEnabled(enabled)
        self.tot_size_label.setEnabled(enabled)

    def _toggle_clip_visible(self):
        """Toggle the visibility of the clipping options."""
        if self.clip_meas.isChecked():
            self.clip_high.setVisible(True)
            self.clip_low.setVisible(True)
            self.clip_high_label.setVisible(True)
            self.clip_low_label.setVisible(True)
        else:
            self.clip_high.setVisible(False)
            self.clip_low.setVisible(False)
            self.clip_high_label.setVisible(False)
            self.clip_low_label.setVisible(False)

    def _init_callbacks_visible_arcosparameters(self):
        """Initialize the callbacks for visible parameters in bias method groupbox."""
        self.bias_method.currentIndexChanged.connect(
            self._toggle_bias_method_parameter_visibility
        )
        self.clip_meas.stateChanged.connect(self._toggle_clip_visible)

    def _set_loading_icon(self, frame=None):
        self.update_arcos.setIcon(QIcon(self.loading_icon.currentPixmap()))

    def _hide_loading_icon(self):
        self.loading_label.hide()
        self.loading_icon.stop()

    def _setup_timer(self):
        self.timer_loading_icon_show = QTimer(parent=self)
        self.timer_loading_icon_show.setSingleShot(True)

    def start_loading(self):
        """Start loading icon animation."""
        self.update_arcos.setEnabled(False)
        self.run_binarization_only.setEnabled(False)
        self.cancel_button.show()
        self.cancel_button.setEnabled(True)
        self.timer_loading_icon_show.timeout.connect(self._show_loading_icon)
        self.timer_loading_icon_show.start(100)

    def _show_loading_icon(self):
        self.loading_label.show()
        self.loading_icon.start()

    def stop_loading(self):
        """Stop loading icon animation."""
        if self.timer_loading_icon_show.isActive():
            self.timer_loading_icon_show.stop()
        self._hide_loading_icon()
        self.cancel_button.hide()
        self.cancel_button.setEnabled(False)
        self.update_arcos.setEnabled(True)
        self.run_binarization_only.setEnabled(True)

    def closeEvent(self, event):
        self.closing.emit()
        event.accept()


class ArcosController:
    """Widget to set arcos parameters and run arcos algorithm."""

    def __init__(self, data_storage_instance: DataStorage, parent=None):
        self.widget = _arcosWidget(parent)

        self._what_to_run: set = set()
        self._data_storage_instance = data_storage_instance
        self.abort_timer = QTimer(parent)
        self.abort_timer.timeout.connect(self.abort_timer_timeout)

        self._init_callbacks_for_whattorun()
        self._update_what_to_run_all()
        self._update_arcos_parameters_object()
        self._connect_callbacks()

    def _connect_callbacks(self):
        self.widget.closing.connect(self.closeEvent)
        self.widget.update_arcos.clicked.connect(self._run_arcos)
        self.widget.run_binarization_only.clicked.connect(self._run_binarization_only)

        self.widget.cancel_button.clicked.connect(self.abort_worker)
        self._data_storage_instance.original_data.value_changed.connect(
            self._update_bias_method_availability
        )
        self._data_storage_instance.original_data.value_changed.connect(
            self._update_filter_availability
        )
        self._data_storage_instance.original_data.value_changed.connect(
            lambda: self.widget.updateValidator(
                self._data_storage_instance.columns.value.vcolscore
            )
        )

        self._connect_arcos_parameter_callbacks()

    def _update_bias_method_availability(self):
        """Change availability of bias methods depending on input data."""
        if self._data_storage_instance.columns.value.object_id is None:
            self.widget.toggle_bias_method_enable(False)
            self.widget.bias_method.setCurrentIndex(0)
        else:
            self.widget.toggle_bias_method_enable(True)

    def _update_filter_availability(self):
        """Change availability of filter methods depending on input data."""
        if self._data_storage_instance.columns.value.object_id is None:
            self.widget.toggle_tracklenght_filter_enable(False)
        else:
            self.widget.toggle_tracklenght_filter_enable(True)

    def _update_datastorage_with_bin_data(self, bin_data):
        self._data_storage_instance.columns.value.measurement_bin = bin_data[0]
        self._data_storage_instance.columns.value.measurement_resc = bin_data[1]
        self._data_storage_instance.arcos_binarization.value = bin_data[2]

    def _update_datastorage_with_arcos(self, arcos_data):
        self._data_storage_instance.arcos_stats.value = arcos_data[1]
        self._data_storage_instance.arcos_output.value = arcos_data[0]

    def _setup_debounce_timer(self):
        self.debounce_time = (
            10  # Adjust this value to set the debounce time in milliseconds
        )
        self.missed_updates = 0
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._perform_update)

    def _perform_update(self):
        # Get the current value of the progress bar
        current_value = self.pbar.n

        # Update the progress bar with the missed updates
        self.pbar.update(self.missed_updates)

        # Correct the number of missed updates based on the actual change in the progress bar value
        self.missed_updates = (current_value + self.missed_updates) - self.pbar.n

        # Reset the missed updates counter if it's zero
        if self.pbar.n >= self.pbar.total:
            self.missed_updates = 0

    def createWorkerThread(self, what_to_run: set):
        """Create a worker thread to run arcos algorithm."""
        # try to get the old ARCOS object from the worker,
        # this allows to continue the calculation if the worker is reset
        try:
            self.worker: arcos_worker  # for mypy
            arcos_object = self.worker.arcos_object
            arcos_raw_output = self.worker.arcos_raw_output
        except AttributeError:
            arcos_object = None
            arcos_raw_output = None

        self._setup_debounce_timer()

        self.pbar = progress(total=0, desc="ARCOS calculation")

        self.worker = arcos_worker(
            what_to_run,
            show_info,
            self._data_storage_instance.arcos_parameters.value,
            columns=self._data_storage_instance.columns.value,
            filtered_data=self._data_storage_instance.filtered_data.value,
            arcos_object=arcos_object,
            arcos_raw_output=arcos_raw_output,
        )
        self.worker.arcos_progress_update.connect(self._update_progressbar)

        self.worker.binarization_finished.connect(
            self._update_datastorage_with_bin_data
        )
        self.worker.new_eps.connect(self._update_eps)
        self.worker.new_arcos_output.connect(self._update_datastorage_with_arcos)
        self.worker.finished.connect(self.widget.stop_loading)
        self.worker.started.connect(self.widget.start_loading)
        self.worker.finished.connect(self.abort_timer_stop)
        self.worker.aborted.connect(self.abort_timer_stop)
        self.worker.aborted.connect(self._show_aborted_message)

        self.worker.start()
        return self.worker

    def _update_progressbar(self, update_type, value):
        if update_type == "total":
            self.pbar.reset(value)
        elif update_type == "reset":
            self.pbar.reset(value)
        elif update_type == "update":
            self.missed_updates += value
            if not self.update_timer.isActive():
                self.update_timer.start(self.debounce_time)
        else:
            raise ValueError(f"Unknown update_type: {update_type}")

    def _run_arcos(self):
        self.createWorkerThread(self._what_to_run)

    def _run_binarization_only(self):
        worker = self.createWorkerThread({"binarization"})
        worker.finished.connect(self._if_data_update_what_to_run)

    def _if_data_update_what_to_run(self):
        if not self._data_storage_instance.arcos_binarization.value.empty:
            self._update_what_to_run_tracking()

    def _show_aborted_message(self, err):
        show_info(f"ARCOS calculation aborted due to: {err}")
        traceback.print_exception(None, err, err.__traceback__)

    def _update_eps(self, eps):
        self._data_storage_instance.arcos_parameters.value.neighbourhood_size.value = (
            eps
        )

    def update_worker_with_data(self):
        self.worker.what_to_run = self._what_to_run
        self.worker.filtered_data = self._data_storage_instance.filtered_data.value
        self.worker.columns = self._data_storage_instance.columns.value
        self.worker.arcos_parameters.set_all_parameters(
            self._data_storage_instance.arcos_parameters.value
        )

    def abort_worker(self):
        self.worker.finished.connect(self.abort_timer_stop)
        self.worker.quit()
        self.widget.cancel_button.setEnabled(False)
        self.widget.cancel_button.setText("Aborting")
        self.abort_timer_start()

    def abort_timer_start(self):
        self.abort_timer.start(1000)

    def abort_timer_timeout(self):
        self.update_abort_button()

    def abort_timer_stop(self):
        self.abort_timer.stop()
        self.pbar.close()
        self.widget.cancel_button.setText("Abort")

    def update_abort_button(self):
        self.dots = self.widget.cancel_button.text().count(".")
        if self.dots < 3:
            self.widget.cancel_button.setText(self.widget.cancel_button.text() + ".")
        else:
            self.widget.cancel_button.setText("Aborting")

    def _stop_worker(self):
        try:
            self.worker.quit()
        except (AttributeError, RuntimeError):
            pass

    def closeEvent(self):
        self._stop_worker()

    def _init_callbacks_for_whattorun(self):
        """Connect callbacks for updating 'what to run'.

        This is used to run only the appropriate parts of the
        run_arcos method depending on the parameters changed.
        """
        # for every changable field connect the appropriate what_to_run function
        for i in [self.widget.bias_method]:
            i.currentIndexChanged.connect(self._update_what_to_run_all)
        for i in [
            self.widget.clip_low,
            self.widget.clip_high,
            self.widget.smooth_k,
            self.widget.bias_k,
            self.widget.polyDeg,
            self.widget.bin_threshold,
            self.widget.bin_peak_threshold,
        ]:
            i.valueChanged.connect(self._update_what_to_run_all)
        for i in [self.widget.interpolate_meas, self.widget.clip_meas]:
            i.stateChanged.connect(self._update_what_to_run_all)
        for i in [
            self.widget.neighbourhood_size,
            self.widget.min_clustersize,
            self.widget.nprev_spinbox,
        ]:
            i.valueChanged.connect(self._update_what_to_run_tracking)
        for i in [self.widget.epsPrev_spinbox]:
            i.valueChanged.connect(self._update_what_to_run_tracking)
        for i in [self.widget.eps_estimation_combobox]:
            i.currentIndexChanged.connect(self._update_what_to_run_tracking)
        for i in [self.widget.min_dur, self.widget.total_event_size]:
            i.valueChanged.connect(self._update_what_to_run_filtering)
        for i in [
            self.widget.add_convex_hull_checkbox,
            self.widget.add_all_cells_checkbox,
            self.widget.add_bin_cells_checkbox,
        ]:
            i.stateChanged.connect(self._update_what_to_run_filtering)

        self.widget.output_order.textChanged.connect(self._update_what_to_run_filtering)

    def _update_what_to_run_all(self):
        """Adds 'all' to the what_to_run attirbute,
        that is used in the main function to check if what to run
        when certain field have updated values."""
        self._clear_what_to_run()
        self._what_to_run.add("binarization")
        self._what_to_run.add("tracking")
        self._what_to_run.add("filtering")

    def _update_what_to_run_tracking(self):
        """Adds 'from_tracking' to the what_to_run attirbute,
        that is used in the main function to check if what to run
        when certain field have updated values."""
        self._what_to_run.add("tracking")
        self._what_to_run.add("filtering")

    def _update_what_to_run_filtering(self):
        """Adds 'from_filtering' to the what_to_run attirbute,
        that is used in the main function to check if what to run
        when certain field have updated values."""
        self._what_to_run.add("filtering")

    def _clear_what_to_run(self):
        """Clears the what_to_run attribute."""
        self._what_to_run.clear()

    def _update_arcos_parameters_object(self):
        """Update the parameters in the data storage instance"""
        try:
            self._data_storage_instance.toggle_callback_block(True)
            if not self.widget.Cluster_linking_dist_checkbox.isChecked():
                epsPrev = None
            else:
                epsPrev = self.widget.epsPrev_spinbox.value()
            self._data_storage_instance.arcos_parameters.value.interpolate_meas.value = (
                self.widget.interpolate_meas.isChecked()
            )
            self._data_storage_instance.arcos_parameters.value.clip_meas.value = (
                self.widget.clip_meas.isChecked()
            )
            self._data_storage_instance.arcos_parameters.value.clip_low.value = (
                self.widget.clip_low.value()
            )
            self._data_storage_instance.arcos_parameters.value.clip_high.value = (
                self.widget.clip_high.value()
            )
            self._data_storage_instance.arcos_parameters.value.bin_advanded_settings.value = (
                self.widget.bin_advanced_options.isChecked()
            )
            self._data_storage_instance.arcos_parameters.value.smooth_k.value = (
                self.widget.smooth_k.value()
            )
            self._data_storage_instance.arcos_parameters.value.bias_k.value = (
                self.widget.bias_k.value()
            )
            self._data_storage_instance.arcos_parameters.value.bias_method.value = (
                self.widget.bias_method.currentText()
            )
            self._data_storage_instance.arcos_parameters.value.polyDeg.value = (
                self.widget.polyDeg.value()
            )
            self._data_storage_instance.arcos_parameters.value.bin_threshold.value = (
                self.widget.bin_threshold.value()
            )
            self._data_storage_instance.arcos_parameters.value.bin_peak_threshold.value = (
                self.widget.bin_peak_threshold.value()
            )
            self._data_storage_instance.arcos_parameters.value.detect_advanced_options.value = (
                self.widget.detect_advance_options.isChecked()
            )
            self._data_storage_instance.arcos_parameters.value.neighbourhood_size.value = (
                self.widget.neighbourhood_size.value()
            )
            self._data_storage_instance.arcos_parameters.value.min_clustersize.value = (
                self.widget.min_clustersize.value()
            )
            self._data_storage_instance.arcos_parameters.value.nprev.value = (
                self.widget.nprev_spinbox.value()
            )
            self._data_storage_instance.arcos_parameters.value.min_dur.value = (
                self.widget.min_dur.value()
            )
            self._data_storage_instance.arcos_parameters.value.total_event_size.value = (
                self.widget.total_event_size.value()
            )
            self._data_storage_instance.arcos_parameters.value.add_convex_hull.value = (
                self.widget.add_convex_hull_checkbox.isChecked()
            )
            self._data_storage_instance.arcos_parameters.value.add_all_cells.value = (
                self.widget.add_all_cells_checkbox.isChecked()
            )
            self._data_storage_instance.arcos_parameters.value.add_bin_cells.value = (
                self.widget.add_bin_cells_checkbox.isChecked()
            )
            self._data_storage_instance.arcos_parameters.value.epsPrev.value = epsPrev
            self._data_storage_instance.arcos_parameters.value.eps_method.value = (
                self.widget.eps_estimation_combobox.currentText()
            )
            self._data_storage_instance.output_order.value = (
                self.widget.output_order.text()
            )
        finally:
            self._data_storage_instance.toggle_callback_block(False)

    def _update_arcos_parameters_ui(self):
        try:
            self._data_storage_instance.toggle_callback_block(True)
            self.block_qt_signals(True)

            self.widget.interpolate_meas.setChecked(
                self._data_storage_instance.arcos_parameters.value.interpolate_meas.value
            )
            self.widget.clip_meas.setChecked(
                self._data_storage_instance.arcos_parameters.value.clip_meas.value
            )
            self.widget.clip_low.setValue(
                self._data_storage_instance.arcos_parameters.value.clip_low.value
            )
            self.widget.clip_high.setValue(
                self._data_storage_instance.arcos_parameters.value.clip_high.value
            )
            self.widget.smooth_k.setValue(
                self._data_storage_instance.arcos_parameters.value.smooth_k.value
            )
            self.widget.bias_k.setValue(
                self._data_storage_instance.arcos_parameters.value.bias_k.value
            )
            self.widget.bias_method.setCurrentText(
                self._data_storage_instance.arcos_parameters.value.bias_method.value
            )
            self.widget.polyDeg.setValue(
                self._data_storage_instance.arcos_parameters.value.polyDeg.value
            )
            self.widget.bin_threshold.setValue(
                self._data_storage_instance.arcos_parameters.value.bin_threshold.value
            )
            self.widget.bin_peak_threshold.setValue(
                self._data_storage_instance.arcos_parameters.value.bin_peak_threshold.value
            )
            self.widget.neighbourhood_size.setValue(
                self._data_storage_instance.arcos_parameters.value.neighbourhood_size.value
            )
            self.widget.min_clustersize.setValue(
                self._data_storage_instance.arcos_parameters.value.min_clustersize.value
            )
            self.widget.nprev_spinbox.setValue(
                self._data_storage_instance.arcos_parameters.value.nprev.value
            )
            self.widget.min_dur.setValue(
                self._data_storage_instance.arcos_parameters.value.min_dur.value
            )
            self.widget.total_event_size.setValue(
                self._data_storage_instance.arcos_parameters.value.total_event_size.value
            )
            self.widget.add_convex_hull_checkbox.setChecked(
                self._data_storage_instance.arcos_parameters.value.add_convex_hull.value
            )
            self.widget.add_all_cells_checkbox.setChecked(
                self._data_storage_instance.arcos_parameters.value.add_all_cells.value
            )
            self.widget.add_bin_cells_checkbox.setChecked(
                self._data_storage_instance.arcos_parameters.value.add_bin_cells.value
            )
            self.widget.eps_estimation_combobox.setCurrentText(
                self._data_storage_instance.arcos_parameters.value.eps_method.value
            )
            if (
                self._data_storage_instance.arcos_parameters.value.epsPrev.value
                is not None
            ):
                self.widget.Cluster_linking_dist_checkbox.setChecked(True)
                self.widget.epsPrev_spinbox.setValue(
                    self._data_storage_instance.arcos_parameters.value.epsPrev.value
                )
            else:
                self.widget.Cluster_linking_dist_checkbox.setChecked(False)
                self.widget.epsPrev_spinbox.setValue(
                    self._data_storage_instance.arcos_parameters.value.neighbourhood_size.value
                )

            self.widget.output_order.setText(
                self._data_storage_instance.output_order.value
            )
            self.widget.bin_advanced_options.setChecked(
                self._data_storage_instance.arcos_parameters.value.bin_advanded_settings.value
            )
            self.widget.detect_advance_options.setChecked(
                self._data_storage_instance.arcos_parameters.value.detect_advanced_options.value
            )
            self.widget._set_advanced_state_dict()
        finally:
            self._data_storage_instance.toggle_callback_block(False)
            self.block_qt_signals(False)
            self.widget._bin_advanced_options_toggle()
            self.widget._detect_advanced_options_toggle()

    def _connect_arcos_parameter_callbacks(self):
        for param in fields(self._data_storage_instance.arcos_parameters.value):
            getattr(
                self._data_storage_instance.arcos_parameters.value, param.name
            ).value_changed.connect(self._update_arcos_parameters_ui)

        self._data_storage_instance.output_order.value_changed.connect(
            self._update_arcos_parameters_ui
        )

        # whenever the ui is updated, update the data storage instance
        for i in [self.widget.bias_method]:
            i.currentIndexChanged.connect(self._update_arcos_parameters_object)
        for i in [
            self.widget.clip_low,
            self.widget.clip_high,
            self.widget.smooth_k,
            self.widget.bias_k,
            self.widget.polyDeg,
            self.widget.bin_threshold,
            self.widget.bin_peak_threshold,
        ]:
            i.valueChanged.connect(self._update_arcos_parameters_object)
        for i in [
            self.widget.interpolate_meas,
            self.widget.clip_meas,
            self.widget.bin_advanced_options,
            self.widget.detect_advance_options,
        ]:
            i.stateChanged.connect(self._update_arcos_parameters_object)
        for i in [
            self.widget.neighbourhood_size,
            self.widget.min_clustersize,
            self.widget.nprev_spinbox,
        ]:
            i.valueChanged.connect(self._update_arcos_parameters_object)
        for i in [self.widget.epsPrev_spinbox]:
            i.valueChanged.connect(self._update_arcos_parameters_object)
        for i in [self.widget.eps_estimation_combobox]:
            i.currentIndexChanged.connect(self._update_arcos_parameters_object)
        for i in [self.widget.min_dur, self.widget.total_event_size]:
            i.valueChanged.connect(self._update_arcos_parameters_object)
        for i in [
            self.widget.add_convex_hull_checkbox,
            self.widget.add_all_cells_checkbox,
            self.widget.add_bin_cells_checkbox,
        ]:
            i.stateChanged.connect(self._update_arcos_parameters_object)

        self.widget.output_order.textChanged.connect(
            self._update_arcos_parameters_object
        )

    def block_qt_signals(self, block=True):
        """Block or unblock signals for a widget and all its child widgets."""
        self.widget.blockSignals(block)
        for child_widget in self.widget.findChildren(QtWidgets.QWidget):
            child_widget.blockSignals(block)

    def __del__(self):
        try:
            self._stop_worker()
        except (AttributeError, RuntimeError):
            pass


if __name__ == "__main__":
    import sys

    from arcos_gui.processing import DataStorage  # noqa: F811

    app = QtWidgets.QApplication(sys.argv)
    controller = ArcosController(DataStorage())
    controller.widget.show()
    sys.exit(app.exec_())
