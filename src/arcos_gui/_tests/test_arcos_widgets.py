# import gc
# from os import path, sep
# from pathlib import Path

# import pandas as pd
# import pytest
# from arcos_gui._config import ARCOS_LAYERS
# from pandas.testing import assert_frame_equal
# from qtpy.QtCore import Qt
# from qtpy.QtTest import QTest
# from skimage import data


# @pytest.fixture(scope="module")
# def data_frame():
#     col_2 = list(range(5, 10))
#     col_2.extend(list(range(10, 5, -1)))
#     d = {
#         "time": [1 for i in range(0, 10)],
#         "X": list(range(0, 10)),
#         "Y": col_2,
#         "collid": [1 for i in range(0, 10)],
#     }
#     df = pd.DataFrame(data=d)

#     return df


# @pytest.fixture()
# def dock_arcos_widget(make_napari_viewer, qtbot):
#     viewer = make_napari_viewer()
#     mywidget = viewer.window.add_plugin_dock_widget(
#         plugin_name="arcos-gui", widget_name="ARCOS Main Widget"
#     )
#     yield viewer, mywidget[1]
#     viewer.close()
#     gc.collect()


# def test_add_timestamp_no_layers(make_napari_viewer, capsys, qtbot):
#     viewer = make_napari_viewer()
#     mywidget = add_timestamp()
#     viewer.window.add_dock_widget(mywidget)
#     mywidget()
#     catptured = capsys.readouterr()
#     assert catptured.out == "INFO: No Layers to add Timestamp to\n"
#     viewer.close()


# def test_add_timestamp(make_napari_viewer, qtbot):
#     viewer = make_napari_viewer()
#     viewer.add_image(
#         data.binary_blobs(length=10, blob_size_fraction=0.2, n_dim=3), name="Image"
#     )
#     mywidget = add_timestamp()
#     viewer.window.add_dock_widget(mywidget)
#     mywidget()
#     mywidget()  # removes first timestamp and re adds new
#     assert viewer.layers["Timestamp"]
#     viewer.close()


# def test_export_data_widget_csv_no_data(make_napari_viewer, capsys, qtbot):
#     viewer = make_napari_viewer()
#     mywidget = export_data()
#     viewer.window.add_dock_widget(mywidget)
#     show_output_csv_folder()
#     output_csv_folder()
#     catptured = capsys.readouterr()
#     assert catptured.out == "INFO: No data to export, run arcos first\n"
#     viewer.close()


# def test_export_data_widget_csv_data(make_napari_viewer, tmp_path, data_frame, qtbot):
#     arcos_dir = str(tmp_path)
#     viewer = make_napari_viewer()
#     mywidget = export_data()
#     viewer.window.add_dock_widget(mywidget)
#     show_output_csv_folder()
#     output_csv_folder.filename.value = arcos_dir
#     stored_variables.data_merged = data_frame
#     output_csv_folder()
#     file = arcos_dir + sep + "arcos_data.csv"
#     df = pd.read_csv(file, index_col=0)
#     assert_frame_equal(df, data_frame)
#     viewer.close()


# def test_export_data_widget_images_no_data(make_napari_viewer, capsys, qtbot):
#     viewer = make_napari_viewer()
#     mywidget = export_data()
#     viewer.window.add_dock_widget(mywidget)
#     show_output_movie_folder()
#     output_movie_folder()
#     catptured = capsys.readouterr()
#     assert catptured.out == "INFO: No data to export, run arcos first\n"
#     viewer.close()


# def test_export_data_widget_images_data(make_napari_viewer, tmp_path, qtbot):
#     viewer = make_napari_viewer()
#     viewer.add_image(data.binary_blobs(length=1, blob_size_fraction=0.2, n_dim=3))
#     arcos_dir = str(tmp_path)
#     mywidget = export_data()
#     viewer.window.add_dock_widget(mywidget)
#     show_output_movie_folder()
#     output_movie_folder.filename.value = arcos_dir
#     output_movie_folder()
#     file = arcos_dir + sep + "arcos_000.png"
#     assert path.isfile(file)
#     viewer.close()


