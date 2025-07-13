import os
import pandas as pd
import geopandas as gpd
from shapely import wkt
from typing import Union, List
from abc import ABC, abstractmethod


class BaseAligner(ABC):
    def __init__(self, provinces, well_filter, connect_to, years) -> None:
        self.current_dir = os.getcwd()
        self.connect_to = connect_to

        if self.connect_to == 'nitrate_data':
            all_dfs = []
            for province in provinces:
                nitrate_dir = os.path.join(self.current_dir, '../data/clean', "well_chem_data", "for_Alignment", f"{province}_well_chem_combined_{well_filter}.csv")
                if os.path.exists(nitrate_dir):
                    df = pd.read_csv(nitrate_dir, parse_dates=['date'])
                    all_dfs.append(df)
                else:
                    print(f"Warning: File not found for {province}")

            self.nitrate_gdf = pd.concat(all_dfs, ignore_index=True)
            self.nitrate_gdf = self._to_gdf(self.nitrate_gdf)

        elif self.connect_to == 'grid_data':
            all_dfs = []
            year = years[0]
            for province in provinces:
                nitrate_dir = os.path.join(self.current_dir, '../data/grids_for_prediction', f"grid_{year}_{province}.csv")
                if os.path.exists(nitrate_dir):
                    df = pd.read_csv(nitrate_dir, parse_dates=['date'])
                    all_dfs.append(df)
                else:
                    print(f"Warning: File not found for {province}")

            nitrate_df = pd.concat(all_dfs, ignore_index=True)
            self.nitrate_gdf = self._to_gdf(nitrate_df)

        self._dataframe = None

    def _to_gdf(self, df):
        df['geometry'] = df['geometry'].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
        return gdf

    # @property
    # def dataframe(self):
    #     return self._dataframe

    def get_variable(self, name: Union[str, List[str]]):
        return self._dataframe[name]
    
    @property
    def dataframe(self):
        return self._dataframe

    @abstractmethod
    def _align(self):
        pass


if __name__ == "__main__":
    provinces = ["utrecht"]
    instance = BaseAligner(provinces)
    nitrate_temp = instance.nitrate_gdf
    print(nitrate_temp)
    # nitrate_temp.to_file("nitrate_temp.gpkg", driver="GPKG")
