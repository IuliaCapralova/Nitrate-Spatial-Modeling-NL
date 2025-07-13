import os
import re
import rasterio
import pandas as pd
import numpy as np
import geopandas as gpd
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

try:
    from .align_data import BaseAligner
except ImportError:
    from align_data import BaseAligner


class SpatialTimeseriesBaseAligner(BaseAligner):
    def __init__(self, provinces:list[str], well_filter, connect_to, years):
        super().__init__(provinces, well_filter, connect_to, years)

    @staticmethod
    def _process_year(year, nitrate_gdf_year, file_path,
                    column, predicate, column_map):
        """
        • If `column == "code"`  → sample the land-use GeoTIFF
        • else                  → keep the original vector spatial-join
        """
        try:
            if column == "code":                        # ── LAND-USE ──
                with rasterio.open(file_path) as src:
                    pts = nitrate_gdf_year.to_crs(src.crs)

                    coords = [(g.x, g.y) if g.geom_type == "Point"
                            else g.centroid.coords[0]
                            for g in pts.geometry]
                    values = [v[0] for v in src.sample(coords)]
                    values = np.where(np.equal(values, src.nodata),
                                    np.nan, values)

                # target = column_map[column]
                # pts[target] = values
                # pts = pts.to_crs(nitrate_gdf_year.crs)
                # joined = pts[["geometry", "date", target]]

                target = column_map[column]

                # Create a 1-column frame; keep the original index
                joined = pd.DataFrame({target: values}, index=nitrate_gdf_year.index)
                return joined                          # index is preserved

            else:                                       # ── OTHER DATA ──
                gdf = gpd.read_file(file_path)          # .gpkg
                gdf = gdf.to_crs(nitrate_gdf_year.crs)
                joined = gpd.sjoin(
                    nitrate_gdf_year,
                    gdf[[column, "geometry"]],
                    how="left",
                    predicate=predicate
                )
                target = column_map[column]
                joined = joined[["geometry", "date", column]]
                joined.rename(columns={column: target}, inplace=True)
                joined = joined[[target]]
                return joined 

        except Exception as e:
            print(f"Year {year}: {e}")
            return None

    def _extract_years_from_filenames(self, path):
        """Get all available land use years from filenames."""
        years = []
        for fname in os.listdir(path):
            match = re.search(r"\d{4}", fname)
            if match:
                years.append(int(match.group(0)))
        return years

    # @staticmethod
    # def _process_year(year, nitrate_gdf_year, file_path, column, predicate, column_map):
    #     import geopandas as gpd

    #     try:
    #         gdf = gpd.read_file(file_path)
    #         gdf = gdf.to_crs(nitrate_gdf_year.crs)

    #         joined = gpd.sjoin(
    #             nitrate_gdf_year,
    #             gdf[[column, "geometry"]],
    #             how="left",
    #             predicate=predicate
    #         )

    #         target_column = column_map.get(column)
    #         joined = joined[["geometry", "date", column]]
    #         joined.rename(columns={column: target_column}, inplace=True)

    #         return joined
    #     except Exception as e:
    #         print(f"Failed to process year {year}: {e}")
    #         return None
        
    # def _align(self, path, column, predicate):
    #     nitrate_gdf = self.nitrate_gdf.copy()
    #     nitrate_years = set(nitrate_gdf["Year"].unique())
    #     dataframe_years = set(self._extract_years_from_filenames(path))
    #     overlap_years = nitrate_years.intersection(dataframe_years)
    #     print(sorted(overlap_years))

    #     column_map = {
    #         "aantal_inwoners": "population",
    #         "code": "landuse code",
    #         "deposition_kg": "n deposition"
    #     }

    #     jobs = []
    #     for year in sorted(overlap_years):
    #         file = self._find_year_file(path, year)
    #         if not file:
    #             continue
    #         nitrate_year_df = nitrate_gdf[nitrate_gdf["Year"] == year].copy()
    #         file_path = os.path.join(path, file)
    #         jobs.append((year, nitrate_year_df, file_path, column, predicate, column_map))

    #     with ProcessPoolExecutor(max_workers=5) as executor:
    #         results = list(executor.map(run_process_year, jobs))

    #     # Drop None results
    #     results = [r for r in results if r is not None]

    #     # Merge back into main nitrate_gdf
    #     for joined in results:
    #         target_column = [c for c in joined.columns if c not in ["geometry", "date"]][0]
    #         mask = nitrate_gdf["geometry"].isin(joined["geometry"]) & nitrate_gdf["date"].isin(joined["date"])
    #         nitrate_gdf.loc[mask, target_column] = joined[target_column].values

    #     return nitrate_gdf

    def _align(self, path, column, predicate):
        self.current_column = column
        nitrate_gdf = self.nitrate_gdf.copy()
        nitrate_years = set(nitrate_gdf["Year"].unique())
        available_years = set(self._extract_years_from_filenames(path))

        # Column → final column name
        column_map = {
            "aantal_inwoners": "population",
            "code": "landuse code",
            "deposition_kg": "n deposition"
        }

        # Only apply fallback for land use (column == 'code')
        fallback_map = {}
        if column == "code":
            fallback_map = {
                2009: 2008,
                2010: 2012,
                2011: 2012,
                2013: 2012,
                2014: 2012,
                2015: 2018,
                2016: 2018,
                2017: 2018
            }

        jobs = []
        for year in sorted(nitrate_years):
            # Determine which land use year to use
            if column == "code":
                landuse_year = year if year in available_years else fallback_map.get(year)
            else:
                landuse_year = year if year in available_years else None

            if landuse_year not in available_years:
                print(f"Skipping year {year} — no suitable land use data found.")
                continue

            file = self._find_year_file(path, landuse_year)
            if not file:
                continue

            nitrate_year_df = nitrate_gdf[nitrate_gdf["Year"] == year].copy()
            file_path = os.path.join(path, file)
            jobs.append((year, nitrate_year_df, file_path, column, predicate, column_map))

        with ProcessPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(run_process_year, jobs))

        # Drop None results
        results = [r for r in results if r is not None]

        # Merge back
        for joined in results:
            # works for both variants:  joined has exactly one data column
            target_column = joined.columns[0]
            nitrate_gdf.loc[joined.index, target_column] = joined[target_column]

        return nitrate_gdf

    def _find_year_file(self, path, year):
        if self.current_column == "code":          # set below in _align()
            ext = ".tif"
        else:
            ext = ".gpkg"

        return next(
            (f for f in os.listdir(path)
            if str(year) in f and f.endswith(ext)),
            None
        )
    
    def _spatial_join_by_year(self, nitrate_subset, gdf, column, predicate):
        gdf = gdf.to_crs(nitrate_subset.crs)
        return gpd.sjoin(
            nitrate_subset,
            gdf[[column, "geometry"]],
            how="left",
            predicate=predicate
        )


def run_process_year(job):
    # from align_spatial import SpatialTimeseriesBaseAligner
    year, nitrate_gdf_year, file_path, column, predicate, column_map = job
    return SpatialTimeseriesBaseAligner._process_year(year, nitrate_gdf_year, file_path, column, predicate, column_map)


if __name__ == "__main__":
    pass
