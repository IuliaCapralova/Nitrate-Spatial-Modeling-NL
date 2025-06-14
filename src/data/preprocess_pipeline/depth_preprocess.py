import pandas as pd
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
        cleaned_dfs = []

        for well_id, group in self._dataframe.groupby("Well_ID"):
            group = group.set_index("Date").sort_index()
            daily = group["Depth"].resample("1D").mean()
            interpolated = daily.interpolate(limit=5)

            # longest continuous valid segment
            valid = interpolated.notna()
            segment_id = (valid != valid.shift()).cumsum()
            segment_lengths = valid.groupby(segment_id).sum()
            longest_id = segment_lengths[valid.groupby(segment_id).first()].idxmax()

            mask = segment_id == longest_id
            longest_segment = interpolated[mask]

            # filter by min number of valid values
            if longest_segment.notna().sum() >= 100:
                subset = pd.DataFrame({
                    "Date": longest_segment.index,
                    "Depth": longest_segment.values,
                    "Well_ID": well_id
                })
                geometry = group["geometry"].iloc[0]  # assumes same geometry per well
                subset["geometry"] = geometry
                cleaned_dfs.append(subset)

        if cleaned_dfs:
            self._dataframe = pd.concat(cleaned_dfs).reset_index()
        else:
            self._dataframe = pd.DataFrame(columns=self._dataframe.columns)


    # def _date_round(self):
    #     self._dataframe['Date'] = self._dataframe['Date'].dt.floor('12h')


if __name__ == "__main__":
    province = "utrecht"
    well_filter = 1
    year_start = 2008
    year_end = 2023

    instance = Depth_Preprocess(province, well_filter, year_start=year_start, year_end=year_end)
    print(len(instance._dataframe))