# def test_arcos_widget_choose_file(dock_arcos_widget, qtbot):
#     viewer, mywidget = dock_arcos_widget
#     stored_variables.filename_for_sample_data = str(
#         Path("src/arcos_gui/_tests/test_data/arcos_data.csv")
#     )
#     test_data = mywidget.data
#     direct_test_data = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
#     direct_test_data["t"] -= 1
#     # manually trigger button press
#     QTest.mouseClick(columnpicker.Ok.native, Qt.LeftButton)
#     assert columnpicker.frame.value == "t"
#     assert columnpicker.track_id.value == "id"
#     assert columnpicker.x_coordinates.value == "x"
#     assert columnpicker.y_coordinates.value == "y"
#     assert columnpicker.measurment.value == "m"
#     assert columnpicker.field_of_view_id.value == "Position"
#     assert_frame_equal(test_data, direct_test_data)
#     viewer.close()


# def test_filter_no_data(dock_arcos_widget, capsys, qtbot):
#     viewer, mywidget = dock_arcos_widget
#     mywidget.data = pd.DataFrame()
#     QTest.mouseClick(mywidget.filter_input_data, Qt.LeftButton)
#     catptured = capsys.readouterr()
#     assert catptured.out == "INFO: No data loaded, or not loaded correctly\n"
#     viewer.close()


# def test_filterwidget_data(dock_arcos_widget, capsys, qtbot):
#     viewer, mywidget = dock_arcos_widget
#     columnpicker.frame.choices = ["Frame"]
#     columnpicker.track_id.choices = ["track_id"]
#     columnpicker.x_coordinates.choices = ["X"]
#     columnpicker.y_coordinates.choices = ["Y"]
#     columnpicker.z_coordinates.choices = ["None"]
#     columnpicker.measurment.choices = ["Measurment"]
#     columnpicker.field_of_view_id.choices = ["Position"]
#     columnpicker.field_of_view_id.set_choice("None", "None")
#     columnpicker.z_coordinates.set_choice("None", "None")

#     columnpicker.frame.set_value = "Frame"
#     columnpicker.x_coordinates.value = "X"
#     columnpicker.y_coordinates.value = "Y"
#     columnpicker.track_id.value = "track_id"
#     columnpicker.measurment.value = "Measurment"
#     columnpicker.field_of_view_id.value = "Position"

#     df_1 = pd.read_csv("src/arcos_gui/_tests/test_data/filter_test.csv")
#     mywidget.data = df_1
#     df_1 = df_1[df_1["Position"] == 1]
#     mywidget.close_columnpicker()
#     mywidget.position.addItem("1", 1)
#     mywidget.position.setCurrentText("1")
#     QTest.mouseClick(mywidget.filter_input_data, Qt.LeftButton)
#     df = mywidget.filtered_data
#     # capture output
#     catptured = capsys.readouterr()
#     # assert output
#     assert catptured.out == "INFO: Data Filtered!\n"
#     assert_frame_equal(df, df_1)
#     viewer.close()


# def test_check_for_collid_column(dock_arcos_widget):
#     viewer, mywidget = dock_arcos_widget
#     df_1 = pd.read_csv("src/arcos_gui/_tests/test_data/data_clTrackID.csv")
#     out = mywidget.check_for_collid_column(
#         df_1, collid_column="clTrackID", suffix="old"
#     )
#     col_list = out.columns
#     assert "clTrackID" not in col_list
#     assert "clTrackID_old" in col_list


# def test_measurement_math_none(dock_arcos_widget):
#     viewer, mywidget = dock_arcos_widget
#     df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_test_meas_math.csv")
#     df["Measurment"] = df["Measurment"]
#     columnpicker.measurement_math.value = "None"
#     measurement_out, data_out = mywidget.calculate_measurment(
#         df, "Measurment", "Measurment_2"
#     )
#     assert "Measurment" == measurement_out
#     assert_frame_equal(df, data_out)


# def test_measurement_math_divide(dock_arcos_widget):
#     viewer, mywidget = dock_arcos_widget
#     df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_test_meas_math.csv")
#     df["Measurement_Ratio"] = df["Measurment"] / df["Measurment_2"]
#     columnpicker.measurement_math.value = "Divide"
#     measurement_out, data_out = mywidget.calculate_measurment(
#         df, "Measurment", "Measurment_2"
#     )
#     assert "Measurement_Ratio" == measurement_out
#     assert_frame_equal(df, data_out)


