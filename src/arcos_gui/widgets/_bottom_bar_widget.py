from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy import QtWidgets
from qtpy.QtCore import QUrl
from qtpy.QtGui import QDesktopServices

if TYPE_CHECKING:
    from arcos_gui.processing import DataStorage


class BottomBarWidget(QtWidgets.QWidget):
    def __init__(self, data_storage_instance: DataStorage, parent=None):
        super().__init__(parent)
        self.data_storage_instance = data_storage_instance
        self.setupui()
        self._connect_signals()

    def setupui(self):
        self.bottom_bar_layout = QtWidgets.QHBoxLayout()
        self.collev_number_display_label = QtWidgets.QLabel(
            "Number of detected collective events: "
        )
        self.collev_number_display = QtWidgets.QLCDNumber()
        self.collev_number_display.setDigitCount(4)
        self.collev_number_display.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.arcos_help_button = QtWidgets.QPushButton("Open Documentation")
        self.bottom_bar_layout.addWidget(self.collev_number_display_label)
        self.bottom_bar_layout.addWidget(self.collev_number_display)
        self.bottom_bar_layout.addWidget(self.arcos_help_button)
        self.setLayout(self.bottom_bar_layout)

    def _connect_signals(self):
        self.data_storage_instance.arcos_stats.value_changed_connect(
            self.update_event_counter
        )
        self.arcos_help_button.clicked.connect(self._update_help_pressed)

    def update_event_counter(self):
        df = self.data_storage_instance.arcos_stats.value

        if df.empty:
            self.collev_number_display.display(0)
        else:
            collev_number = df["collid"].nunique()
            self.collev_number_display.display(collev_number)

    def _update_help_pressed(self):
        url = QUrl("https://bgraedel.github.io/arcos-gui/Usage/")
        QDesktopServices.openUrl(url)


if __name__ == "__main__":
    import sys

    from arcos_gui.processing import DataStorage  # noqa: F811

    app = QtWidgets.QApplication(sys.argv)
    ds = DataStorage()
    window = BottomBarWidget(ds)
    window.show()
    sys.exit(app.exec_())
