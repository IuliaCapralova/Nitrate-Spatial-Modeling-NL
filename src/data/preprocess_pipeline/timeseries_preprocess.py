import os
import pandas as pd
import geopandas as gpd
from shapely import wkt
from typing import Union, List
from abc import abstractmethod

try:
    from .dataset import Dataset_Preprocess
except ImportError:
    from dataset import Dataset_Preprocess


class TimeseriesPreprocess(Dataset_Preprocess):
    
    def __init__(self, provinces:list[str], well_filter, year_start, year_end, type_of_data) -> None:
        super().__init__(provinces, type_of_data)
        self.year_start = year_start
        self.year_end = year_end

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

        self._dataframe = {}
        for province in self._provinces:
            self._file_path = os.path.join(self._datasetdir, f"{province}_well_{variable}_combined.csv")
            file = pd.read_csv(self._file_path)
            self._data = file
            self._df_selection()
            name = f"{province}_well_{variable}_combined_{self.filter}"
            self._dataframe[name] = self._data

    def _df_selection(self):
        self._filter_columns()
        self._time_standardization() # bring time to the same format - 'coerce'
        self._filter_and_year_selection() # select year 2000 onwards, select filters 1, 2, or 3 (user's choice)
        self._drop_dupes() # remove duplicates
        self._handle_missing_values()
        self._to_gdf()
        self._well_selection()
        self._date_round()
        self._rename_cols()

    def _time_standardization(self):
        self._data['Date'] = pd.to_datetime(self._data['Date'], errors='coerce', utc=True)
        self._data = self._data.sort_values(by=['Well_ID', 'Date']).reset_index(drop=True)
    
    def _filter_and_year_selection(self):
        self._data['Year'] = self._data['Date'].dt.year
        self._data = self._data[
            (self._data['Year'] >= self.year_start) &
            (self._data['Year'] <= self.year_end) &
            (self._data['Filter'] == self.filter)
        ]

    def _well_selection(self):
        pass

    def _to_gdf(self):
        self._data = self._data.dropna(subset=['geometry'])
        self._data['geometry'] = self._data['geometry'].apply(wkt.loads)
        self._data = gpd.GeoDataFrame(self._data, geometry='geometry', crs="EPSG:4326")

    def _drop_dupes(self):
        self._data = self._data.drop_duplicates().reset_index(drop=True)

    def _date_round(self):
        pass

    def _rename_cols(self):
        pass
    
    def __len__(self):
        pass

    def __getitem__(self):
        pass

    def get_variable(self, name: Union[str, List[str]]):
        return self._data[name]
    
    @property
    def dataframe(self):
        """Getter for the processed dataframes dictionary."""
        return self._dataframe

    @abstractmethod
    def _filter_columns(self):
        pass

    @abstractmethod
    def _handle_missing_values():
        pass


if __name__ == "__main__":
    pass
