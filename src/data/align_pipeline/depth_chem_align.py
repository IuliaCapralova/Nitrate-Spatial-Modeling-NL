import os
import numpy as np
import pandas as pd
import geopandas as gpd
from datetime import timedelta
from shapely.geometry import Point
from concurrent.futures import ProcessPoolExecutor

try:
    from .align_data import BaseAligner
except ImportError:
    from align_data import BaseAligner

import warnings
warnings.filterwarnings("ignore", category=FutureWarning, message=".*GeoDataFrame.swapaxes.*")



class DepthAligner(BaseAligner):
    def __init__(self, provinces, well_filter: int, connect_to, years, days_window=72, radius=5000) -> None:
        super().__init__(provinces, well_filter, connect_to, years)
        self.window = days_window
        self.radius = radius

        depth_dfs = []
        for province in provinces:
            var_dir = os.path.join(self.current_dir, '../data/clean', "well_depth_data", "for_Alignment", f"{province}_well_depth_combined_{well_filter}.csv")
            if os.path.exists(var_dir):
                df = pd.read_csv(var_dir, parse_dates=['Date'])
                gdf = self._to_gdf(df)
                depth_dfs.append(gdf)
            else:
                print(f"Warning: File not found for {province}")

        # bring together data from all needed provinces
        self.depth_gdf = gpd.GeoDataFrame(pd.concat(depth_dfs, ignore_index=True))

        ## distance calculations (Amersfoort RD New)
        self.nitrate_gdf = self.nitrate_gdf.to_crs(epsg=28992)
        self.depth_gdf = self.depth_gdf.to_crs(epsg=28992)

        # unique wells from the depth dataset
        self.wells_gdf = self.depth_gdf[['Well_ID', 'geometry']].drop_duplicates().set_index('Well_ID')
        # Build spatial index for fast nearest-neighbor queries
        self.wells_sindex = self.wells_gdf.sindex

        self._dataframe = self._align()

    def _align(self):
        print("Starting parallel alignment...")

        # find how many cores computer has (11 cores in case of m3 pro chip)
        n_cores = 6
        chunks = np.array_split(self.nitrate_gdf, n_cores)

        with ProcessPoolExecutor(max_workers=n_cores) as executor:
            futures = [executor.submit(self._process_nitrate_chunk, chunk, self.wells_gdf, self.depth_gdf, self.window, self.radius) for chunk in chunks]
            all_results = []
            for f in futures:
                all_results.extend(f.result())

        df_results = pd.DataFrame(all_results)

        if self.connect_to == "nitrate_data":
            joined = self.nitrate_gdf.merge(df_results, left_index=True, right_on='nitrate_index')
            joined = joined[['Well_ID', 'bro-id', 'Filter', 'date', 'nitrate', 'geometry', 'distance_m', 'groundwater depth']]
        elif self.connect_to == "grid_data":
            joined = self.nitrate_gdf.merge(df_results, left_index=True, right_on='nitrate_index')
            joined = joined[['date', 'geometry', 'distance_m', 'groundwater depth']]

        return joined
    
    def _process_nitrate_chunk(self, chunk, wells_gdf, depth_gdf, window, radius):
        from shapely.geometry import Point  # Required in subprocesses
        results = []

        for idx, row in chunk.iterrows():
            pt = row.geometry
            sample_date = row.date
            matched_well = None
            avg_depth = None
            dist = None

            # Bounding box
            possible_idx = list(wells_gdf.sindex.intersection(pt.buffer(radius).bounds))
            if not possible_idx:
                results.append({'nitrate_index': idx, 'matched_well': None, 'distance_m': None, 'groundwater depth': None})
                continue

            candidates = wells_gdf.iloc[possible_idx]
            dists = candidates.geometry.distance(pt)
            dists = dists[dists <= radius]
            if dists.empty:
                results.append({'nitrate_index': idx, 'matched_well': None, 'distance_m': None, 'groundwater depth': None})
                continue

            for well_id in dists.sort_values().index:
                d = candidates.loc[well_id].geometry.distance(pt)
                window_start = sample_date - timedelta(days=window)
                window_end = sample_date

                window_df = depth_gdf[
                    (depth_gdf.Well_ID == well_id) &
                    (depth_gdf.Date >= window_start) &
                    (depth_gdf.Date <= window_end)
                ]
                if not window_df.empty:
                    avg_depth = window_df.Depth.mean()
                    matched_well = well_id
                    dist = d
                    break

            results.append({
                'nitrate_index': idx,
                'matched_well': matched_well,
                'distance_m': dist,
                'groundwater depth': avg_depth
            })

        return results

    def find_candidate_wells(self, point: Point, radius: float = 5000):
        # Query spatial index for candidate wells within point's bounding box
        possible_idx = list(self.wells_sindex.intersection(point.buffer(radius).bounds))
        if not possible_idx:
            return []
        candidates = self.wells_gdf.iloc[possible_idx]
        # Compute distances and filter by radius
        dists = candidates.geometry.distance(point)
        dists = dists[dists <= radius]
        if dists.empty:
            return []
        # Return well IDs sorted by ascending distance
        return dists.sort_values().index.tolist()


if __name__ == "__main__":
    well_filter = 1
    window = 72
    radius = 6000
    connect_to = "nitrate_data"
    provinces = ["utrecht", "flevoland"]
    years = [2010]

    instance = DepthAligner(provinces, well_filter, connect_to, years, window, radius)
    print(instance.dataframe)
    instance._dataframe.to_csv("depth_temp.csv")
    # print(instance.get_variable("groundwater depth"))
