# import numpy as np
# import pandas as pd
# import os
# import geopandas as gpd
# from scipy.spatial import cKDTree
# from datetime import timedelta
# from shapely.geometry import Point
# from concurrent.futures import ProcessPoolExecutor

# try:
#     from .align_data import BaseAligner
# except ImportError:
#     from align_data import BaseAligner

# import warnings
# warnings.filterwarnings("ignore", category=FutureWarning, message=".*GeoDataFrame.swapaxes.*")


# class DepthAligner(BaseAligner):
#     def __init__(self, provinces, well_filter: int, connect_to, years, days_window=72, radius=6000) -> None:
#         super().__init__(provinces, well_filter, connect_to, years)
#         self.window  = days_window
#         self.radius  = radius
#         self._prepare_depth(provinces, well_filter)
#         self._dataframe = self._align()

#     def _prepare_depth(self, provinces, well_filter):
#         depth = []
#         for pr in provinces:
#             f = f"../data/clean/well_depth_data/for_Alignment/{pr}_well_depth_combined_{well_filter}.csv"
#             if os.path.exists(f):
#                 depth.append(pd.read_csv(f, parse_dates=['Date']))
#         depth = pd.concat(depth, ignore_index=True)
#         self.depth_gdf = self._to_gdf(depth).to_crs(28992)

#         # rolling 72-day mean per well
#         d = self.depth_gdf
#         d['Date_bin'] = d['Date'].dt.floor('1D')

#         d = d.sort_values(['Well_ID', 'Date_bin'])

#         self.depth_roll = (
#             d.set_index('Date_bin')
#              .groupby('Well_ID')
#              .rolling(f'{self.window}D', closed='both')['Depth']
#              .mean()
#              .reset_index()
#              .rename(columns={'Depth': 'groundwater_depth'})
#         )

#         # wells geometry for KD-tree
#         self.wells = (
#             self.depth_gdf[['Well_ID', 'geometry']]
#             .drop_duplicates()
#             .set_index('Well_ID')
#             .to_crs(28992)
#         )
#         xy = np.vstack(self.wells.geometry.apply(lambda g: (g.x, g.y)).to_numpy())
#         self.tree = cKDTree(xy)
#         self.well_ids = self.wells.index.to_numpy()

#     # ------------------------------------------------------------
#     # 2) fast align
#     # ------------------------------------------------------------
#     def _align(self):
#         nitr = self.nitrate_gdf.to_crs(28992).reset_index(drop=False)
#         nitr_xy = np.vstack(nitr.geometry.apply(lambda g: (g.x, g.y)).to_numpy())

#         # ---------- 2a. spatial search
#         neigh_idx = self.tree.query_ball_point(nitr_xy, r=self.radius)

#         flat_well_idx, flat_sample_idx, flat_dist = [], [], []
#         for sample_pos, (idx_list, sample_id) in enumerate(zip(neigh_idx, nitr['index'])):
#             if not idx_list:
#                 continue
#             wells_xy = self.tree.data[idx_list]
#             dists = np.linalg.norm(wells_xy - nitr_xy[sample_pos], axis=1)

#             flat_well_idx.extend(idx_list)
#             flat_sample_idx.extend([sample_id] * len(idx_list))
#             flat_dist.extend(dists)

#         if not flat_well_idx:
#             raise ValueError("No wells found inside the search radius")

#         flat_well_idx = np.asarray(flat_well_idx, dtype=np.intp)
#         flat_sample_idx = np.asarray(flat_sample_idx, dtype=np.intp)
#         flat_dist = np.asarray(flat_dist, dtype=float)

#         df_pairs = pd.DataFrame(
#             {
#                 "nitrate_index": flat_sample_idx,
#                 "Well_ID": self.well_ids[flat_well_idx],
#                 "distance_m": flat_dist,
#             }
#         )

#         # ---------- 2b. add sample date
#         df_pairs = df_pairs.merge(
#             nitr[["index", "date"]],
#             left_on="nitrate_index",
#             right_on="index",
#             how="left",
#         ).drop(columns="index")

