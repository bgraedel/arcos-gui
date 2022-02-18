import logging

import pandas as pd
import rpy2.robjects as ro
from rpy2.rinterface_lib.callbacks import logger as rpy2_logger
from rpy2.robjects import pandas2ri
from rpy2.robjects.lib.dplyr import filter
from rpy2.robjects.packages import importr

r_base = importr("base")
datatable = importr("data.table")
arcos = importr("ARCOS")
rpy2_logger.setLevel(logging.ERROR)


class WrongColumnsSpecified(Exception):
    "wrong column specified"


class ARCOS:
    """
    class to calculate collective events with arcos algroithm.
    requires r installation and the r packages arcos and data.table
    column argument requires a dictionarry of columns:
    "frame","x_coordinates","y_coordinates","track_id", "measurment", 'field_of_view_id'
    e.g.
    dicCols = {
        'frame': frame,
        'x_coordinates': x_coordinates,
        'y_coordinates': y_coordinates,
        'track_id': track_id,
        'measurment': measurment,
        'field_of_view_id': field_of_view_id
        }
    required python packages are: rpy2, pandas, seaborn, matplotlib
    """

    def __init__(self, dataframe, columns: dict):
        self.dataframe = dataframe
        self.datatable = None
        self.ts = None
        self.columns = columns
        self.tcollsel = None

        if not all(
            key in self.columns
            for key in [
                "frame",
                "x_coordinates",
                "y_coordinates",
                "track_id",
                "measurment",
                "field_of_view_id",
            ]
        ):
            print(
                "not all required keys are in the dict, requires: \n \
                'frame','x_coordinates','y_coordinates','track_id',  \
                'measurment', 'field_of_view_id'"
            )
            raise WrongColumnsSpecified("dic requires specific column names")

    def __str__(self):
        """
        string method to print r datatable
        """
        return f"{self.datatable}"

    def create_arcosTS(self, interval=1, inter_type="fixed", return_dataframe=False):
        """
        method to create an arcos object.
        returns pandas dataframe if return_dataframe = True
        """
        with ro.conversion.localconverter(ro.default_converter + pandas2ri.converter):
            self.datatable = ro.conversion.py2rpy(self.dataframe)
        self.datatable = datatable.as_data_table(self.datatable)

        lista = ro.vectors.ListVector(
            {"Frame": self.columns["frame"], "IDobj": self.columns["track_id"]}
        )
        pos_variables_r = ro.StrVector(
            [self.columns["x_coordinates"], self.columns["y_coordinates"]]
        )

        self.datatable = arcos.arcosTS(
            self.datatable,
            colPos=pos_variables_r,
            colMeas=self.columns["measurment"],
            col=lista,
            interVal=interval,
            interType=inter_type,
        )

        if return_dataframe:
            return self.convert_to_pd(self.datatable)

    def interpolate_measurements(self, return_dataframe=False):
        """
        interpolates missing measurements of meas column
        """
        self.datatable = arcos.interpolMeas(self.datatable)
        if return_dataframe:
            return self.convert_to_pd(self.datatable)

    def clip_measurements(
        self, clip_low=0.001, clip_high=0.999, return_dataframe=False
    ):
        """
        clips measurements base on quantilles
        """
        meas_clip = ro.FloatVector([clip_low, clip_high])
        self.datatable = arcos.clipMeas(self.datatable, meas_clip, quant=True)
        if return_dataframe:
            return self.convert_to_pd(self.datatable)

    def bin_measurements(
        self,
        biasmethod="runmed",
        smooth_k=1,
        bias_k=25,
        peak_thr=0.2,
        bin_thr=0.1,
        polyDeg=1,
        return_dataframe=False,
    ):
        """
        binarizes measurements
        """
        self.datatable = arcos.binMeas(
            self.datatable,
            biasMet=biasmethod,
            smoothK=smooth_k,
            biasK=bias_k,
            polyDeg=polyDeg,
            peakThr=peak_thr,
            binThr=bin_thr,
        )
        if return_dataframe:
            return self.convert_to_pd(self.datatable)

    def track_events(
        self, neighbourhood_size=40, min_clustersize=5, return_dataframe=False
    ):
        """
        method to track collective events of an arcos object.
        can return pandas dataframe
        """
        self.ts = self.datatable
        self.ts = arcos.trackColl(
            filter(self.ts, self.ts.rx2("meas.bin").ro > 0),
            eps=neighbourhood_size,
            minClSz=min_clustersize,
        )
        if return_dataframe:
            return self.convert_to_pd(self.ts)

    def filter_tracked_events(
        self, min_duration=3, total_event_size=30, as_pd_dataframe=False
    ):
        """
        filters tracked events, either returns r object Dataframe or pandas dataframe
        """
        min_max_duration = ro.IntVector([min_duration, 1000])
        tot_event_size = ro.IntVector([total_event_size, 1000])
        self.tcollsel = arcos.selColl(
            self.ts, colldur=min_max_duration, colltotsz=tot_event_size
        )
        if as_pd_dataframe:
            return self.convert_to_pd(self.tcollsel)
        else:
            return self.tcollsel

    def calculate_stats(self):
        """
        calculates statistics for plotting of number of collective events
        """
        datatable = arcos.calcStatsColl(self.tcollsel)
        return self.convert_to_pd(datatable)

    def convert_to_pd(self, datatable):
        """
        method to convert a r object dataframe to a pandas dataframe
        """
        with ro.conversion.localconverter(ro.default_converter + pandas2ri.converter):
            pd_from_r_df = ro.conversion.rpy2py(datatable)
        return pd_from_r_df


