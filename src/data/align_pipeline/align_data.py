import os
import pandas as pd
import geopandas as gpd
from shapely import wkt
from typing import Union, List
from abc import ABC, abstractmethod


class BaseAligner(ABC):
    def __init__(self, well_filter=1, connect_to='nitrate_data', years=[2010]) -> None:
        self.current_dir = os.getcwd()
        self.connect_to = connect_to

        if self.connect_to == 'nitrate_data':
            nitrate_dir = os.path.join(self.current_dir, 'data/clean', "well_chem_data", "for_Alignment", f"utrecht_well_chem_combined_{well_filter}.csv")
            nitrate_df = pd.read_csv(nitrate_dir, parse_dates=['date'])
            self.nitrate_gdf = self._to_gdf(nitrate_df)
        elif self.connect_to == 'grid_data':
            year = years[0]
            nitrate_dir = os.path.join(self.current_dir, 'data/grids_for_prediction', f"grid_{year}.csv")
            nitrate_df = pd.read_csv(nitrate_dir, parse_dates=['date'])
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
    
    @abstractmethod
    def _align(self):
        pass


if __name__ == "__main__":
    instance = BaseAligner()
    nitrate_temp = instance.nitrate_gdf
    print(nitrate_temp)
    # nitrate_temp.to_file("nitrate_temp.gpkg", driver="GPKG")