#         # ---------- 2c. temporal join (depth window)
#         merged = df_pairs.merge(self.depth_roll, on="Well_ID", how="left")

#         w = self.window
#         ok = (merged["Date_bin"] >= merged["date"] - pd.Timedelta(days=w)) & (
#             merged["Date_bin"] <= merged["date"]
#         )
#         merged = merged[ok]

#         # ---------- 2d. keep nearest well that has data
#         merged = (
#             merged.sort_values(["nitrate_index", "distance_m"])
#             .drop_duplicates("nitrate_index")
#         )

#         # ---------- 2e. final join back to nitrate layer
#         out = nitr.merge(
#             merged,
#             left_on="index",
#             right_on="nitrate_index",
#             how="left",
#             suffixes=("_nitr", "_depth"),
#         )

#         # keep nitrate-layer IDs/dates; rename depth mean
#         out = out.rename(
#             columns={
#                 "Well_ID_nitr": "Well_ID",
#                 "groundwater_depth": "groundwater_depth",
#                 "date_nitr": "date",
#             }
#         )

#         # Only drop columns that actually exist!
#         to_drop = [c for c in ["Well_ID_depth", "date_depth"] if c in out.columns]
#         if to_drop:
#             out = out.drop(columns=to_drop)

#         # ---------- 2f. honour original public schema
#         if self.connect_to == "nitrate_data":
#             return out[
#                 [
#                     "Well_ID",
#                     "bro-id",
#                     "Filter",
#                     "date",
#                     "nitrate",
#                     "geometry",
#                     "distance_m",
#                     "groundwater_depth",
#                 ]
#             ]
#         else:  # grid_data
#             return out[["date", "geometry", "distance_m", "groundwater_depth"]]


# if __name__ == "__main__":
#     well_filter = 1
#     window = 72
#     radius = 6000
#     connect_to = "grid_data"
#     provinces = ["utrecht"]
#     years = [2022]

#     instance = DepthAligner(provinces, well_filter, connect_to, years, window, radius)
#     print(instance.dataframe)
#     instance._dataframe.to_csv("depth_temp.csv")
#     # print(instance.get_variable("groundwater depth"))


# ---------------------