class process_input:
    def __init__(self, columns: dict, csv_file=None, df=None):
        if df is not None:
            self.df = df
        else:
            self.csv_file = csv_file
            self.df = None

        self.columns = columns
        if not all(
            [
                key in self.columns
                for key in [
                    "frame",
                    "x_coordinates",
                    "y_coordinates",
                    "track_id",
                    "measurment",
                    "field_of_view_id",
                ]
            ]
        ):
            print(
                "not all required keys are in the dict, requires: \n  \
                'frame','x_coordinates','y_coordinates','track_id',  \
                'measurment', 'field_of_view_id'"
            )
            raise WrongColumnsSpecified("dic requires specific column names")

    def read_csv(self, return_dataframe=False):
        """
        read csv, returns pandas dataframe if return_dataframe = True
        """
        self.df = pd.read_csv(self.csv_file)
        if return_dataframe:
            return self.df

    def filter_position(self, fov_to_select=None, return_dataframe=False):
        if fov_to_select is not None:
            self.df = self.df.loc[
                self.df.loc[:, self.columns["field_of_view_id"]] == fov_to_select
            ].copy(deep=True)
        if return_dataframe:
            return self.df

        # filter_tracklenght works only if previously filtered by pos
        # or if track_ids dont overlapp between fov

    def filter_tracklength(self, min, max, return_dataframe=False):
        track_length = self.df.groupby(self.columns["track_id"]).size()
        track_length_filtered = track_length.between(min, max)
        track_length_filtered_names = track_length_filtered[track_length_filtered].index
        self.df = self.df.loc[
            self.df.loc[:, self.columns["track_id"]].isin(track_length_filtered_names)
        ].copy(deep=True)
        if return_dataframe:
            return self.df

    def rescale_measurment(self, rescale_factor: int, return_dataframe=False):
        """
        rescales measurment column by factor passed in as argument
        """
        meas_col = self.columns["measurment"]
        self.df[meas_col] = rescale_factor * self.df[meas_col]
        if return_dataframe:
            return self.df

    def frame_interval(self, factor):
        if factor > 1:
            self.df[self.columns["frame"]] = self.df[self.columns["frame"]] / factor

    def return_pd_df(self):
        return self.df
