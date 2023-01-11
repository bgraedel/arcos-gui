from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from arcos_gui.processing import arcos_wrapper
from napari.utils.notifications import show_info
from qtpy import QtWidgets, uic

if TYPE_CHECKING:
    from arcos_gui.processing import DataStorage


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
    nprev_spinbox_label: QtWidgets.QLabel
    min_dur_label: QtWidgets.QLabel
    tot_size_label: QtWidgets.QLabel

    interpolate_meas: QtWidgets.QCheckBox
    clip_meas: QtWidgets.QCheckBox
    clip_low: QtWidgets.QDoubleSpinBox
    clip_high: QtWidgets.QDoubleSpinBox
    bias_method: QtWidgets.QComboBox
    smooth_k: QtWidgets.QSpinBox
    bias_k: QtWidgets.QSpinBox
    polyDeg: QtWidgets.QSpinBox
    bin_peak_threshold: QtWidgets.QDoubleSpinBox
    bin_threshold: QtWidgets.QDoubleSpinBox
    neighbourhood_size: QtWidgets.QSpinBox
    min_clustersize: QtWidgets.QSpinBox
    min_dur: QtWidgets.QSpinBox
    total_event_size: QtWidgets.QSpinBox
    Progress: QtWidgets.QProgressBar
    update_arcos: QtWidgets.QPushButton
    run_binarization_only: QtWidgets.QPushButton
    arcos_group: QtWidgets.QGroupBox
    clip_frame: QtWidgets.QFrame
    add_convex_hull_checkbox: QtWidgets.QCheckBox

    def setup_ui(self):
        uic.loadUi(self.UI_FILE, self)  # load QtDesigner .ui file


class ArcosWidget(QtWidgets.QWidget, _arcosWidget):
    def __init__(self, data_storage_instance: DataStorage, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self._what_to_run: set = set()
        self._data_storage_instance = data_storage_instance
        self.arcos_wrapper_instance = arcos_wrapper(
            self._data_storage_instance, self._what_to_run, show_info
        )
        self._init_callbacks_for_whattorun()
        self._init_callbacks_visible_arcosparameters()
        self._set_default_visible()
        self._update_what_to_run_all()
        self.update_arcos.clicked.connect(self._run_arcos)
        self.run_binarization_only.clicked.connect(self._run_binarization_only)

    def _set_default_visible(self):
        """Method that sets the default visible widgets in the main window."""
        self.clip_meas.setChecked(False)
        self.polyDeg.setVisible(False)
        self.polyDeg_label.setVisible(False)

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

    def _run_arcos(self):
        self.arcos_wrapper_instance.run_arcos(
            self.interpolate_meas.isChecked(),
            self.clip_meas.isChecked(),
            self.clip_low.value(),
            self.clip_high.value(),
            self.smooth_k.value(),
            self.bias_k.value(),
            self.bias_method.currentText(),
            self.polyDeg.value(),
            self.bin_threshold.value(),
            self.bin_peak_threshold.value(),
            self.neighbourhood_size.value(),
            self.min_clustersize.value(),
            self.nprev_spinbox.value(),
            self.min_dur.value(),
            self.total_event_size.value(),
        )
        self._clear_what_to_run()
        self._update_arcos_parameters()

    def _run_binarization_only(self):
        if self._what_to_run:
            self._what_to_run.clear()
            self._what_to_run.add("binarization")
        self.arcos_wrapper_instance.run_arcos(
            self.interpolate_meas.isChecked(),
            self.clip_meas.isChecked(),
            self.clip_low.value(),
            self.clip_high.value(),
            self.smooth_k.value(),
            self.bias_k.value(),
            self.bias_method.currentText(),
            self.polyDeg.value(),
            self.bin_threshold.value(),
            self.bin_peak_threshold.value(),
            self.neighbourhood_size.value(),
            self.min_clustersize.value(),
            self.nprev_spinbox.value(),
            self.min_dur.value(),
            self.total_event_size.value(),
        )
        if self._what_to_run:
            self._update_what_to_run_tracking()
            self._update_arcos_parameters()

    def _update_arcos_parameters(self):
        """Update the parameters in the data storage instance"""
        self._data_storage_instance.arcos_parameters.interpolate_meas = (
            self.interpolate_meas.isChecked()
        )
        self._data_storage_instance.arcos_parameters.clip_meas = (
            self.clip_meas.isChecked()
        )
        self._data_storage_instance.arcos_parameters.clip_low = self.clip_low.value()
        self._data_storage_instance.arcos_parameters.clip_high = self.clip_high.value()
        self._data_storage_instance.arcos_parameters.smooth_k = self.smooth_k.value()
        self._data_storage_instance.arcos_parameters.bias_k = self.bias_k.value()
        self._data_storage_instance.arcos_parameters.bias_method = (
            self.bias_method.currentText()
        )
        self._data_storage_instance.arcos_parameters.polyDeg = self.polyDeg.value()
        self._data_storage_instance.arcos_parameters.bin_threshold = (
            self.bin_threshold.value()
        )
        self._data_storage_instance.arcos_parameters.bin_peak_threshold = (
            self.bin_peak_threshold.value()
        )
        self._data_storage_instance.arcos_parameters.neighbourhood_size = (
            self.neighbourhood_size.value()
        )
        self._data_storage_instance.arcos_parameters.min_clustersize = (
            self.min_clustersize.value()
        )
        self._data_storage_instance.arcos_parameters.nprev_spinbox = (
            self.nprev_spinbox.value()
        )
        self._data_storage_instance.arcos_parameters.min_dur = self.min_dur.value()
        self._data_storage_instance.arcos_parameters.total_event_size = (
            self.total_event_size.value()
        )


if __name__ == "__main__":
    import sys

    from arcos_gui.processing import DataStorage  # noqa: F811
    from napari import Viewer

    viewer = Viewer()

    app = QtWidgets.QApplication(sys.argv)
    widget = ArcosWidget(DataStorage())
    widget.show()
    sys.exit(app.exec_())
