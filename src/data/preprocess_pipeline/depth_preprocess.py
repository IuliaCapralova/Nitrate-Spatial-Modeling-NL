import pandas as pd
try:
    from .timeseries_preprocess import TimeseriesPreprocess
except ImportError:
    from timeseries_preprocess import TimeseriesPreprocess


class Depth_Preprocess(TimeseriesPreprocess):
    
    def __init__(self, province:list[str], well_filter, year_start = 2008, year_end = 2023) -> None:
        super().__init__(province, well_filter, year_start, year_end, type_of_data="well_depth_data")

    def _filter_columns(self):
        columns = ["Well_ID", "BRO-ID", "Filter", "Date", "Depth", "geometry"]
        self._data = self._data[columns].copy()

    def _handle_missing_values(self):
        self._data = self._data.drop_duplicates(subset=["Well_ID", "BRO-ID", "Filter", "Date", "geometry"], keep="first")
        
    def _well_selection(self):
        cleaned_dfs = []

        for well_id, group in self._data.groupby("Well_ID"):
            group = group.set_index("Date").sort_index()
            daily = group["Depth"].resample("1D").mean()
            interpolated = daily.interpolate(limit=5)

            # longest continuous valid segment
            valid = interpolated.notna()
            segment_id = (valid != valid.shift()).cumsum()
            segment_lengths = valid.groupby(segment_id).sum()

            valid_segments = segment_lengths[valid.groupby(segment_id).first()]

            if not valid_segments.empty:
                # longest_id = segment_lengths[valid.groupby(segment_id).first()].idxmax()
                longest_id = valid_segments.idxmax()
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
            self._data = pd.concat(cleaned_dfs).reset_index()
        else:
            self._data = pd.DataFrame(columns=self._data.columns)


    # def _date_round(self):
    #     self._dataframe['Date'] = self._dataframe['Date'].dt.floor('12h')


if __name__ == "__main__":
    provinces = ["utrecht", "flevoland"]
    well_filter = 1
    year_start = 2008
    year_end = 2009

    instance = Depth_Preprocess(provinces, well_filter, year_start=year_start, year_end=year_end)
    print(len(instance.dataframe["flevoland"]))
