import os
import pandas as pd
from datetime import timedelta
from shapely.geometry import Point
from align_data import BaseAligner


class DepthAligner(BaseAligner):
    def __init__(self, well_filter: int, days_window=72, radius=10000) -> None:
        super().__init__(well_filter)
        self.window = days_window
        self.radius = radius

        var_dir = os.path.join(self.current_dir, 'data/clean', "well_depth_data", "for_Alignment", f"utrecht_well_depth_combined_{well_filter}.csv")
        depth_df = pd.read_csv(var_dir, parse_dates=['Date'])
        self.depth_gdf = self._to_gdf(depth_df)

        ## distance calculations (Amersfoort RD New)
        self.nitrate_gdf = self.nitrate_gdf.to_crs(epsg=28992)
        self.depth_gdf  = self.depth_gdf.to_crs(epsg=28992)

        # unique wells from the depth dataset
        self.wells_gdf = self.depth_gdf[['Well_ID', 'geometry']].drop_duplicates().set_index('Well_ID')
        # Build spatial index for fast nearest-neighbor queries
        self.wells_sindex = self.wells_gdf.sindex

        self._dataframe = self._align()

    def _align(self):
        # iterate over each nitrate observation and assign averaged depth
        results = []
        for idx, row in self.nitrate_gdf.iterrows():
            pt = row.geometry
            sample_date = row.date
            matched_well = None
            avg_depth = None
            dist = None

            candidate_wells = self.find_candidate_wells(pt, radius=self.radius) # Get wells within radius
            
            # Define time window for depth sampling
            window_start = sample_date - timedelta(days=self.window)
            window_end = sample_date
            
            # Explore each well until a valid depth window is found
            for well_id in candidate_wells:
                # Calculate exact distance
                d = self.wells_gdf.loc[well_id].geometry.distance(pt)
                # Filter depth records for this well within window
                window = self.depth_gdf[
                    (self.depth_gdf.Well_ID == well_id) &
                    (self.depth_gdf.Date >= window_start) &
                    (self.depth_gdf.Date <= window_end)
                ]
                if not window.empty:
                    avg_depth = window.Depth.mean()
                    matched_well = well_id
                    dist = d
                    break

            results.append({
                'nitrate_index': idx,
                'matched_well': matched_well,
                'distance_m': dist,
                'groundwater depth': avg_depth
            })

        df_results = pd.DataFrame(results)

        # TODO do a separte function
        joined = self.nitrate_gdf.merge(df_results, left_index=True, right_on='nitrate_index')
        joined = joined[['Well_ID', 'bro-id', 'Filter', 'date', 'nitrate', 'geometry', 'distance_m', 'groundwater depth']]

        return joined

    def find_candidate_wells(self, point: Point, radius: float = 10000):
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
    radius = 7000

    instance = DepthAligner(well_filter, window, radius)
    print(instance._dataframe)
    instance._dataframe.to_csv("depth_temp.csv")
    # print(instance.get_variable("groundwater depth"))
