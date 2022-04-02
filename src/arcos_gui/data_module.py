import pandas as pd


class process_input:
    def __init__(
        self,
        field_of_view_column: str,
        frame_column: str,
        pos_columns: list,
        track_id_column: str,
        measurement_column: str,
        csv_file=None,
        df=None,
    ):

        self.field_of_view_column = field_of_view_column
        self.frame_column = frame_column
        self.pos_columns = pos_columns
        self.track_id_column = track_id_column
        self.measurment_column = measurement_column
        self.track_id_column = track_id_column

        if df is not None:
            self.df = df
        else:
            self.csv_file = csv_file
            self.df = None

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
                self.df.loc[:, self.field_of_view_column] == fov_to_select
            ].copy(deep=True)
        if return_dataframe:
            return self.df

        # filter_tracklenght works only if previously filtered by pos
        # or if track_ids dont overlapp between fov

    def filter_tracklength(self, min, max, return_dataframe=False):
        track_length = self.df.groupby(self.track_id_column).size()
        track_length_filtered = track_length.between(min, max)
        track_length_filtered_names = track_length_filtered[track_length_filtered].index
        self.df = self.df.loc[
            self.df.loc[:, self.track_id_column].isin(track_length_filtered_names)
        ].copy(deep=True)
        if return_dataframe:
            return self.df

    def rescale_measurment(self, rescale_factor: int, return_dataframe=False):
        """
        rescales measurment column by factor passed in as argument
        """
        self.df[self.measurment_column] = (
            rescale_factor * self.df[self.measurment_column]
        )
        if return_dataframe:
            return self.df

    def frame_interval(self, factor):
        if factor > 1:
            self.df[self.frame_column] = self.df[self.frame_column] / factor

    def return_pd_df(self):
        return self.df
