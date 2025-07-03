import os
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
from abc import abstractmethod

try:
    from .dataset import Dataset_Preprocess
except ImportError:
    from dataset import Dataset_Preprocess


class SpatialData(Dataset_Preprocess):
    def __init__(self, provinces, type_of_data):
        super().__init__(provinces, type_of_data)
        self._utrecht_mask = self._aoi_finder()

        self._datapaths = None
        self._dataframe = None

    def _aoi_finder(self):
        provinces_path = os.path.join(self._datasetdir, "..", "provinces_nl/BestuurlijkeGebieden_2025.gpkg")
        gdf = gpd.read_file(provinces_path, layer="provinciegebied")   # load only layer with Provinces
        gdf = gdf.to_crs("EPSG:4326")

        # normalize province names
        gdf["naam"] = gdf["naam"].str.lower()

        included_geometries = []

        for province in self._provinces:
            if province == "utrecht_east":
                # get full Utrecht geometry and crop
                utrecht_geom = gdf[gdf["naam"] == "utrecht"].geometry.values[0]
                if isinstance(utrecht_geom, MultiPolygon) and len(utrecht_geom.geoms) == 1:
                    utrecht_geom = utrecht_geom.geoms[0]
                cropped = self._crop_utrecht_east(utrecht_geom)  # helper function
                included_geometries.append(cropped)
            else:
                matched = gdf[gdf["naam"] == province]
                if not matched.empty:
                    # included_geometries.append(matched.union_all())
                    geom = matched.geometry.unary_union
                    included_geometries.append(geom)

        # combine all selected geometries into one AOI
        aoi_union = gpd.GeoSeries(included_geometries).union_all()
        return gpd.GeoDataFrame(geometry=[aoi_union], crs=gdf.crs)
    
    def _crop_utrecht_east(self, polygon):
        # cropping diagonal
        x1, y1 = 5.066884, 52.170366  # upper-left
        x2, y2 = 5.237030, 51.978896  # lower-right

        def is_above_line(x, y):
            if x1 == x2:
                return y > y1
            slope = (y2 - y1) / (x2 - x1)
            y_on_line = slope * (x - x1) + y1
            return (y > y_on_line) and (x > x1)

        filtered_coords = [
            (x, y) for x, y in polygon.exterior.coords
            if is_above_line(x, y)
        ]

        if len(filtered_coords) < 3:
            raise ValueError("Not enough points to form a polygon after cropping.")

        if filtered_coords[0] != filtered_coords[-1]:
            filtered_coords.append(filtered_coords[0])

        return Polygon(filtered_coords)

    def _column_selection(self, gdf, selected_cols: list[str]):
        gdf = gdf[selected_cols].copy()
        return gdf
    
    def _crop_file(self, gdf):
        # Crops polygons by computing spatial intersection
        utrecht_mask_proj = self._utrecht_mask.to_crs(gdf.crs)
        cropped = gpd.overlay(gdf, utrecht_mask_proj, how="intersection")
        return cropped

    @abstractmethod
    def _populate_dataframe(self):
        pass

    @abstractmethod
    def _paths_finder(self):
        pass

    def _preprocess(self):
        pass

    @property
    def dataframe(self):
        """Getter for the processed dataframes."""
        return self._dataframe


if __name__ == "__main__":
    pass
