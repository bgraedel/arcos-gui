# Usage

The following section shows how to use arcos-gui.

## Open Main Widget, Load Data, and run ARCOS

#### Open Widget
1. Make sure the arcos-gui and napari are installed.
2. Open napari and dock the ARCOS main widget:

![load_plugin](screenshots/load_plugin.png){ width="500" }


#### Load Data
3. Load and filter the data:

    a. Open file browser and select comma-delimited CSV file in long format.

    b. Load CSV file.

    c. In the popup dialogue, select columns corresponding to the indicated label. For Z-coordinates and Position can be None if this column does not exist.

    d. Filter input data. Parameters can be used to select track length, rescale frame interval and rescale measurement.

![load_and_filter](screenshots/load_filter.png){ width="300" } ![columnpicker](screenshots/select_from_dropdown.png){ width="150" }


#### Run ARCOS
4. Select ARCOS parameters and run the algorithm.

    a. Change ARCOS parameters, see the [ARCOS parameters](#arcos-parameters) section for in detail explanation.

    b. Update ARCOS. Will run the algorithm and generate layers.

![arcos_parameters](screenshots/select_arcos_parameters.png){ width="400" }

## Generated Layers

![collective_events](screenshots/collev_.png){ width="600" }

- a. Detected collective event with its convex hull.

- b. Generated layers are:

    1. all_cells: centroid of cells with the color code representing the measurement.
    2. active cells: points represent active cells according to binarization
    3. coll cells: cross marking cells that are part of a collective event
    4. coll event: the convex hull of collective events

## Other Widgets

### Exporting Data
![export_data](screenshots/data_export.png){ width="400" }

#### Export CSV file
The data generated by Arcos can be exported as a CSV file using the Export data widget.
Can be docked in the same way as the main widget.

![export_csv_dialog](screenshots/export_csv.png){ width="400" }

#### Export Image sequence
Images of the viewer can be exported using the Export Movie button.
The option automatically determines the correct viewer size and will try to automatically fit the data into the viewer.

![export_image_sequence_dialog](screenshots/export_image_sequence.png){ width="400" }

### Timestamp
Timestamps can be added with the Timestamp widget. Can be loaded just as the main widget.

![add_timestamp](screenshots/add_timestamp.png){ width="400" }

#### Timestamp options
Options can be set using the Timestamp Options dialogue

![timestamp_options_dialog](screenshots/timestamp_options.png){ width="200" }

## ARCOS parameters

### Measurement
| Parameters               | Description                                                                                                        |
|--------------------------|--------------------------------------------------------------------------------------------------------------------|
| Interpolate Measurements | If the tickbox is checked, missing values are<br /> interpolated across all columns in the input data                       |
| Clip Measurements        | if the tickbox is checked, the measurement will be clipped<br />according to the quantiles provided in clip low and clip high |
| Clip Low                 | appears if clip measurements is checked                                                                            |
| Clip High                | appears if clip measurements is checked                                                                            |

### Binarization

| Parameter                 | Description                                                                                         |
|---------------------------|-----------------------------------------------------------------------------------------------------|
| Bias Method               | Choose de-trending method, <br>can be runmed, lm or none                                     |
| Smooth K                  | Size of the short-term median smoothing filter.                                                         |
| Bias K                    | Available if Bias Method is set to 'runmed', <br>size of long term median smoothing filter          |
| polyDeg                   | Available if Bias Method is set to 'lm',<br>sets the degree of the polynomial for regression detrending |
| Bin Peak Threshold        | Threshold for rescaling of the de-trended signal.                                                   |

First, a short-term median filter with size smoothK is applied to remove fast noise from the time series. If the de-trending method is set to "none", smoothing is applied on globally rescaled time series. The subsequent de-trending can be performed with a long-term median filter with the size biasK {biasMet = "runmed"} or by fitting a polynomial of degree polyDeg {biasMet = "lm"}.
After de-trending, if the global difference between min/max is greater than the threshold the signal is rescaled to the (0,1) range. The final signal is binarised using the binThr threshold parameter.

### Collective Event Detection

| Parameter          | Description                                                                                                                                                                                                                                                     |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Neighbourhood Size | The maximum distance between two samples for one to be considered<br>as in the neighbourhood of the other. This is not a maximum bound <br>on the distances of points within a cluster. <br>Value is also used to connect collective events across multiple frames. |
| Min Clustersize    | Minimum size for a cluster to be identified as a collective event.                                                                                                                                                                                              |

### Filter Collective Events

| Parameter        | Description                                           |
|------------------|-------------------------------------------------------|
| Min Duration     | Minimal duration of collective events to be selected. |
| Total Event Size | Minimal total event size.                             |


## Plots
Under the main widgets plotting tab, several types of plots can be found that describe the time-series data and collective events.

![plots](screenshots/plots.png){ width="400" }

### Time-series statistics
These plots help to choose appropriate parameters for Arcos and track length filtering.
Available plots are:

- Track length Histogram
- Measurement Density plot (kde)
- X-T and Y-T plot

### Collective Event statistics
This plot shows collective event duration over collective event size.