try:
    from .timeseries_preprocess import TimeseriesPreprocess
except ImportError:
    from timeseries_preprocess import TimeseriesPreprocess


class Nitrate_Preprocess(TimeseriesPreprocess):
    
    def __init__(self, provinces:list[str], well_filter, year_start = 2008, year_end = 2023) -> None:
        super().__init__(provinces, well_filter, year_start, year_end,type_of_data="well_chem_data")

    def _filter_columns(self):
        columns = ["Well_ID", "BRO-ID", "Filter", "Date", "Nitrate", "geometry"]
        self._data = self._data[columns].copy()

    def _handle_missing_values(self):
        # Drop rows with any NaNs in Niterate column
        self._data = self._data.dropna(subset=["Nitrate"])

    def _rename_cols(self):
        self._data.rename(columns={"BRO-ID":"bro-id", "Date": "date", "Nitrate": "nitrate"}, inplace=True)


if __name__ == "__main__":
    provinces = ["utrecht", "flevoland"]
    well_filter = 1
    instance = Nitrate_Preprocess(provinces, well_filter)
    # print(len(instance._dataframe))
    print(instance.dataframe)

    # cols = ['nitrate', 'geometry', 'date']
    # print(instance.get_variable(cols))
