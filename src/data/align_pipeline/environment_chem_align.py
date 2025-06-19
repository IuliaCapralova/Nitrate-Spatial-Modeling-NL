import os
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.spatial import cKDTree

# try:
#     from .align_data import BaseAligner
# except ImportError:
#     from align_data import BaseAligner

# try:
#     from .env_preprocess import Environmental_Preprocess
# except ImportError:
#     from env_preprocess import Environmental_Preprocess

from align_pipeline.env_preprocess import Environmental_Preprocess
from align_pipeline.align_data import BaseAligner



class EnvironmentalAligner(BaseAligner):
    def __init__(self, provinces, well_filter, connect_to, years):
        super().__init__(provinces, well_filter, connect_to, years)
        self.env_preprocess_instance = Environmental_Preprocess()

        self.var_dir = os.path.join(self.current_dir, '../data/clean', "environment")
        self.env_df = None

        station_location_dir = os.path.join(self.var_dir, "meteorological_stations_locations.csv")
        stations_df = pd.read_csv(station_location_dir)
        self.stations_gdf = self._to_gdf(stations_df)

        self._kdtree = self._create_kdtree()

        self._dataframe = self._align()
    
    def _create_kdtree(self):
        # create KDTree to quickly find the nearest station with respect to nitrate well location
        station_coords = np.array([(geom.x, geom.y)for geom in self.stations_gdf["geometry"]])
        kdtree = cKDTree(station_coords)
        return kdtree
    
    def _nearest_station_finder(self, nitrate_row):
        nitrate_point = nitrate_row['geometry']
        nitrate_coords = np.array([[nitrate_point.x, nitrate_point.y]])

        station_ids = self.stations_gdf["station_id"].to_list()

        # Find nearest station
        dist, idx = self._kdtree.query(nitrate_coords)
        nearest_station_id = station_ids[idx[0]]

        return nearest_station_id

    def _align(self):
        # 1. For each nitrate row extract geometry and find the closes station using kdtree
        # 2. Load file with data from the nearest station
        # 3. Align using date

        aligned_data = []

        for _, row in self.nitrate_gdf.iterrows():
            measurement_date = row['date'].date()

            nearest_station_id = self._nearest_station_finder(row)

            # NOTE: do this ONLY if file is not already in the folder
            var_dir_complete = os.path.join(self.var_dir, f"{str(nearest_station_id)}.csv")

            # In case we do not have file with needed station --> retreive, load, and then align
            if not os.path.exists(var_dir_complete):
                self.env_preprocess_instance(station_ids=nearest_station_id)

            self.env_df = pd.read_csv(var_dir_complete, parse_dates=['Date'])
            self.env_df['Date'] = self.env_df['Date'].dt.date         # strip time for matching

            #find the row index in env_df that matches the measurement date
            match_idx = self.env_df[self.env_df['Date'] == measurement_date].index

            if len(match_idx) == 0:
                avg_temp, avg_precip = np.nan, np.nan
            else:
                idx = match_idx[0]
                temp_start_idx = idx - 59  # 60 days: idx - 59 to idx
                precip_start_idx = idx - 3  # 4 days: idx - 3 to idx

                # check if we have enough data
                if temp_start_idx < 0 or precip_start_idx < 0:
                    avg_temp, avg_precip = np.nan, np.nan
                else:
                    temp_subset = self.env_df.loc[temp_start_idx:idx]
                    precip_subset = self.env_df.loc[precip_start_idx:idx]

                    # Sanity check: enforce exact length
                    if len(temp_subset) == 60 and len(precip_subset) == 4:
                        avg_temp = temp_subset['temp_mean'].replace(-1, np.nan).mean()
                        avg_precip = precip_subset['precip_sum'].mean()
                    else:
                        avg_temp, avg_precip = np.nan, np.nan

            if self.connect_to == "nitrate_data":
                aligned_data.append({
                    "Well_ID": row["Well_ID"],
                    "BRO-ID": row["bro-id"],
                    "date": row["date"],
                    "Nitrate": row["nitrate"],
                    "geometry": row["geometry"],
                    "temperature": avg_temp,
                    "precipitation": avg_precip,
                })
            elif self.connect_to == "grid_data":
                aligned_data.append({
                    "date": row["date"],
                    "geometry": row["geometry"],
                    "temperature": avg_temp,
                    "precipitation": avg_precip,
                })

        return gpd.GeoDataFrame(aligned_data, geometry="geometry", crs="EPSG:4326")


if __name__ == "__main__":
    print(f"CURR DIR: {os.getcwd()}")
    provinces = ["utrecht"]
    well_filter = 1
    connect_to = "nitrate_data"
    years = [2010]

    instance = EnvironmentalAligner(provinces, well_filter, connect_to, years)
    print(instance.dataframe)
    # print(instance.get_variable(["temperature", "precipitation"]))
