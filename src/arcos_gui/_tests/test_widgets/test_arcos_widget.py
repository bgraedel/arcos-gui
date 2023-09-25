import pytest
from arcos_gui.processing import DataStorage
from arcos_gui.widgets._arcos_widget import (
    ArcosController,
    OutputOrderValidator,
    _arcosWidget,
)
from qtpy.QtCore import Qt
from qtpy.QtGui import QValidator


@pytest.fixture()
def make_arcos_widget(qtbot):
    ds = DataStorage()
    controller = ArcosController(ds)
    # qtbot.addWidget(controller.widget)
    yield controller, qtbot
    try:
        controller.closeEvent()
        controller.widget.close()
    except (AttributeError, RuntimeError):
        pass
    del controller


@pytest.fixture()
def make_arcos_ui(qtbot):
    widget = _arcosWidget()
    qtbot.addWidget(widget)
    yield widget, qtbot
    widget.close()


@pytest.fixture
def setup_validator():
    vColsCore = ["t", "x", "y"]
    return OutputOrderValidator(vColsCore)


def test_open_widget(make_arcos_widget):
    arcos_controller, _ = make_arcos_widget
    assert arcos_controller


def test_arcos_widget_defaults(make_arcos_widget):
    arcos_controller, qtbot = make_arcos_widget
    # Test the initial values of the widget's attributes
    assert arcos_controller.widget.clip_meas.isChecked() is False
    assert arcos_controller.widget.clip_low.value() == 0.001
    assert arcos_controller.widget.clip_high.value() == 0.999
    assert arcos_controller.widget.bin_advanced_options.isChecked() is False
    assert arcos_controller.widget.bias_method.currentText() == "none"
    assert arcos_controller.widget.smooth_k.value() == 3
    assert arcos_controller.widget.bias_k.value() == 25
    assert arcos_controller.widget.polyDeg.value() == 1
    assert arcos_controller.widget.bin_peak_threshold.value() == 0.2
    assert arcos_controller.widget.bin_threshold.value() == 0.5
    assert arcos_controller.widget.detect_advance_options.isChecked() is False
    assert arcos_controller.widget.eps_estimation_combobox.currentText() == "mean"
    assert arcos_controller.widget.neighbourhood_size.value() == 40
    assert arcos_controller.widget.Cluster_linking_dist_checkbox.isChecked() is False
    assert arcos_controller.widget.epsPrev_spinbox.value() == 40
    assert arcos_controller.widget.nprev_spinbox.value() == 1
    assert arcos_controller.widget.min_clustersize.value() == 5
    assert arcos_controller.widget.min_dur.value() == 3
    assert arcos_controller.widget.total_event_size.value() == 10
    arcos_controller.widget.close()