import numpy as np
import pandas as pd
import os
from itertools import repeat
import geopandas as gpd
from scipy.spatial import cKDTree
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
    def __init__(self, provinces, well_filter: int, connect_to, years, days_window=72, radius=6000, n_jobs=8) -> None:
        super().__init__(provinces, well_filter, connect_to, years)
        self.window  = days_window
        self.radius  = radius
        self.n_jobs = n_jobs
        self._prepare_depth(provinces, well_filter)
        self._dataframe = self._align()

    def _prepare_depth(self, provinces, well_filter):
        depth = []
        for pr in provinces:
            f = f"../data/clean/well_depth_data/for_Alignment/{pr}_well_depth_combined_{well_filter}.csv"
            if os.path.exists(f):
                depth.append(pd.read_csv(f, parse_dates=['Date']))
        depth = pd.concat(depth, ignore_index=True)
        self.depth_gdf = self._to_gdf(depth).to_crs(28992)

        # rolling 72-day mean per well
        d = self.depth_gdf
        d['Date_bin'] = d['Date'].dt.floor('1D')
        d = d.sort_values(['Well_ID', 'Date_bin'])

        self.depth_roll = (
            d.set_index('Date_bin')
             .groupby('Well_ID')
             .rolling(f'{self.window}D', closed='both')['Depth']
             .mean()
             .reset_index()
             .rename(columns={'Depth': 'groundwater_depth'})
        )

        # wells geometry for KD-tree
        self.wells = (
            self.depth_gdf[['Well_ID', 'geometry']]
            .drop_duplicates()
            .set_index('Well_ID')
            .to_crs(28992)
        )
        xy = np.vstack(self.wells.geometry.apply(lambda g: (g.x, g.y)).to_numpy())
        self.tree = cKDTree(xy)
        self.well_ids = self.wells.index.to_numpy()

    @staticmethod
    def _process_sample(args):
        sample_pos, sample_id, neigh_idx, nitr_xy, tree_data = args
        idx_list = neigh_idx[sample_pos]
        if not idx_list:
            return None
        wells_xy = tree_data[idx_list]
        dists = np.linalg.norm(wells_xy - nitr_xy[sample_pos], axis=1)
        return idx_list, [sample_id] * len(idx_list), dists

    def _align(self):
        nitr = self.nitrate_gdf.to_crs(28992).reset_index(drop=False)
        nitr_xy = np.vstack(nitr.geometry.apply(lambda g: (g.x, g.y)).to_numpy())
        n_jobs = self.n_jobs

        sample_indices = np.arange(len(nitr))
        n_chunks = n_jobs * 4  # Or even more if you want
        chunk_indices = np.array_split(sample_indices, n_chunks)
        nitr_values = nitr['index'].values

        # Only pass coordinates, not KDTree objects or giant arrays
        well_coords = np.vstack(self.wells.geometry.apply(lambda g: (g.x, g.y)).to_numpy())

        from itertools import repeat
        with ProcessPoolExecutor(max_workers=n_jobs) as executor:
            chunk_results = list(
                executor.map(
                    process_chunk,
                    chunk_indices,
                    repeat(well_coords),
                    repeat(nitr_values),
                    repeat(nitr_xy),
                    repeat(self.radius),
                )
            )

        # --- Merge results from all chunks
        flat_well_idx, flat_sample_idx, flat_dist = [], [], []
        for widx, sidx, dist in chunk_results:
            flat_well_idx.extend(widx)
            flat_sample_idx.extend(sidx)
            flat_dist.extend(dist)

        if not flat_well_idx:
            raise ValueError("No wells found inside the search radius")

        flat_well_idx = np.asarray(flat_well_idx, dtype=np.intp)
        flat_sample_idx = np.asarray(flat_sample_idx, dtype=np.intp)
        flat_dist = np.asarray(flat_dist, dtype=float)

        df_pairs = pd.DataFrame({
            "nitrate_index": flat_sample_idx,
            "Well_ID": self.well_ids[flat_well_idx],
            "distance_m": flat_dist,
        })

        # The rest as before (not chunked, vectorized)
        df_pairs = df_pairs.merge(
            nitr[["index", "date"]],
            left_on="nitrate_index",
            right_on="index",
            how="left",
        ).drop(columns="index")

        merged = df_pairs.merge(self.depth_roll, on="Well_ID", how="left")

        w = self.window
        ok = (merged["Date_bin"] >= merged["date"] - pd.Timedelta(days=w)) & (
            merged["Date_bin"] <= merged["date"]
        )
        merged = merged[ok]

        merged = (
            merged.sort_values(["nitrate_index", "distance_m"])
            .drop_duplicates("nitrate_index")
        )

        out = nitr.merge(
            merged,
            left_on="index",
            right_on="nitrate_index",
            how="left",
            suffixes=("_nitr", "_depth"),
        )

        out = out.rename(
            columns={
                "Well_ID_nitr": "Well_ID",
                "groundwater_depth": "groundwater_depth",
                "date_nitr": "date",
            }
        )
        to_drop = [c for c in ["Well_ID_depth", "date_depth"] if c in out.columns]
        if to_drop:
            out = out.drop(columns=to_drop)

        if self.connect_to == "nitrate_data":
            return out[
                [
                    "Well_ID",
                    "bro-id",
                    "Filter",
                    "date",
                    "nitrate",
                    "geometry",
                    "distance_m",
                    "groundwater_depth",
                ]
            ]
        else:
            return out[["date", "geometry", "distance_m", "groundwater_depth"]]

