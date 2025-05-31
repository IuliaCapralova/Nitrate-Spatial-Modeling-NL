import os
import pandas as pd
import geopandas as gpd
from shapely import wkt
from dataset import Dataset_Preprocess
from typing import Union, List
from abc import ABC, abstractmethod


class TimeseriesPreprocess(Dataset_Preprocess):
    
    def __init__(self, province, well_filter, year_start, year_end, type_of_data) -> None:
        super().__init__(type_of_data)
        self.year_start = year_start
        self.year_end = year_end
        self.province = province

        if well_filter not in [1,2,3]:
            print("We are interested only in filter 1, 2, and 3.")
        else:
            self.filter = well_filter

        if type_of_data == "well_depth_data":
            variable = "depth"
        elif type_of_data == "well_chem_data":
            variable = "chem"
        else:
            raise ValueError(f"Unknown type_of_data: {type_of_data}")

        self._file_path = os.path.join(self._datasetdir, f"{self.province}_well_{variable}_combined.csv")
        file = pd.read_csv(self._file_path)
        self._dataframe = file

        self._df_selection()

    def _df_selection(self):
        self._filter_columns()
        self._time_standardization() # brind time to the same format - 'coerce'
        self._filter_and_year_selection() # select year 2000 onwards, select filters 1, 2, or 3 (user's choice)
        self._drop_dupes() # remove duplicates
        self._handle_missing_values()
        self._to_gdf()
        self._well_selection()
        self._date_round()
        self._rename_cols()

    def _time_standardization(self):
        self._dataframe['Date'] = pd.to_datetime(self._dataframe['Date'], errors='coerce', utc=True)
        self._dataframe = self._dataframe.sort_values(by=['Well_ID', 'Date']).reset_index(drop=True)
    
    def _filter_and_year_selection(self):
        self._dataframe['Year'] = self._dataframe['Date'].dt.year
        self._dataframe = self._dataframe[
            (self._dataframe['Year'] >= self.year_start) &
            (self._dataframe['Year'] <= self.year_end) &
            (self._dataframe['Filter'] == self.filter)
        ]

    def _well_selection(self):
        pass

    def _to_gdf(self):
        self._dataframe['geometry'] = self._dataframe['geometry'].apply(wkt.loads)
        self._dataframe = gpd.GeoDataFrame(self._dataframe, geometry='geometry', crs="EPSG:4326")

    def _drop_dupes(self):
        self._dataframe = self._dataframe.drop_duplicates().reset_index(drop=True)

    def _date_round(self):
        pass

    def _rename_cols(self):
        pass
    
    def __len__(self):
        pass

    def __getitem__(self):
        pass

    def get_variable(self, name: Union[str, List[str]]):
        return self._dataframe[name]

    @abstractmethod
    def _filter_columns(self):
        pass

    @abstractmethod
    def _handle_missing_values():
        pass


if __name__ == "__main__":
    pass