def test_the_what_to_run_changes(make_arcos_widget):
    arcos_controller, qtbot = make_arcos_widget
    assert arcos_controller._what_to_run == {"binarization", "tracking", "filtering"}
    qtbot.mouseClick(arcos_controller.widget.run_binarization_only, Qt.LeftButton)
    assert arcos_controller._what_to_run == {
        "binarization",
        "tracking",
        "filtering",
    }  # no data so should not change
    qtbot.mouseClick(arcos_controller.widget.update_arcos, Qt.LeftButton)
    assert arcos_controller._what_to_run == {"binarization", "tracking", "filtering"}
    qtbot.mouseClick(arcos_controller.widget.clip_meas, Qt.LeftButton)
    assert arcos_controller._what_to_run == {"tracking", "filtering", "binarization"}
    arcos_controller._what_to_run.clear()
    qtbot.mouseClick(arcos_controller.widget.interpolate_meas, Qt.LeftButton)
    assert arcos_controller._what_to_run == {"tracking", "filtering", "binarization"}
    arcos_controller._what_to_run.clear()
    arcos_controller.widget.clip_low.setValue(0.02)
    assert arcos_controller._what_to_run == {"tracking", "filtering", "binarization"}
    arcos_controller._what_to_run.clear()
    arcos_controller.widget.clip_high.setValue(0.88)
    assert arcos_controller._what_to_run == {"tracking", "filtering", "binarization"}
    arcos_controller._what_to_run.clear()
    assert arcos_controller.widget.bias_method.currentText() == "none"
    arcos_controller.widget.bias_method.setCurrentText("none")
    assert arcos_controller._what_to_run == set()
    arcos_controller.widget.bias_method.setCurrentText("runmed")
    assert arcos_controller._what_to_run == {"tracking", "filtering", "binarization"}
    arcos_controller._what_to_run.clear()
    arcos_controller.widget.smooth_k.setValue(2)
    assert arcos_controller._what_to_run == {"tracking", "filtering", "binarization"}
    arcos_controller._what_to_run.clear()
    arcos_controller.widget.bias_k.setValue(30)
    assert arcos_controller._what_to_run == {"tracking", "filtering", "binarization"}
    arcos_controller._what_to_run.clear()
    arcos_controller.widget.polyDeg.setValue(2)
    assert arcos_controller._what_to_run == {"tracking", "filtering", "binarization"}
    arcos_controller._what_to_run.clear()
    arcos_controller.widget.bin_peak_threshold.setValue(0.3)
    assert arcos_controller._what_to_run == {"tracking", "filtering", "binarization"}
    arcos_controller._what_to_run.clear()
    arcos_controller.widget.bin_threshold.setValue(0.2)
    assert arcos_controller._what_to_run == {"tracking", "filtering", "binarization"}
    arcos_controller._what_to_run.clear()
    arcos_controller.widget.eps_estimation_combobox.setCurrentIndex(0)
    arcos_controller.widget.eps_estimation_combobox.setCurrentIndex(1)
    assert arcos_controller._what_to_run == {"tracking", "filtering"}
    arcos_controller._what_to_run.clear()
    arcos_controller.widget.neighbourhood_size.setValue(50)
    assert arcos_controller._what_to_run == {"tracking", "filtering"}
    arcos_controller._what_to_run.clear()
    arcos_controller.widget.nprev_spinbox.setValue(2)
    assert arcos_controller._what_to_run == {"tracking", "filtering"}
    arcos_controller._what_to_run.clear()
    arcos_controller.widget.min_clustersize.setValue(6)
    assert arcos_controller._what_to_run == {"tracking", "filtering"}
    arcos_controller._what_to_run.clear()
    arcos_controller.widget.min_dur.setValue(4)
    assert arcos_controller._what_to_run == {"filtering"}
    arcos_controller._what_to_run.clear()
    arcos_controller.widget.total_event_size.setValue(11)
    assert arcos_controller._what_to_run == {"filtering"}
    arcos_controller.widget.close()


def test_set_default_visible(make_arcos_widget):
    arcos_controller, qtbot = make_arcos_widget
    assert arcos_controller.widget.clip_meas.isChecked() is False
    assert (
        arcos_controller.widget.clip_low.isVisibleTo(arcos_controller.widget) is False
    )
    assert (
        arcos_controller.widget.clip_high.isVisibleTo(arcos_controller.widget) is False
    )
    qtbot.mouseClick(arcos_controller.widget.clip_meas, Qt.LeftButton)
    assert arcos_controller.widget.clip_low.isVisibleTo(arcos_controller.widget) is True
    assert (
        arcos_controller.widget.clip_high.isVisibleTo(arcos_controller.widget) is True
    )
    qtbot.mouseClick(arcos_controller.widget.clip_meas, Qt.LeftButton)
    assert (
        arcos_controller.widget.clip_low.isVisibleTo(arcos_controller.widget) is False
    )
    assert (
        arcos_controller.widget.clip_high.isVisibleTo(arcos_controller.widget) is False
    )
    arcos_controller.widget.close()


