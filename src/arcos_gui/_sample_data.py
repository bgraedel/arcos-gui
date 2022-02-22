"""
It implements the "sample data" specification.
see: https://napari.org/plugins/stable/guides.html#sample-data

"""
from __future__ import annotations

from pathlib import Path

from arcos_gui._arcos_widgets import stored_variables


def load_sample_data():
    """Load sample data into stored_variables"""
    stored_variables.filename_for_sample_data = str(
        Path("arcos_gui/sample_data/arcos_data.csv")
    )
    return []
