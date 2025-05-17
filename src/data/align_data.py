import os
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import wkt
from shapely.geometry import Point
from abc import ABC, abstractmethod


class BaseAligner(ABC):
    def __init__(self, well_filter=1) -> None:

        self.current_dir = os.getcwd()
        nitrate_dir = os.path.join(self.current_dir, 'data/clean', "well_chem_data", "for_Alignment", f"utrecht_well_chem_combined_{well_filter}.csv")
        nitrate_df = pd.read_csv(nitrate_dir, parse_dates=['Date'])

        self.nitrate_gdf = self._to_gdf(nitrate_df)

        # self.joined_df = self._align()
    
    def _to_gdf(self, df):
        df['geometry'] = df['geometry'].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
        return gdf
    
    # def getter(self):
    #     return self.joined_df
    
    # @abstractmethod
    # def _align(self):
    #     pass

    def _to_geo_table(self, lgn):
        band_float = lgn[0].values
        mask = ~np.isnan(band_float) # create mask before converting to int
        band = band_float.astype("int32")
        # extract polygons
        results = (
            {"geometry": shape(geom), "code": int(value)}
            for geom, value in shapes(band, mask=mask, transform=lgn.rio.transform())
        )
        gdf = gpd.GeoDataFrame.from_records(results)
        gdf = gdf.set_geometry("geometry")
        gdf.set_crs(lgn.rio.crs, inplace=True)
        return gdf


if __name__ == "__main__":
    instance = BaseAligner()
    nitrate_temp = instance.nitrate_gdf
    nitrate_temp.to_file("nitrate_temp.gpkg", driver="GPKG")