def test_toggle_biasmethod_visibility(make_arcos_widget):
    arcos_controller, qtbot = make_arcos_widget
    arcos_controller.widget.bias_method.setCurrentText("runmed")
    assert (
        arcos_controller.widget.smooth_k.isVisibleTo(arcos_controller.widget) is False
    )  # advanced options are not toggled
    arcos_controller.widget.bin_advanced_options.setChecked(True)
    assert arcos_controller.widget.smooth_k.isVisibleTo(arcos_controller.widget) is True
    arcos_controller.widget.bias_method.setCurrentText("runmed")
    assert (
        arcos_controller.widget.smooth_k_label.isVisibleTo(arcos_controller.widget)
        is True
    )
    assert arcos_controller.widget.bias_k.isVisibleTo(arcos_controller.widget) is True
    assert (
        arcos_controller.widget.bias_k_label.isVisibleTo(arcos_controller.widget)
        is True
    )
    assert arcos_controller.widget.polyDeg.isVisibleTo(arcos_controller.widget) is False
    assert (
        arcos_controller.widget.polyDeg_label.isVisibleTo(arcos_controller.widget)
        is False
    )
    assert (
        arcos_controller.widget.bin_peak_threshold.isVisibleTo(arcos_controller.widget)
        is True
    )
    assert (
        arcos_controller.widget.bin_peak_threshold_label.isVisibleTo(
            arcos_controller.widget
        )
        is True
    )
    assert (
        arcos_controller.widget.bin_threshold.isVisibleTo(arcos_controller.widget)
        is True
    )
    assert (
        arcos_controller.widget.bin_threshold_label.isVisibleTo(arcos_controller.widget)
        is True
    )
    arcos_controller.widget.bias_method.setCurrentText("lm")
    assert arcos_controller.widget.smooth_k.isVisibleTo(arcos_controller.widget) is True
    assert (
        arcos_controller.widget.smooth_k_label.isVisibleTo(arcos_controller.widget)
        is True
    )
    assert arcos_controller.widget.bias_k.isVisibleTo(arcos_controller.widget) is False
    assert (
        arcos_controller.widget.bias_k_label.isVisibleTo(arcos_controller.widget)
        is False
    )
    assert arcos_controller.widget.polyDeg.isVisibleTo(arcos_controller.widget) is True
    assert (
        arcos_controller.widget.polyDeg_label.isVisibleTo(arcos_controller.widget)
        is True
    )
    assert (
        arcos_controller.widget.bin_peak_threshold.isVisibleTo(arcos_controller.widget)
        is True
    )
    assert (
        arcos_controller.widget.bin_peak_threshold_label.isVisibleTo(
            arcos_controller.widget
        )
        is True
    )
    assert (
        arcos_controller.widget.bin_threshold.isVisibleTo(arcos_controller.widget)
        is True
    )
    assert (
        arcos_controller.widget.bin_threshold_label.isVisibleTo(arcos_controller.widget)
        is True
    )
    arcos_controller.widget.bias_method.setCurrentText("none")
    assert arcos_controller.widget.smooth_k.isVisibleTo(arcos_controller.widget) is True
    assert (
        arcos_controller.widget.smooth_k_label.isVisibleTo(arcos_controller.widget)
        is True
    )
    assert arcos_controller.widget.bias_k.isVisibleTo(arcos_controller.widget) is False
    assert (
        arcos_controller.widget.bias_k_label.isVisibleTo(arcos_controller.widget)
        is False
    )
    assert arcos_controller.widget.polyDeg.isVisibleTo(arcos_controller.widget) is False
    assert (
        arcos_controller.widget.polyDeg_label.isVisibleTo(arcos_controller.widget)
        is False
    )
    assert (
        arcos_controller.widget.bin_peak_threshold.isVisibleTo(arcos_controller.widget)
        is False
    )
    assert (
        arcos_controller.widget.bin_peak_threshold_label.isVisibleTo(
            arcos_controller.widget
        )
        is False
    )
    assert (
        arcos_controller.widget.bin_threshold.isVisibleTo(arcos_controller.widget)
        is True
    )
    assert (
        arcos_controller.widget.bin_threshold_label.isVisibleTo(arcos_controller.widget)
        is True
    )
    arcos_controller.widget.close()


