import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas


from qtpy.QtCore import Signal
from qtpy.QtWidgets import QPushButton, QWidget, QVBoxLayout, QDialog, QComboBox, QHBoxLayout, QLabel,  QSpinBox


class TimeSeriesPlots(QWidget):
    """QWidget for plotting.
    This class generates a matplotlib figure canvas and binds it into a QWidget. The canvas and artists are accessible
    by the attributes self.canvas, self.fig and self.ax.
    """
    def __init__(self, napari_viewer, parent=None):
        """Initialise instance.
        :param napari_viewer: Napari viewer instance, input should be handled by the napari_hook_implementation decoration
        :type napari_viewer: napari.viewer.Viewer
        :param parent: Parent widget, optional
        :type parent: qtpy.QtWidgets.QWidget
        """
        super(TimeSeriesPlots, self).__init__(parent)
        self.viewer = napari_viewer
        self._init_mpl_widgets()

        num_points_container = QWidget()
        num_points_container.setLayout(QHBoxLayout())
        lbl = QLabel("Choose Plot")
        num_points_container.layout().addWidget(lbl)

        self.plot_list = ["tracklength histogram", 'measurment density plot', 'x/t-plot', 'y/t-plot']
        plot_choice = SelectDeviceFromCombobox(self.plot_list)
        plot_choice._on_change(self.update_plot)
        num_points_container.layout().addWidget(plot_choice)
        self._sp_num_points = QSpinBox()
        self._sp_num_points.setMinimum(1)
        self._sp_num_points.setMaximum(200)
        self._sp_num_points.setValue(100)
        num_points_container.layout().addWidget(self._sp_num_points)
        num_points_container.layout().setSpacing(0)
        self.layout().addWidget(num_points_container)


        # connect callbacks
        # self.sync.signal.connect(self._update_layer_selection)
        self.viewer.layers.events.inserted.connect(self.update_plot)
        self.viewer.layers.events.removed.connect(self.update_plot)

    def _init_mpl_widgets(self):
        """Method to initialise a matplotlib figure canvas.
        This method generates a matplotlib.backends.backend_qt5agg.FigureCanvas and populates it with a
        matplotlib.figure.Figure and further matplotlib artists. The canvas is added to a QVBoxLayout afterwards.
        """
        # set up figure and axe objects
        with plt.style.context('dark_background'):
            plt.rcParams['figure.dpi'] = 110
            plt.rcParams['axes.edgecolor'] = '#ffffff'
            self.fig = Figure(figsize = (3,2))
            self.canvas = FigureCanvas(self.fig)
            self.ax = self.fig.add_subplot(111)
            self.ax.scatter([],[])
            self.ax.set_xlabel("Total Size")
            self.ax.set_ylabel("Event Duration")       
            self.canvas.figure.tight_layout()

        # construct layout
        layout = QVBoxLayout()
        # layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.setWindowTitle('Collective Events')

    def update_plot(self, plottype):
        dataframe = stored_variables.get_dataframe(), columnpicker.dicCols.value
        n = self._sp_num_points.value
        columns = columnpicker.dicCols.value

        self.ax.cla()
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white') 
        self.ax.spines['right'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.tick_params(colors='white', which='both')
        self.ax.axis('on')

    # tracklength histogram
        if plottype == 'tracklength histogram':
            track_length = dataframe.groupby(columns['track_id']).size()
            self.ax.hist(track_length)
            self.ax.set_xlabel("tracklength")
            self.ax.set_ylabel("counts")  

    # measurment density plot, kde
        elif plottype == 'measurment density plot':
            density = kde.gaussian_kde(dataframe[columns['measurment']].interpolate())
            x = np.linspace(min(dataframe[columns['measurment']]),max(dataframe[columns['measurment']]), 100)
            y=density(x)
            self.ax.plot(x,y)
            self.ax.set_xlabel("measurement values")
            self.ax.set_ylabel("density")  

    # xy/t plots
        elif plottype == 'x/t-plot':
            sample = pd.Series(dataframe[columns['track_id']].unique()).sample(n)
            pd_from_r_df = dataframe.loc[dataframe[columns['track_id']].isin(sample)]
            for label, df in pd_from_r_df.groupby(columns['track_id']):
                self.ax.plot(df[columns['frame']], df[columns['x_coordinates']])
            self.ax.set_xlabel("Frame")
            self.ax.set_ylabel("Position X")    

        elif plottype == 'y/t-plot':
            sample = pd.Series(dataframe[columns['track_id']].unique()).sample(n)
            pd_from_r_df = dataframe.loc[dataframe[columns['track_id']].isin(sample)]
            for label, df in pd_from_r_df.groupby(columns['track_id']):
                self.ax.plot(df[columns['frame']], df[columns['y_coordinates']])
            self.ax.set_xlabel("Frame")
            self.ax.set_ylabel("Position Y")
        self.fig.canvas.draw_idle()  

class SelectDeviceFromCombobox(QDialog):
    val_changed = Signal(str)

    def __init__(self, obj_dev: list, label: str, parent=None):
        super().__init__(parent)

        self.setLayout(QHBoxLayout())
        self.label = QLabel()
        self.label.setText(label)
        self.combobox = QComboBox()
        self.combobox.addItems(obj_dev)
        self.button = QPushButton("Set")
        self.button.clicked.connect(self._on_click)

        self.layout().addWidget(self.label)
        self.layout().addWidget(self.combobox)
        self.layout().addWidget(self.button)

    def _on_click(self):
        self.val_changed.emit(self.combobox.currentText())