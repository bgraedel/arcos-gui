"""
It implements the "sample data" specification.
see: https://napari.org/plugins/stable/guides.html#sample-data

"""
from __future__ import annotations

from pathlib import Path

from arcos_gui._arcos_widgets import MainWindow


def load_sample_data():
    """Load sample data into stored_variables"""
    MainWindow.file_LineEdit.setText(
        Path("src/arcos_gui/_tests/test_data/arcos_data.csv")
    )
    return []