def test_update_arcos_parameters(make_arcos_widget):
    # makes a DataStorage object and fills it with the default parameters
    ds_test = DataStorage()
    ds_test.arcos_parameters.value.interpolate_meas.value = True
    ds_test.arcos_parameters.value.clip_meas.value = False
    ds_test.arcos_parameters.value.clip_low.value = 0.001
    ds_test.arcos_parameters.value.clip_high.value = 0.999
    ds_test.arcos_parameters.value.bias_method.value = "none"
    ds_test.arcos_parameters.value.smooth_k.value = 3
    ds_test.arcos_parameters.value.bias_k.value = 25
    ds_test.arcos_parameters.value.polyDeg.value = 1
    ds_test.arcos_parameters.value.bin_threshold.value = 0.5
    ds_test.arcos_parameters.value.bin_peak_threshold.value = 0.2
    ds_test.arcos_parameters.value.eps_method.value = "mean"
    ds_test.arcos_parameters.value.neighbourhood_size.value = 40
    ds_test.arcos_parameters.value.epsPrev.value = None
    ds_test.arcos_parameters.value.min_clustersize.value = 5
    ds_test.arcos_parameters.value.nprev.value = 1
    ds_test.arcos_parameters.value.min_dur.value = 3
    ds_test.arcos_parameters.value.total_event_size.value = 10
    # updates the DataStorage instance linked to the arcos widget
    ds_test.arcos_parameters
    arcos_widget, qtbot = make_arcos_widget
    arcos_widget._update_arcos_parameters_object()
    # checks if the parameters are updated correctly
    assert (
        arcos_widget._data_storage_instance.arcos_parameters == ds_test.arcos_parameters
    )
    arcos_widget.widget.close()


def test_max_length(setup_validator):
    validator = setup_validator
    result, _, _ = validator.validate("txyzx", 5)
    assert result == QValidator.Invalid


def test_allowed_characters(setup_validator):
    validator = setup_validator
    result, _, _ = validator.validate("txyh", 4)
    assert result == QValidator.Invalid


def test_no_duplicates(setup_validator):
    validator = setup_validator
    result, _, _ = validator.validate("txxt", 4)
    assert result == QValidator.Invalid


def test_string_length_less_than_vColsCore(setup_validator):
    validator = setup_validator
    result, _, _ = validator.validate("tx", 2)
    assert result == QValidator.Intermediate


def test_all_required_characters(setup_validator):
    validator = setup_validator
    result, _, _ = validator.validate("txz", 3)
    assert result == QValidator.Intermediate


def test_valid_string(setup_validator):
    validator = setup_validator
    result, _, _ = validator.validate("txyz", 4)
    assert result == QValidator.Acceptable


def test_output_order_text_changed(make_arcos_widget, qtbot):
    widget = make_arcos_widget[0].widget
    widget.updateValidator(None)
    widget.output_order.setText("tyx")
    widget._onTextChanged("tyx")
    assert widget.update_arcos.isEnabled() is True
    assert widget.run_binarization_only.isEnabled() is True
    assert widget.output_order.styleSheet() == ""

    widget.output_order.setText("tzx")
    widget._onTextChanged("tzx")
    assert widget.update_arcos.isEnabled() is False
    assert widget.run_binarization_only.isEnabled() is False
    assert (
        widget.output_order.styleSheet()
        == "QLineEdit { background-color: #f6989d; color: black }"
    )
    widget.close()


def test_createWorkerThread(make_arcos_widget):
    arcos_widget = make_arcos_widget[0]
    # Call the method
    arcos_widget.createWorkerThread(arcos_widget._what_to_run)

    # Check that the worker is up
    assert arcos_widget.worker is not None


def test_update_eps(make_arcos_widget):
    arcos_widget = make_arcos_widget[0]
    # Call the method with a test value
    arcos_widget._update_eps(5)

    # Check that the value was updated in the data storage instance
    assert (
        arcos_widget._data_storage_instance.arcos_parameters.value.neighbourhood_size.value
        == 5
    )
    arcos_widget.widget.close()


def test_abort_worker(make_arcos_widget):
    arcos_widget = make_arcos_widget[0]
    arcos_widget.createWorkerThread(arcos_widget._what_to_run)
    # Call the method
    arcos_widget.abort_worker()

    # Check that the aborted_flag attribute was set to True
    assert arcos_widget.worker.abort_requested is True
    arcos_widget.widget.close()


def test_closeEvent(make_arcos_widget):
    arcos_widget = make_arcos_widget[0]
    arcos_widget.createWorkerThread(arcos_widget._what_to_run)
    # Call the method
    arcos_widget.closeEvent()

    # Check that the worker_thread was terminated
    assert arcos_widget.worker.abort_requested is True


