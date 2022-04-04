# Welcome to Arcos-GUI

Arcos-GUI is a plugin that allows users to use the ARCOS algorithm inside napari.

**A**utomated **R**ecognition of **C**ollective **S**ignalling (ARCOS) is an R package to identify collective spatial events in time series data,
that was written by Maciej Dobrzynski (https://github.com/dmattek).
ARCOS can identify and visualize collective protein activation in 2- and 3D cell cultures over time.

This plugin relies on this algorithm and integrates it into a napari plugin. Therefore, it allows users to import tracked time-series data in CSV format and provides
the necessary GUI elements to process this data with the ARCOS algorithm. The plugin adds several layers to the viewer to visually inspect the detected events. Based on that, fine-tune the parameters used by ARCOS.

Following analysis, the user can export the output as a CSV file with the detected collective events or as a sequence of images to generate a movie.

# Installation

To use this plugin, first install napari with:

```
pip install napari[all]
```
It is better to do this in a newly created virtual environment such as an anaconda/miniconda to avoid dependency issues.

After successfully installing napari, you can install this plugin with:

```
pip install arcos-gui
```

## System Requirements

Since version "0.0.2" this plugin is python native with the arcos4py package available.
