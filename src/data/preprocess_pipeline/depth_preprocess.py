from .timeseries_preprocess import TimeseriesPreprocess


class Depth_Preprocess(TimeseriesPreprocess):
    
    def __init__(self, province, well_filter, year_start = 2012, year_end = 2020) -> None:
        super().__init__(province, well_filter, year_start, year_end, type_of_data="well_depth_data")

    def _filter_columns(self):
        columns = ["Well_ID", "BRO-ID", "Filter", "Date", "Depth", "geometry"]
        self._dataframe = self._dataframe[columns].copy()

    def _handle_missing_values(self):
        self._dataframe = self._dataframe.drop_duplicates(subset=["Well_ID", "BRO-ID", "Filter", "Date", "geometry"], keep="first")
        
    def _well_selection(self):

        self._dataframe['Delta_Days'] = self._dataframe.groupby('Well_ID')['Date'].diff().dt.total_seconds() / (60 * 60 * 24)
        df_clean = self._dataframe.dropna(subset=['Delta_Days'])
        stats_per_well = df_clean.groupby('Well_ID')['Delta_Days'].agg(['mean', 'std'])
        constant_wells = stats_per_well[(stats_per_well['std'] == 0) & (stats_per_well['mean'] == 0.5)].index.tolist()
        constant_wells = set(constant_wells)

        self._dataframe = self._dataframe[self._dataframe["Well_ID"].isin(constant_wells)]

    def _date_round(self):
        self._dataframe['Date'] = self._dataframe['Date'].dt.floor('12h')


if __name__ == "__main__":
    province = "utrecht"
    well_filter = 1
    year_start = 2012
    year_end = 2020

    instance = Depth_Preprocess(province, well_filter, year_start=year_start, year_end=year_end)
    print(len(instance._dataframe))