# def test_measurement_math_subtract(dock_arcos_widget):
#     viewer, mywidget = dock_arcos_widget
#     df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_test_meas_math.csv")
#     df["Measurement_Ratio"] = df["Measurment"] - df["Measurment_2"]
#     columnpicker.measurement_math.value = "Subtract"
#     measurement_out, data_out = mywidget.calculate_measurment(
#         df, "Measurment", "Measurment_2"
#     )
#     assert "Measurement_Difference" == measurement_out
#     assert_frame_equal(df, data_out)


# def test_measurement_math_add(dock_arcos_widget):
#     viewer, mywidget = dock_arcos_widget
#     df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_test_meas_math.csv")
#     df["Measurement_Ratio"] = df["Measurment"] + df["Measurment_2"]
#     columnpicker.measurement_math.value = "Add"
#     measurement_out, data_out = mywidget.calculate_measurment(
#         df, "Measurment", "Measurment_2"
#     )
#     assert "Measurement_Sum" == measurement_out
#     assert_frame_equal(df, data_out)


# def test_measurement_math_multiply(dock_arcos_widget):
#     viewer, mywidget = dock_arcos_widget
#     df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_test_meas_math.csv")
#     df["Measurement_Ratio"] = df["Measurment"] * df["Measurment_2"]
#     columnpicker.measurement_math.value = "Multiply"
#     measurement_out, data_out = mywidget.calculate_measurment(
#         df, "Measurment", "Measurment_2"
#     )
#     assert "Measurement_Product" == measurement_out
#     assert_frame_equal(df, data_out)


# def test_arcos_widget_no_data(dock_arcos_widget, capsys, qtbot):
#     viewer, mywidget = dock_arcos_widget
#     mywidget.filtered_data = pd.DataFrame()
#     viewer, mywidget = dock_arcos_widget
#     QTest.mouseClick(mywidget.update_arcos, Qt.LeftButton)
#     # capture output
#     catptured = capsys.readouterr()
#     # assert output
#     assert (
#         catptured.out
#         == "INFO: No Data Loaded, Use arcos_widget to load and filter data first\n"
#     )
#     viewer.close()


# def test_arcos_widget_data_active_cells(dock_arcos_widget, capsys, qtbot):
#     columnpicker.frame.choices = ["t"]
#     columnpicker.track_id.choices = ["id"]
#     columnpicker.x_coordinates.choices = ["x"]
#     columnpicker.y_coordinates.choices = ["y"]
#     columnpicker.z_coordinates.choices = ["None"]
#     columnpicker.measurment.choices = ["m"]
#     columnpicker.field_of_view_id.choices = ["Position"]
#     columnpicker.field_of_view_id.set_choice("None", "None")
#     columnpicker.z_coordinates.set_choice("None", "None")

#     columnpicker.frame.set_value = "t"
#     columnpicker.x_coordinates.value = "x"
#     columnpicker.y_coordinates.value = "y"
#     columnpicker.track_id.value = "id"
#     columnpicker.measurment.value = "m"
#     columnpicker.measurement_math.value = "None"
#     columnpicker.field_of_view_id.value = "Position"

#     viewer, mywidget = dock_arcos_widget

#     df = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
#     df = df[df["Position"] == 1]
#     mywidget.data = df
#     mywidget.filtered_data = mywidget.data
#     mywidget.close_columnpicker()

#     stored_variables.positions = [0, 1]
#     stored_variables.current_position = 0
#     mywidget.total_event_size.setValue(70)
#     mywidget.update_what_to_run_all()
#     QTest.mouseClick(mywidget.update_arcos, Qt.LeftButton)
#     # capture output
#     catptured = capsys.readouterr()
#     # assert output
#     assert (
#         catptured.out
#         == "INFO: No collective events detected, consider adjusting parameters\n"
#     )
#     assert viewer.layers[ARCOS_LAYERS["all_cells"]]
#     assert viewer.layers[ARCOS_LAYERS["all_cells"]]
#     viewer.close()


# def test_arcos_widget_data_all(dock_arcos_widget, capsys, qtbot):
#     viewer, mywidget = dock_arcos_widget
#     columnpicker.frame.choices = ["t"]
#     columnpicker.track_id.choices = ["id"]
#     columnpicker.x_coordinates.choices = ["x"]
#     columnpicker.y_coordinates.choices = ["y"]
#     columnpicker.z_coordinates.choices = ["None"]
#     columnpicker.measurment.choices = ["m"]
#     columnpicker.field_of_view_id.choices = ["Position"]
#     columnpicker.field_of_view_id.set_choice("None", "None")
#     columnpicker.z_coordinates.set_choice("None", "None")

