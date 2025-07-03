import os
import re
import geopandas as gpd
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

try:
    from .align_data import BaseAligner
except ImportError:
    from align_data import BaseAligner


class SpatialTimeseriesBaseAligner(BaseAligner):
    def __init__(self, provinces:list[str], well_filter=1, connect_to='nitrate_data', years=[2010]):
        super().__init__(provinces, well_filter, connect_to, years)

    def _extract_years_from_filenames(self, path):
        """Get all available land use years from filenames."""
        years = []
        for fname in os.listdir(path):
            match = re.search(r"\d{4}", fname)
            if match:
                years.append(int(match.group(0)))
        return years

    # def _align(self, path, column, predicate):
    #     # find overlap in years between nitrate and landuse datasets
    #     nitrate_gdf = self.nitrate_gdf
    #     nitrate_years = set(nitrate_gdf["Year"].unique())
    #     dataframe_years = set(self._extract_years_from_filenames(path))
    #     overlap_years = nitrate_years.intersection(dataframe_years)
    #     print(sorted(overlap_years))

    #     for year in sorted(overlap_years):
    #         # Get nitrate rows for this year
    #         nitrate_year = nitrate_gdf[nitrate_gdf["Year"] == year].copy()

    #         file = self._find_year_file(path, year)
    #         if not file:
    #             print(f"No file found for year {year}")
    #             continue

    #         file_path = os.path.join(path, file)
    #         gdf = gpd.read_file(file_path)

    #         # spatial join
    #         joined = self._spatial_join_by_year(nitrate_year, gdf, column, predicate)
    #         # print(joined)

    #         column_map = {
    #             "aantal_inwoners": "population",
    #             "code": "landuse code",
    #             "deposition_kg": "n deposition"
    #             }
    #         target_column = column_map.get(column)

    #         nitrate_gdf.loc[
    #             nitrate_gdf["geometry"].isin(joined["geometry"]) &
    #             nitrate_gdf["date"].isin(joined["date"]),
    #             target_column
    #         ] = joined[column].values

    #     return nitrate_gdf

    @staticmethod
    def _process_year(year, nitrate_gdf_year, file_path, column, predicate, column_map):
        import geopandas as gpd

        try:
            gdf = gpd.read_file(file_path)
            gdf = gdf.to_crs(nitrate_gdf_year.crs)

            joined = gpd.sjoin(
                nitrate_gdf_year,
                gdf[[column, "geometry"]],
                how="left",
                predicate=predicate
            )

            target_column = column_map.get(column)
            joined = joined[["geometry", "date", column]]
            joined.rename(columns={column: target_column}, inplace=True)

            return joined
        except Exception as e:
            print(f"Failed to process year {year}: {e}")
            return None
        
    def _align(self, path, column, predicate):
        nitrate_gdf = self.nitrate_gdf.copy()
        nitrate_years = set(nitrate_gdf["Year"].unique())
        dataframe_years = set(self._extract_years_from_filenames(path))
        overlap_years = nitrate_years.intersection(dataframe_years)
        print(sorted(overlap_years))

        column_map = {
            "aantal_inwoners": "population",
            "code": "landuse code",
            "deposition_kg": "n deposition"
        }

        jobs = []
        for year in sorted(overlap_years):
            file = self._find_year_file(path, year)
            if not file:
                continue
            nitrate_year_df = nitrate_gdf[nitrate_gdf["Year"] == year].copy()
            file_path = os.path.join(path, file)
            jobs.append((year, nitrate_year_df, file_path, column, predicate, column_map))

        with ProcessPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(run_process_year, jobs))

        # Drop None results
        results = [r for r in results if r is not None]

        # Merge back into main nitrate_gdf
        for joined in results:
            target_column = [c for c in joined.columns if c not in ["geometry", "date"]][0]
            mask = nitrate_gdf["geometry"].isin(joined["geometry"]) & nitrate_gdf["date"].isin(joined["date"])
            nitrate_gdf.loc[mask, target_column] = joined[target_column].values

        return nitrate_gdf

    def _find_year_file(self, path, year):
        return next(
            (f for f in os.listdir(path) if str(year) in f and f.endswith(".gpkg")),
            None)
    
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