def process_chunk(indices, well_coords, nitr_values, nitr_xy, radius):
    from scipy.spatial import cKDTree  # must be in the worker
    import numpy as np
    tree = cKDTree(well_coords)
    flat_well_idx, flat_sample_idx, flat_dist = [], [], []
    for sample_pos in indices:
        idx_list = tree.query_ball_point(nitr_xy[sample_pos], r=radius)
        if not idx_list:
            continue
        wells_xy = well_coords[idx_list]
        dists = np.linalg.norm(wells_xy - nitr_xy[sample_pos], axis=1)
        flat_well_idx.extend(idx_list)
        flat_sample_idx.extend([nitr_values[sample_pos]] * len(idx_list))
        flat_dist.extend(dists)
    return flat_well_idx, flat_sample_idx, flat_dist

# ---------------------

# import numpy as np
# import pandas as pd
# import os
# from itertools import repeat
# import geopandas as gpd
# from scipy.spatial import cKDTree
# from datetime import timedelta
# from joblib import Parallel, delayed

# try:
#     from .align_data import BaseAligner
# except ImportError:
#     from align_data import BaseAligner

# import warnings
# warnings.filterwarnings("ignore", category=FutureWarning, message=".*GeoDataFrame.swapaxes.*")


# def process_kdtree_chunk(chunk_indices, well_points, sample_points, radius, sample_ids):
#     # This runs in a subprocess!
#     from scipy.spatial import cKDTree
#     tree = cKDTree(well_points)
#     results = []
#     for idx in chunk_indices:
#         neighbors = tree.query_ball_point(sample_points[idx], r=radius)
#         if neighbors:
#             dists = np.linalg.norm(well_points[neighbors] - sample_points[idx], axis=1)
#             results.append((sample_ids[idx], neighbors, dists))
#     return results

# def rolling_for_one_well(df, window_days):
#     df = df.sort_values('Date_bin')
#     df = df.set_index('Date_bin')
#     rolled = (
#         df['Depth']
#         .rolling(f'{window_days}D', closed='both')
#         .mean()
#         .reset_index()
#         .rename(columns={'Depth': 'groundwater_depth'})
#     )
#     rolled['Well_ID'] = df['Well_ID'].iloc[0]
#     return rolled

# def parallel_rolling(depth_gdf, window_days, n_jobs=8):
#     results = Parallel(n_jobs=n_jobs)(
#         delayed(rolling_for_one_well)(well_df, window_days)
#         for _, well_df in depth_gdf.groupby('Well_ID')
#     )
#     return pd.concat(results, ignore_index=True)


# class DepthAligner(BaseAligner):
#     def __init__(self, provinces, well_filter: int, connect_to, years, days_window=72, radius=6000, n_jobs=8) -> None:
#         super().__init__(provinces, well_filter, connect_to, years)
#         self.window = days_window
#         self.radius = radius
#         self.n_jobs = n_jobs
#         self._prepare_depth(provinces, well_filter)
#         self._dataframe = self._align()

#     def _prepare_depth(self, provinces, well_filter):
#         depth = []
#         for pr in provinces:
#             f = f"../data/clean/well_depth_data/for_Alignment/{pr}_well_depth_combined_{well_filter}.csv"
#             if os.path.exists(f):
#                 depth.append(pd.read_csv(f, parse_dates=['Date']))
#         depth = pd.concat(depth, ignore_index=True)
#         self.depth_gdf = self._to_gdf(depth).to_crs(28992)

#         # rolling 72-day mean per well, in parallel!
#         d = self.depth_gdf
#         d['Date_bin'] = d['Date'].dt.floor('1D')
#         d = d.sort_values(['Well_ID', 'Date_bin'])

#         self.depth_roll = parallel_rolling(d, self.window, n_jobs=self.n_jobs)

#         # wells geometry for KD-tree
#         self.wells = (
#             self.depth_gdf[['Well_ID', 'geometry']]
#             .drop_duplicates()
#             .set_index('Well_ID')
#             .to_crs(28992)
#         )
#         self.well_coords = np.vstack(self.wells.geometry.apply(lambda g: (g.x, g.y)).to_numpy())
#         self.well_ids = self.wells.index.to_numpy()

