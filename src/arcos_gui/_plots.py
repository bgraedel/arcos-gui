import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from arcos4py.tools import calcCollevStats
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from napari.utils.notifications import show_info
from qtpy import QtWidgets
from scipy.stats import gaussian_kde


class CollevPlotter(QtWidgets.QWidget):
    """
    QWidget for plotting.
    Class to make a matplotlib figure canvas and add it to a Qwidget.
    Canvas, figure and axis objects can be acessed by self.canvas,
    self.fig and self.ax. This plots duration of Collective events over their size as
    returned by arcos.
    """

    def __init__(self, parent=None):
        """Initialise instance.
        :param viewer: Napari viewer instance
        :type viewer: napari.viewer.Viewer
        :param parent: Parent widget, optional
        :type parent: qtpy.QtWidgets.QWidget
        """
        super().__init__(parent)

        self.collid_name: str = "collid"
        self.nbr_collev: int = 0
        self._init_mpl_widgets()

    def _init_mpl_widgets(self):
        """
        Method to initialise a matplotlib figure canvas, to generate,
        set plot style and axis, and populate it with a matplotlib.figure.Figure.
        """
        # set up figure and axe objects
        with plt.style.context("dark_background"):
            plt.rcParams["figure.dpi"] = 110
            plt.rcParams["axes.edgecolor"] = "#ffffff"
            self.fig = Figure(figsize=(3, 2), tight_layout=True)
            self.canvas = FigureCanvas(self.fig)
            self.ax = self.fig.add_subplot(111)
            self.ax.scatter([], [])
            self.ax.set_xlabel("Total Size")
            self.ax.set_ylabel("Event Duration")
            self.canvas.figure.tight_layout()

        self.toolbar = NavigationToolbar(self.canvas, self)

        # construct layout
        self.layout_collevplot = QtWidgets.QVBoxLayout()
        self.layout_collevplot.addWidget(self.toolbar)
        self.layout_collevplot.addWidget(self.canvas)
        self.setLayout(self.layout_collevplot)
        self.setWindowTitle("Collective Events")

    def update_plot(self, columnpicker_widget, arcos_data):
        """
        Method to update the matplotlibl axis object self.ax with new values from
        the stored_variables object
        """
        arcos = arcos_data
        collev_stats = calcCollevStats()
        # if no calculation was run so far (i.e. when the widget is initialized)
        # populate it with no data
        if arcos.empty:
            stats = pd.DataFrame(data={"tot_size": [], "duration": []})
        else:
            stats = collev_stats.calculate(
                arcos, columnpicker_widget.frame.value, self.collid_name
            )
        self.ax.cla()
        self.ax.spines["bottom"].set_color("white")
        self.ax.spines["top"].set_color("white")
        self.ax.spines["right"].set_color("white")
        self.ax.spines["left"].set_color("white")
        self.ax.xaxis.label.set_color("white")
        self.ax.yaxis.label.set_color("white")
        self.ax.tick_params(colors="white", which="both")
        self.ax.axis("on")
        stats = stats[["tot_size", "duration"]]
        self.ax.scatter(stats[["tot_size"]], stats[["duration"]], alpha=0.8)
        self.ax.set_xlabel("Total Size")
        self.ax.set_ylabel("Event Duration")
        self.fig.canvas.draw_idle()
        self.nbr_collev = stats.shape[0]


