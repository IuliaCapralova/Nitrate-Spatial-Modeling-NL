import os
import time
import concurrent.futures
import pandas as pd
import rasterio

try:
    from .align_spatial import SpatialTimeseriesBaseAligner
except ImportError:
    from align_spatial import SpatialTimeseriesBaseAligner


import os
from owslib.wcs import WebCoverageService
import pandas as pd

class ElevationAligner(SpatialTimeseriesBaseAligner):
    def __init__(self, provinces, well_filter, connect_to, years):
        super().__init__(provinces, well_filter, connect_to, years)
        self.elevation_dir = os.path.join(self.current_dir, "../data/clean/elevation")
        os.makedirs(self.elevation_dir, exist_ok=True)
        self.wcs_url = "https://api.ellipsis-drive.com/v3/ogc/wcs/69f81443-c000-4479-b08f-2078e3570394?"
        self.layer_id = "393408cf-842d-4181-af87-94f6123bdff0"
        self._dataframe = self._align()

    def _align(self):
        start = time.time()
        gdf = self.nitrate_gdf.to_crs("EPSG:28992")
        gdf["elevation"] = gdf.apply(self._get_elevation_at_point, axis=1)

        # rows = [row for _, row in gdf.iterrows()]
        # with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:  # or os.cpu_count()
        #     # Map rows to elevation
        #     elevations = list(executor.map(self._get_elevation_at_point, rows))
        # gdf["elevation"] = elevations

        gdf = gdf.to_crs("EPSG:4326")
        gdf["lon"] = gdf.geometry.x
        gdf["lat"] = gdf.geometry.y

        duration = time.time() - start
        print(f"Elevation alignment finished in {self._format_duration(duration)} (hh:mm:ss)")

        return gdf

    def _get_elevation_at_point(self, row):
        x, y = row.geometry.x, row.geometry.y
        x_tile = int(x // 1000) * 1000
        y_tile = int(y // 1000) * 1000
        bbox = (x_tile, y_tile, x_tile + 1000, y_tile + 1000)

        # Construct tile name
        tile_name = f"ahn_tile_{x_tile}_{y_tile}.tif"
        tile_path = os.path.join(self.elevation_dir, tile_name)

        # Download tile if not exists
        if not os.path.exists(tile_path):
            try:
                wcs = WebCoverageService(self.wcs_url, version="1.0.0")
                response = wcs.getCoverage(
                    identifier=self.layer_id,
                    bbox=bbox,
                    crs="EPSG:28992",
                    format="GeoTIFF",
                    width=500, height=500
                )
                with open(tile_path, "wb") as f:
                    f.write(response.read())
            except Exception as e:
                print(f"Failed to download tile for bbox {bbox}: {e}")
                return None

        # Read elevation at point
        try:
            with rasterio.open(tile_path) as src:
                row, col = src.index(x, y)
                value = src.read(1)[row, col]
                return None if value == src.nodata else value
        except Exception as e:
            print(f"Failed to read elevation at point ({x}, {y}): {e}")
            return None
        
    def _format_duration(self, seconds):
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{secs:02}"


if __name__ == "__main__":
    provinces = ["utrecht"]
    well_filter = 1
    connect_to = "grid_data"
    years = [2010]

    instance = ElevationAligner(provinces, well_filter, connect_to, years)
    print(instance.dataframe)
    instance.dataframe.to_csv("elevation_align.csv", index=False)
    # print(instance.get_variable(name="landuse code"))
    # landuse_counts = gdf['Landuse_Code'].value_counts(dropna=True).sort_index()
    # print(landuse_counts)