#     def _align(self):
#         from concurrent.futures import ProcessPoolExecutor

#         nitr = self.nitrate_gdf.to_crs(28992).reset_index(drop=False)
#         nitr_xy = np.vstack(nitr.geometry.apply(lambda g: (g.x, g.y)).to_numpy())
#         sample_ids = nitr['index'].values
#         n_jobs = self.n_jobs

#         # Chunking for good load balance
#         n_chunks = n_jobs * 4
#         chunk_indices = np.array_split(np.arange(len(nitr)), n_chunks)

#         # --- Run KDTree search in parallel ---
#         with ProcessPoolExecutor(max_workers=n_jobs) as executor:
#             chunk_results = list(
#                 executor.map(
#                     process_kdtree_chunk,
#                     chunk_indices,
#                     repeat(self.well_coords),
#                     repeat(nitr_xy),
#                     repeat(self.radius),
#                     repeat(sample_ids),
#                 )
#             )

#         # --- Flatten and merge results ---
#         # Each result is a list of (sample_id, [neighbor_indices], [dists])
#         flat_well_idx, flat_sample_idx, flat_dist = [], [], []
#         for chunk in chunk_results:
#             for sample_id, neighbors, dists in chunk:
#                 flat_well_idx.extend(neighbors)
#                 flat_sample_idx.extend([sample_id] * len(neighbors))
#                 flat_dist.extend(dists)

#         if not flat_well_idx:
#             raise ValueError("No wells found inside the search radius")

#         flat_well_idx = np.asarray(flat_well_idx, dtype=np.intp)
#         flat_sample_idx = np.asarray(flat_sample_idx, dtype=np.intp)
#         flat_dist = np.asarray(flat_dist, dtype=float)

#         df_pairs = pd.DataFrame({
#             "nitrate_index": flat_sample_idx,
#             "Well_ID": self.well_ids[flat_well_idx],
#             "distance_m": flat_dist,
#         })

#         # The rest as before (not chunked, vectorized)
#         df_pairs = df_pairs.merge(
#             nitr[["index", "date"]],
#             left_on="nitrate_index",
#             right_on="index",
#             how="left",
#         ).drop(columns="index")

#         merged = df_pairs.merge(self.depth_roll, on="Well_ID", how="left")

#         w = self.window
#         ok = (merged["Date_bin"] >= merged["date"] - pd.Timedelta(days=w)) & (
#             merged["Date_bin"] <= merged["date"]
#         )
#         merged = merged[ok]

#         merged = (
#             merged.sort_values(["nitrate_index", "distance_m"])
#             .drop_duplicates("nitrate_index")
#         )

#         out = nitr.merge(
#             merged,
#             left_on="index",
#             right_on="nitrate_index",
#             how="left",
#             suffixes=("_nitr", "_depth"),
#         )

#         out = out.rename(
#             columns={
#                 "Well_ID_nitr": "Well_ID",
#                 "groundwater_depth": "groundwater_depth",
#                 "date_nitr": "date",
#             }
#         )
#         to_drop = [c for c in ["Well_ID_depth", "date_depth"] if c in out.columns]
#         if to_drop:
#             out = out.drop(columns=to_drop)

#         if self.connect_to == "nitrate_data":
#             return out[
#                 [
#                     "Well_ID",
#                     "bro-id",
#                     "Filter",
#                     "date",
#                     "nitrate",
#                     "geometry",
#                     "distance_m",
#                     "groundwater_depth",
#                 ]
#             ]
#         else:
#             return out[["date", "geometry", "distance_m", "groundwater_depth"]]


if __name__ == "__main__":
    well_filter = 1
    window = 72
    radius = 6000
    connect_to = "grid_data"
    provinces = ["utrecht"]
    years = [2022]

    instance = DepthAligner(provinces, well_filter, connect_to, years, window, radius, n_jobs=8)
    print(instance.dataframe)
    instance._dataframe.to_csv("depth_temp.csv")