class TimeSeriesPlots(QtWidgets.QWidget):
    """
    QWidget for plotting.
    Class to make a matplotlib figure canvas and add it to a Qwidget.
    Canvas, figure and axis objects can be acessed by self.canvas, self.fig and self.ax.
    This plots several different Timeseries plots such as Position/t plots,
    tracklength histogram and a measurment density plot.
    """

    def __init__(self, parent=None):
        """
        Initialise instance.
        :param viewer: Napari viewer instance
        :type viewer: napari.viewer.Viewer
        :param parent: Parent widget, optional
        :type parent: qtpy.QtWidgets.QWidget
        """
        super().__init__(parent)
        # available plots
        self.plot_list = [
            "tracklength histogram",
            "measurment density plot",
            "x/t-plot",
            "y/t-plot",
        ]
        self._init_widgets()

    def _init_widgets(self):
        """
        Method to initialise a matplotlib figure canvas as well as a spinbox,
        Button and label widgets. Additionally, generates a
        matplotlib.backends.backend_qt5agg.FigureCanvas, a set plot style and axis,
        and populates it with a matplotlib.figure.Figure.
        These are the added to a QVboxlayout.
        """
        # creating spinbox widget
        self.sample_number = QtWidgets.QSpinBox()
        self.sample_number.setMinimum(1)
        self.sample_number.setMaximum(200)
        self.sample_number.setValue(20)

        self.button = QtWidgets.QPushButton("Update Plot")

        # label
        self.spinbox_title = QtWidgets.QLabel("Sample Size")
        self.spinbox_title.setVisible(False)

        # creating a combo box widget
        self.combo_box = QtWidgets.QComboBox(self)
        self.combo_box.addItems(self.plot_list)
        # self.combo_box.currentIndexChanged.connect(self.update_plot)

        # set up figure and axe objects
        with plt.style.context("dark_background"):
            plt.rcParams["figure.dpi"] = 110
            plt.rcParams["axes.edgecolor"] = "#ffffff"
            self.fig = Figure(figsize=(3, 2), tight_layout=True)
            self.canvas = FigureCanvas(self.fig)
            self.ax = self.fig.add_subplot(111)
            self.ax.scatter([], [])
            self.ax.set_xlabel("X Axis")
            self.ax.set_ylabel("Y Axis")
            self.canvas.figure.tight_layout()

        self.toolbar = NavigationToolbar(self.canvas, self)

        # construct layout
        layout = QtWidgets.QVBoxLayout()
        layout_combobox = QtWidgets.QVBoxLayout()
        layout_spinbox = QtWidgets.QHBoxLayout()

        # add widgets to sub_layouts
        layout_combobox.addWidget(self.button)
        layout_combobox.addWidget(self.combo_box)
        layout_spinbox.addWidget(self.spinbox_title)
        layout_spinbox.addWidget(self.sample_number)

        # add sublayouts together
        layout.addWidget(self.toolbar)
        layout.addLayout(layout_combobox)
        layout.addLayout(layout_spinbox)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.setWindowTitle("Collective Events")

    def update_plot(self, columnpicker_widget, dataframe: pd.DataFrame):
        """
        Method to update the from the dropdown menu chosen
        matplotlibl plot with values from
        the stored_variables object dataframe.
        """
        # return plottype that should be plotted
        plottype = self.combo_box.currentText()
        # sample number for position/t-plots
        n = self.sample_number.value()

        # get column values and dataframe
        frame = columnpicker_widget.frame.value
        track_id = columnpicker_widget.track_id.value
        x_coordinates = columnpicker_widget.x_coordinates.value
        y_coordinates = columnpicker_widget.y_coordinates.value
        measurement = columnpicker_widget.measurment.value

        # check if some data was loaded already, otherwise do nothing
        if not dataframe.empty:
            self.ax.cla()
            self.ax.spines["bottom"].set_color("white")
            self.ax.spines["top"].set_color("white")
            self.ax.spines["right"].set_color("white")
            self.ax.spines["left"].set_color("white")
            self.ax.xaxis.label.set_color("white")
            self.ax.yaxis.label.set_color("white")
            self.ax.tick_params(colors="white", which="both")
            self.ax.axis("on")

            # tracklength histogram
            if plottype == "tracklength histogram":
                self.sample_number.setVisible(False)
                self.spinbox_title.setVisible(False)
                track_length = dataframe.groupby(track_id).size()
                self.ax.hist(track_length)
                self.ax.set_xlabel("tracklength")
                self.ax.set_ylabel("counts")

            # measurment density plot, kde
            elif plottype == "measurment density plot":
                self.sample_number.setVisible(False)
                self.spinbox_title.setVisible(False)
                density = gaussian_kde(dataframe[measurement].interpolate())
                x = np.linspace(
                    min(dataframe[measurement]),
                    max(dataframe[measurement]),
                    100,
                )
                y = density(x)
                self.ax.plot(x, y)
                self.ax.set_xlabel("measurement values")
                self.ax.set_ylabel("density")

            # xy/t plots
            elif plottype == "x/t-plot":
                self.sample_number.setVisible(True)
                self.spinbox_title.setVisible(True)
                sample = pd.Series(dataframe[track_id].unique()).sample(n, replace=True)
                pd_from_r_df = dataframe.loc[dataframe[track_id].isin(sample)]
                df_grp = pd_from_r_df.groupby(track_id)
                for label, df in df_grp:
                    self.ax.plot(df[frame], df[x_coordinates])
                self.ax.set_xlabel("Frame")
                self.ax.set_ylabel("Position X")

            elif plottype == "y/t-plot":
                self.sample_number.setVisible(True)
                self.spinbox_title.setVisible(True)
                sample = pd.Series(dataframe[track_id].unique()).sample(n, replace=True)
                pd_from_r_df = dataframe.loc[dataframe[track_id].isin(sample)]
                df_grp = pd_from_r_df.groupby(track_id)
                for label, df in df_grp:
                    self.ax.plot(df[frame], df[y_coordinates])
                self.ax.set_xlabel("Frame")
                self.ax.set_ylabel("Position Y")
            self.fig.canvas.draw_idle()
        else:
            show_info("No Data to plot")
