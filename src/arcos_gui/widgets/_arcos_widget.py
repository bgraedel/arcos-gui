"""Widget to set arcos parameters and run arcos algorithm."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from arcos_gui.processing import arcos_worker
from napari.utils.notifications import show_info
from qtpy import QtWidgets, uic
from qtpy.QtCore import QSize, QThread, QTimer
from qtpy.QtGui import QIcon, QMovie

if TYPE_CHECKING:
    from arcos_gui.processing import DataStorage

# icons
ICONS = Path(__file__).parent.parent / "_icons"


class _arcosWidget:
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
    add_convex_hull_checkbox: QtWidgets.QCheckBox
    cancel_button: QtWidgets.QPushButton

    def setup_ui(self):
        """Setup UI. Loads it from ui file."""
        uic.loadUi(self.UI_FILE, self)  # load QtDesigner .ui file
        self.loading_icon = QMovie(str(ICONS / "Dual Ring-1s-200px.gif"))
        self.loading_icon.setScaledSize(QSize(40, 40))
        self.loading_icon.stop()
        self.update_arcos.setIcon(QIcon(self.loading_icon.currentPixmap()))
        self.cancel_button.setStyleSheet("background-color : #7C0A02; color : white")
        self.cancel_button.hide()
        self._setup_timer()

    def _set_loading_icon(self, frame=None):
        self.update_arcos.setIcon(QIcon(self.loading_icon.currentPixmap()))

    def _hide_loading_icon(self):
        self.update_arcos.setIcon(QIcon())
        # self.loading_icon.frameChanged.disconnect(self._set_loading_icon)

    def _setup_timer(self):
        self.timer_loading_icon_show = QTimer()
        self.timer_loading_icon_show.setSingleShot(True)

    def start_loading(self):
        """Start loading icon animation."""
        self.update_arcos.setEnabled(False)
        self.run_binarization_only.setEnabled(False)
        self.cancel_button.show()
        self.cancel_button.setEnabled(True)
        self.update_arcos.setText("")
        self.run_binarization_only.setText("")
        self.timer_loading_icon_show.timeout.connect(self._show_loading_icon)
        self.timer_loading_icon_show.start(100)

    def _show_loading_icon(self):
        self.loading_icon.start()
        self.loading_icon.frameChanged.connect(self._set_loading_icon)

    def stop_loading(self):
        """Stop loading icon animation."""
        self.timer_loading_icon_show.stop()
        self._hide_loading_icon()
        self.loading_icon.stop()
        self.cancel_button.hide()
        self.update_arcos.setText("Update ARCOS")
        self.run_binarization_only.setText("Binarize Data")
        self.cancel_button.setEnabled(False)
        self.update_arcos.setEnabled(True)
        self.run_binarization_only.setEnabled(True)


class ArcosWidget(QtWidgets.QWidget, _arcosWidget):
    """Widget to set arcos parameters and run arcos algorithm."""

    def __init__(self, data_storage_instance: DataStorage, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self._what_to_run: set = set()
        self._data_storage_instance = data_storage_instance
        self.bias_met_advanced_state = {
            "bias_method": self.bias_method.currentText(),
            "smoothK": self.smooth_k.value(),
        }
        self.detect_advanced_state = {
            "eps": self.neighbourhood_size.value(),
            "auto_eps": self.eps_estimation_combobox.currentText(),
            "cluter_linking_dist_check": self.Cluster_linking_dist_checkbox.isChecked(),
            "epsPrev": self.epsPrev_spinbox.value(),
            "nPrev": self.nprev_spinbox.value(),
        }
        self.my_qtimer = QTimer(self)
        self.my_qtimer.timeout.connect(self.timer_timeout)

        self._init_callbacks_for_whattorun()
        self._init_callbacks_visible_arcosparameters()
        self._set_default_visible()
        self._update_what_to_run_all()
        self._connect_ui_callbacks()
        self._connect_arcos_parameter_callbacks()
        self.createWorkerThread()
        self._connect_callbacks()

    def _connect_callbacks(self):
        self.update_arcos.clicked.connect(self._update_arcos_parameters)
        self.run_binarization_only.clicked.connect(self._update_arcos_parameters)
        self.run_binarization_only.clicked.connect(
            self._data_storage_instance.reset_arcos_data
        )
        self.update_arcos.clicked.connect(self.update_worker_with_data)
        self.run_binarization_only.clicked.connect(self.update_worker_with_data)
        self.cancel_button.clicked.connect(self.abort_worker)

    def _update_datastorage_with_bin_data(self, bin_data):
        self._data_storage_instance.columns.measurement_bin = bin_data[0]
        self._data_storage_instance.columns.measurement_resc = bin_data[1]
        self._data_storage_instance.arcos_binarization.value = bin_data[2]

    def _update_datastorage_with_arcos(self, arcos_data):
        self._data_storage_instance.arcos_output.value = arcos_data[0]
        self._data_storage_instance.arcos_stats.value = arcos_data[1]

    def createWorkerThread(self):
        # Setup the worker object and the worker_thread.

        self.worker = arcos_worker(
            self._what_to_run,
            show_info,
            wait_for_parameter_update=True,
        )
        self.worker_thread = QThread(self)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

        # Connect any worker signals
        self.update_arcos.clicked.connect(self.worker.run_arcos)
        self.run_binarization_only.clicked.connect(self.worker.run_bin)
        self.worker.binarization_finished.connect(
            self._update_datastorage_with_bin_data
        )
        self.worker.new_eps.connect(self._update_eps)
        self.worker.new_arcos_output.connect(self._update_datastorage_with_arcos)
        self.worker.finished.connect(self._enable_ui_elements)
        self.worker.started.connect(self._disable_ui_elements)
        self.worker.finished.connect(self.stop_timer)
        self.worker.aborted.connect(self.stop_timer)
        self.worker.aborted.connect(self._show_aborted_message)
        if self.parent() is not None:
            self.parent().destroyed.connect(self._stop_worker)
        else:
            self.destroyed.connect(self._stop_worker)

    def _show_aborted_message(self, err):
        show_info(f"ARCOS calculation aborted due to: {err}")

    def _enable_ui_elements(self):
        self.stop_loading()

    def _disable_ui_elements(self):
        self.start_loading()

    def _update_eps(self, eps):
        self._data_storage_instance.arcos_parameters.neighbourhood_size.value = eps

    def update_worker_with_data(self):
        self.worker.what_to_run = self._what_to_run
        self.worker.filtered_data = self._data_storage_instance.filtered_data.value
        self.worker.columns = self._data_storage_instance.columns
        self.worker.arcos_parameters.set_all_parameters(
            self._data_storage_instance.arcos_parameters
        )

    def abort_worker(self):
        self.worker.aborted_flag = True
        self.cancel_button.setEnabled(False)
        self.cancel_button.setText("Aborting...")
        self.timer_start()

    def timer_start(self):
        self.time_left_int = 10
        self.my_qtimer.start(1000)

    def timer_timeout(self):
        self.time_left_int -= 1

        if self.time_left_int < 8:
            self.update_abort_button()

        if self.time_left_int == 0:
            self.stop_timer()
            self.forceWorkerReset()

    def stop_timer(self):
        self.my_qtimer.stop()
        self.cancel_button.setText("Abort")
        self.time_left_int = 10

    def update_abort_button(self):
        self.cancel_button.setText(f"Aborting... {str(self.time_left_int)} s (timeout)")

    def forceWorkerReset(self):
        if self.worker_thread.isRunning() and not self.worker.idle_flag:
            old_arcos_object = self.worker.arcos_object
            arcos_raw_output = self.worker.arcos_raw_output

            self.worker_thread.terminate()
            self.worker_thread.wait(5000)

            self.createWorkerThread()
            self.stop_loading()
            self.update_worker_with_data()
            self.worker.arcos_object = old_arcos_object
            self.worker.arcos_raw_output = arcos_raw_output

        self.stop_timer()

    def _stop_worker(self):
        self.worker_thread.quit()
        self.worker_thread.wait(1000)
        if self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait(1000)

    def closeEvent(self, event):
        self._stop_worker()
        event.accept()

    def _connect_ui_callbacks(self):
        self.bin_advanced_options.clicked.connect(self._bin_advanced_options_toggle)
        self.detect_advance_options.clicked.connect(
            self._detect_advanced_options_toggle
        )
        self.eps_estimation_combobox.currentIndexChanged.connect(
            self._eps_estimation_toggle
        )
        self.Cluster_linking_dist_checkbox.clicked.connect(self._epsPrev_toggle)

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

        self.smooth_k.setVisible(checked)
        self.smooth_k_label.setVisible(checked)
        self.bias_method.setVisible(checked)
        self.bias_method_label.setVisible(checked)

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
        if self.bias_method.currentText() == "runmed":
            self.smooth_k.setVisible(True)
            self.smooth_k_label.setVisible(True)
            self.polyDeg.setVisible(False)
            self.polyDeg_label.setVisible(False)
            self.bias_k.setVisible(True)
            self.bias_k_label.setVisible(True)
            self.bin_peak_threshold.setVisible(True)
            self.bin_peak_threshold_label.setVisible(True)
            self.bin_threshold.setVisible(True)
            self.bin_threshold_label.setVisible(True)

        if self.bias_method.currentText() == "lm":
            self.smooth_k.setVisible(True)
            self.smooth_k_label.setVisible(True)
            self.polyDeg.setVisible(True)
            self.polyDeg_label.setVisible(True)
            self.bias_k.setVisible(False)
            self.bias_k_label.setVisible(False)
            self.bin_peak_threshold.setVisible(True)
            self.bin_peak_threshold_label.setVisible(True)
            self.bin_threshold.setVisible(True)
            self.bin_threshold_label.setVisible(True)

        if self.bias_method.currentText() == "none":
            self.smooth_k.setVisible(True)
            self.smooth_k_label.setVisible(True)
            self.polyDeg.setVisible(False)
            self.polyDeg_label.setVisible(False)
            self.bias_k.setVisible(False)
            self.bias_k_label.setVisible(False)
            self.bin_peak_threshold.setVisible(False)
            self.bin_peak_threshold_label.setVisible(False)
            self.bin_threshold.setVisible(True)
            self.bin_threshold_label.setVisible(True)

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

    def _init_callbacks_for_whattorun(self):
        """Connect callbacks for updating 'what to run'.

        This is used to run only the appropriate parts of the
        run_arcos method depending on the parameters changed.
        """
        # for every changable field connect the appropriate what_to_run function
        for i in [self.bias_method]:
            i.currentIndexChanged.connect(self._update_what_to_run_all)
        for i in [
            self.clip_low,
            self.clip_high,
            self.smooth_k,
            self.bias_k,
            self.polyDeg,
            self.bin_threshold,
            self.bin_peak_threshold,
        ]:
            i.valueChanged.connect(self._update_what_to_run_all)
        for i in [self.interpolate_meas, self.clip_meas]:
            i.stateChanged.connect(self._update_what_to_run_all)
        for i in [self.neighbourhood_size, self.min_clustersize, self.nprev_spinbox]:
            i.valueChanged.connect(self._update_what_to_run_tracking)
        for i in [self.epsPrev_spinbox]:
            i.valueChanged.connect(self._update_what_to_run_tracking)
        for i in [self.eps_estimation_combobox]:
            i.currentIndexChanged.connect(self._update_what_to_run_tracking)
        for i in [self.min_dur, self.total_event_size]:
            i.valueChanged.connect(self._update_what_to_run_filtering)

        self.add_convex_hull_checkbox.stateChanged.connect(
            self._update_what_to_run_filtering
        )

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
        self._clear_what_to_run()
        self._what_to_run.add("tracking")
        self._what_to_run.add("filtering")

    def _update_what_to_run_filtering(self):
        """Adds 'from_filtering' to the what_to_run attirbute,
        that is used in the main function to check if what to run
        when certain field have updated values."""
        self._clear_what_to_run()
        self._what_to_run.add("filtering")

    def _clear_what_to_run(self):
        """Clears the what_to_run attribute."""
        self._what_to_run.clear()

    def _update_arcos_parameters(self):
        """Update the parameters in the data storage instance"""
        if not self.Cluster_linking_dist_checkbox.isChecked():
            epsPrev = None
        else:
            epsPrev = self.epsPrev_spinbox.value()
        self._data_storage_instance.arcos_parameters.interpolate_meas.value = (
            self.interpolate_meas.isChecked()
        )
        self._data_storage_instance.arcos_parameters.clip_meas.value = (
            self.clip_meas.isChecked()
        )
        self._data_storage_instance.arcos_parameters.clip_low.value = (
            self.clip_low.value()
        )
        self._data_storage_instance.arcos_parameters.clip_high.value = (
            self.clip_high.value()
        )
        self._data_storage_instance.arcos_parameters.smooth_k.value = (
            self.smooth_k.value()
        )
        self._data_storage_instance.arcos_parameters.bias_k.value = self.bias_k.value()
        self._data_storage_instance.arcos_parameters.bias_method.value = (
            self.bias_method.currentText()
        )
        self._data_storage_instance.arcos_parameters.polyDeg.value = (
            self.polyDeg.value()
        )
        self._data_storage_instance.arcos_parameters.bin_threshold.value = (
            self.bin_threshold.value()
        )
        self._data_storage_instance.arcos_parameters.bin_peak_threshold.value = (
            self.bin_peak_threshold.value()
        )
        self._data_storage_instance.arcos_parameters.neighbourhood_size.value = (
            self.neighbourhood_size.value()
        )
        self._data_storage_instance.arcos_parameters.min_clustersize.value = (
            self.min_clustersize.value()
        )
        self._data_storage_instance.arcos_parameters.nprev.value = (
            self.nprev_spinbox.value()
        )
        self._data_storage_instance.arcos_parameters.min_dur.value = (
            self.min_dur.value()
        )
        self._data_storage_instance.arcos_parameters.total_event_size.value = (
            self.total_event_size.value()
        )
        self._data_storage_instance.arcos_parameters.add_convex_hull.value = (
            self.add_convex_hull_checkbox.isChecked()
        )
        self._data_storage_instance.arcos_parameters.epsPrev.value = epsPrev
        self._data_storage_instance.arcos_parameters.eps_method.value = (
            self.eps_estimation_combobox.currentText()
        )

    def _update_neighbourhood_size(self):
        value = self._data_storage_instance.arcos_parameters.neighbourhood_size.value
        self.neighbourhood_size.setValue(value)

    def _connect_arcos_parameter_callbacks(self):
        self._data_storage_instance.arcos_parameters.neighbourhood_size.value_changed_connect(
            self._update_neighbourhood_size
        )


if __name__ == "__main__":
    import sys

    from arcos_gui.processing import DataStorage  # noqa: F811

    app = QtWidgets.QApplication(sys.argv)
    widget = ArcosWidget(DataStorage())
    widget.show()
    sys.exit(app.exec_())
