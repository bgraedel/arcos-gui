import pytest
from arcos_gui.processing import DataStorage
from arcos_gui.widgets import ArcosController
from qtpy.QtCore import Qt


@pytest.fixture()
def make_arcos_widget(qtbot):
    ds = DataStorage()
    controller = ArcosController(ds)
    qtbot.addWidget(controller.widget)
    return controller, qtbot


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


def test_toggle_biasmethod_visibility(make_arcos_widget):
    arcos_controller, qtbot = make_arcos_widget
    arcos_controller.widget.bias_method.setCurrentText("runmed")
    assert arcos_controller.widget.smooth_k.isVisibleTo(arcos_controller.widget) is True
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


def test_update_arcos_parameters(make_arcos_widget):
    # makes a DataStorage object and fills it with the default parameters
    ds_test = DataStorage()
    ds_test.arcos_parameters.interpolate_meas.value = True
    ds_test.arcos_parameters.clip_meas.value = False
    ds_test.arcos_parameters.clip_low.value = 0.001
    ds_test.arcos_parameters.clip_high.value = 0.999
    ds_test.arcos_parameters.bias_method.value = "none"
    ds_test.arcos_parameters.smooth_k.value = 3
    ds_test.arcos_parameters.bias_k.value = 25
    ds_test.arcos_parameters.polyDeg.value = 1
    ds_test.arcos_parameters.bin_threshold.value = 0.5
    ds_test.arcos_parameters.bin_peak_threshold.value = 0.2
    ds_test.arcos_parameters.eps_method.value = "mean"
    ds_test.arcos_parameters.neighbourhood_size.value = 40
    ds_test.arcos_parameters.epsPrev.value = None
    ds_test.arcos_parameters.min_clustersize.value = 5
    ds_test.arcos_parameters.nprev.value = 1
    ds_test.arcos_parameters.min_dur.value = 3
    ds_test.arcos_parameters.total_event_size.value = 10
    # updates the DataStorage instance linked to the arcos widget
    ds_test.arcos_parameters
    arcos_widget, qtbot = make_arcos_widget
    arcos_widget._update_arcos_parameters()
    # checks if the parameters are updated correctly
    assert (
        arcos_widget._data_storage_instance.arcos_parameters == ds_test.arcos_parameters
    )
