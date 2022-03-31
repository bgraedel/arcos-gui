# Welcome to arcos-gui

This is a plugin that allows users to interact with the R ARCOS libary inside of napari.

**A**utomated **R**ecognition of **C**ollective **S**ignalling (ARCOS) is an R package to identify collective spatial events in time series data,
that was written by Maciej Dobrzynski (https://github.com/dmattek).
The software identifies and visualises collective protein activation in 2- and 3D cell cultures over time.

This plugin relies on this library and integrates it into a napari plugin. Threfore it allows users to import tracked timeseries data in csv format and provides
the necessary gui elements to process this data with the ARCOS libary. It then plots it's results and adds several layers to the viewer that
allow users to visually inspect the detected events and based on that fine-tune that parameters used by ARCOS.

Following analysis the user can export the output in form of a csv file with the detected collective events or as a sequence of Images that can be transformed into a movie.

# Installation

This plugin relies on a rpy2, a libary for running R functions inside of python. Since this libary officially only supports Unix based systems this plugin does likewise only support unix based systems such as linux and mac os.

## Windows

Installation on Windows is still possible by adding the R binary to
system-environment variable windows before installing rpy2 (or the plugin directly).

## System Requirements

To use this plugin, it is reccomended to setup a fresh virtual enviroment, as can be done with e.g. miniconda. Before procceding with the installation of this plugin a working R installation with the ARCOS plugin (https://github.com/dmattek/ARCOS) is also required.

Once done, this package can be installed either by downloading it directly from github or by installing it with

pip install arcos-gui.