def test_bin_advanced_options_toggle(make_arcos_ui):
    widget = make_arcos_ui[0]

    # Check that the advanced options are hidden by default
    assert not widget.bin_advanced_options.isChecked()
    assert not widget.smooth_k.isVisibleTo(widget)
    assert not widget.bias_method.isVisibleTo(widget)
    # Check that the advanced options are shown when the button is checked
    widget.bin_advanced_options.setChecked(True)
    assert widget.smooth_k.isVisibleTo(widget)
    assert widget.bias_method.isVisibleTo(widget)

    # Check that the advanced options are hidden again when the button is unchecked
    widget.bin_advanced_options.setChecked(False)
    assert not widget.smooth_k.isVisibleTo(widget)
    assert not widget.bias_method.isVisibleTo(widget)
    widget.close()


def test_detect_advanced_options_toggle(make_arcos_ui):
    widget = make_arcos_ui[0]

    # Check that the advanced options are hidden by default
    assert not widget.detect_advance_options.isChecked()
    assert not widget.eps_estimation_label.isVisibleTo(widget)
    assert not widget.eps_estimation_combobox.isVisibleTo(widget)
    assert not widget.neighbourhood_label.isVisibleTo(widget)
    assert not widget.neighbourhood_size.isVisibleTo(widget)
    assert not widget.Cluster_linking_dist_checkbox.isVisibleTo(widget)
    assert not widget.epsPrev_spinbox.isVisibleTo(widget)
    assert not widget.nprev_label.isVisibleTo(widget)
    assert not widget.nprev_spinbox.isVisibleTo(widget)

    # Check that the advanced options are shown when the button is checked
    widget.detect_advance_options.setChecked(True)
    assert widget.eps_estimation_label.isVisibleTo(widget)
    assert widget.eps_estimation_combobox.isVisibleTo(widget)
    assert widget.neighbourhood_label.isVisibleTo(widget)
    assert widget.neighbourhood_size.isVisibleTo(widget)
    assert widget.Cluster_linking_dist_checkbox.isVisibleTo(widget)
    assert widget.epsPrev_spinbox.isVisibleTo(widget)
    assert widget.nprev_label.isVisibleTo(widget)
    assert widget.nprev_spinbox.isVisibleTo(widget)

    # Check that the advanced options are hidden again when the button is unchecked
    widget.detect_advance_options.setChecked(False)
    assert not widget.eps_estimation_label.isVisibleTo(widget)
    assert not widget.eps_estimation_combobox.isVisibleTo(widget)
    assert not widget.neighbourhood_label.isVisibleTo(widget)
    assert not widget.neighbourhood_size.isVisibleTo(widget)
    assert not widget.Cluster_linking_dist_checkbox.isVisibleTo(widget)
    assert not widget.epsPrev_spinbox.isVisibleTo(widget)
    assert not widget.nprev_label.isVisibleTo(widget)
    assert not widget.nprev_spinbox.isVisibleTo(widget)
    widget.close()


def test_eps_estimation_toggle(make_arcos_ui):
    widget = make_arcos_ui[0]

    # Check that the neighbourhood size is enabled by default
    assert not widget.neighbourhood_size.isEnabled()

    # Check that the neighbourhood size is disabled when the method is set to "auto"
    widget.eps_estimation_combobox.setCurrentText("kneepoint")
    assert not widget.neighbourhood_size.isEnabled()

    # Check that the neighbourhood size is enabled again when the method is set to "manual"
    widget.eps_estimation_combobox.setCurrentText("manual")
    assert widget.neighbourhood_size.isEnabled()
    widget.close()


def test_epsPrev_toggle(make_arcos_ui):
    widget = make_arcos_ui[0]

    # Check that the checkbox is unchecked by default
    assert not widget.Cluster_linking_dist_checkbox.isChecked()

    # Check that the spinbox is disabled by default
    assert not widget.epsPrev_spinbox.isEnabled()

    # Check that the spinbox is enabled when the checkbox is checked
    widget.Cluster_linking_dist_checkbox.setChecked(True)
    assert widget.epsPrev_spinbox.isEnabled()

    # Check that the spinbox is disabled again when the checkbox is unchecked
    widget.Cluster_linking_dist_checkbox.setChecked(False)
    assert not widget.epsPrev_spinbox.isEnabled()
    widget.close()