#     columnpicker.frame.set_value = "t"
#     columnpicker.x_coordinates.value = "x"
#     columnpicker.y_coordinates.value = "y"
#     columnpicker.track_id.value = "id"
#     columnpicker.measurment.value = "m"
#     columnpicker.measurement_math.value = "None"
#     columnpicker.field_of_view_id.value = "Position"

#     mywidget.data = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
#     mywidget.filtered_data = pd.read_csv(
#         "src/arcos_gui/_tests/test_data/arcos_data.csv"
#     )

#     mywidget.close_columnpicker()
#     stored_variables.positions = [0, 1]
#     stored_variables.current_position = 0
#     mywidget.neighbourhood_size.setValue(5)
#     mywidget.total_event_size.setValue(5)
#     mywidget.update_what_to_run_all()
#     QTest.mouseClick(mywidget.update_arcos, Qt.LeftButton)
#     assert viewer.layers[ARCOS_LAYERS["all_cells"]]
#     assert viewer.layers[ARCOS_LAYERS["active_cells"]]
#     assert viewer.layers[ARCOS_LAYERS["collective_events_cells"]]
#     assert viewer.layers[ARCOS_LAYERS["event_hulls"]]
#     viewer.close()


# def test_toggle_biasmethod_visibility(dock_arcos_widget, qtbot):
#     viewer, mywidget = dock_arcos_widget
#     mywidget.bias_method.setCurrentText("runmed")
#     mywidget.bias_method.setCurrentText("lm")
#     mywidget.bias_method.setCurrentText("none")
#     viewer.close()


# def test_add_widget(make_napari_viewer):
#     viewer = make_napari_viewer()
#     num_dw = len(viewer.window._dock_widgets)
#     viewer.window.add_plugin_dock_widget(
#         plugin_name="arcos-gui", widget_name="ARCOS Main Widget"
#     )
#     assert len(viewer.window._dock_widgets) == num_dw + 1
#     viewer.close()


# def test_TimeSeriesPlots_widget(make_napari_viewer, qtbot):
#     viewer = make_napari_viewer()
#     num_dw = len(viewer.window._dock_widgets)
#     widget = viewer.window.add_plugin_dock_widget(
#         plugin_name="arcos-gui", widget_name="ARCOS Main Widget"
#     )
#     mywidget = widget[1]
#     plot = mywidget
#     mywidget.data = pd.read_csv("src/arcos_gui/_tests/test_data/arcos_data.csv")
#     mywidget.filtered_data = pd.read_csv(
#         "src/arcos_gui/_tests/test_data/arcos_data.csv"
#     )
#     columnpicker.frame.choices = ["t"]
#     columnpicker.track_id.choices = ["id"]
#     columnpicker.x_coordinates.choices = ["x"]
#     columnpicker.y_coordinates.choices = ["y"]
#     columnpicker.z_coordinates.choices = ["None"]
#     columnpicker.measurment.choices = ["m"]
#     columnpicker.field_of_view_id.choices = ["Position"]
#     columnpicker.field_of_view_id.set_choice("None", "None")
#     columnpicker.z_coordinates.set_choice("None", "None")

#     columnpicker.frame.set_value = "t"
#     columnpicker.x_coordinates.value = "x"
#     columnpicker.y_coordinates.value = "y"
#     columnpicker.track_id.value = "id"
#     columnpicker.measurment.value = "m"
#     columnpicker.measurement_math.value = "None"
#     columnpicker.field_of_view_id.value = "Position"
#     mywidget.close_columnpicker()

#     stored_variables.positions = [0, 1]
#     stored_variables.current_position = 0
#     mywidget.total_event_size.setValue(5)
#     mywidget.update_what_to_run_all()
#     QTest.mouseClick(mywidget.update_arcos, Qt.LeftButton)
#     plot._ts_plot_update()
#     plot.timeseriesplot.combo_box.setCurrentText("tracklength histogram")
#     plot._ts_plot_update()
#     plot.timeseriesplot.combo_box.setCurrentText("measurment density plot")
#     plot._ts_plot_update()
#     plot.timeseriesplot.combo_box.setCurrentText("x/t-plot")
#     plot._ts_plot_update()
#     plot.timeseriesplot.combo_box.setCurrentText("y/t-plot")

#     assert len(viewer.window._dock_widgets) == num_dw + 1
#     viewer.close()
