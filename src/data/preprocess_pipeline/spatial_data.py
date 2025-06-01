import os
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
from abc import abstractmethod
from .dataset import Dataset_Preprocess


class SpatialData(Dataset_Preprocess):
    def __init__(self, type_of_data):
        super().__init__(type_of_data)
        self._utrecht_mask = self._aoi_finder()

        self._datapaths = None
        self._dataframe = None

    def _aoi_finder(self):
        # load Utrecht polygon coordinates
        utrecht_polygon_path = os.path.join(self._datasetdir, "..", "utrecht polygon.csv")
        df = pd.read_csv(utrecht_polygon_path, sep=';')

        geo_shape_str = df.loc[0, "Geo Shape"] #coordinates of the polygon
        geo_shape = json.loads(geo_shape_str)
        coords = geo_shape["coordinates"][0]  # outer ring of the polygon

        utrecht_polygon = Polygon(coords)

        # define boundary line
        x1, y1 = 5.066884, 52.170366  # upper-left
        x2, y2 = 5.237030, 51.978896  # lower-right

        def is_above_line(x, y):
            """Returns True if point (x, y) is above the diagonal line"""
            if x1 == x2:
                return y > y1  # vertical line
            slope = (y2 - y1) / (x2 - x1)
            y_on_line = slope * (x - x1) + y1
            return (y > y_on_line) and (x > x1)

        # Filter polygon coordinates
        filtered_coords = [
            (x, y) for x, y in utrecht_polygon.exterior.coords
            if is_above_line(x, y)]

        # Make sure polygon closes properly
        if filtered_coords[0] != filtered_coords[-1]:
            filtered_coords.append(filtered_coords[0])

        #new precise polygon
        aoi = Polygon(filtered_coords)

        utrecht_mask = gpd.GeoDataFrame(geometry=[aoi], crs="EPSG:4326")
        return utrecht_mask

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

    @abstractmethod
    def _preprocess(self):
        pass


if __name__ == "__main__":
    pass
