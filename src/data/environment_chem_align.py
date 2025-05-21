import os
import numpy as np
import pandas as pd
import geopandas as gpd
from align_data import BaseAligner


class EnvironmentalAligner(BaseAligner):
    def __init__(self, well_filter=1):
        super().__init__(well_filter)
        var_dir = os.path.join(self.current_dir, 'data/clean', "environment", f"environment.csv")
        self.env_df = pd.read_csv(var_dir, parse_dates=['Date'])

        self._dataframe = self._align()
        
    def _align(self):
        aligned_data = []
        self.env_df['Date'] = self.env_df['Date'].dt.date  # strip time for matching

        for _, row in self.nitrate_gdf.iterrows():
            measurement_date = row['Date'].date()

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

            aligned_data.append({
                "Well_ID": row["Well_ID"],
                "BRO-ID": row["BRO-ID"],
                "Date": row["Date"],
                "Nitrate": row["Nitrate"],
                "geometry": row["geometry"],
                "avg_temp_mean": avg_temp,
                "avg_precip_sum": avg_precip,
            })

        return gpd.GeoDataFrame(aligned_data, geometry="geometry", crs="EPSG:4326")


if __name__ == "__main__":
    instance = EnvironmentalAligner()
    print(instance._dataframe.head(30))
