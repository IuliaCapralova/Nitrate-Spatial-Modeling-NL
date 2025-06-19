import os
import re
import geopandas as gpd

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

    def _align(self, path, column, predicate):
        # find overlap in years between nitrate and landuse datasets
        nitrate_gdf = self.nitrate_gdf
        nitrate_years = set(nitrate_gdf["Year"].unique())
        dataframe_years = set(self._extract_years_from_filenames(path))
        overlap_years = nitrate_years.intersection(dataframe_years)
        print(sorted(overlap_years))

        for year in sorted(overlap_years):
            # Get nitrate rows for this year
            nitrate_year = nitrate_gdf[nitrate_gdf["Year"] == year].copy()

            file = self._find_year_file(path, year)
            if not file:
                print(f"No file found for year {year}")
                continue

            file_path = os.path.join(path, file)
            gdf = gpd.read_file(file_path)

            # spatial join
            joined = self._spatial_join_by_year(nitrate_year, gdf, column, predicate)
            # print(joined)

            column_map = {
                "aantal_inwoners": "population",
                "code": "landuse code",
                "deposition_kg": "n deposition"
                }
            target_column = column_map.get(column)

            nitrate_gdf.loc[
                nitrate_gdf["geometry"].isin(joined["geometry"]) &
                nitrate_gdf["date"].isin(joined["date"]),
                target_column
            ] = joined[column].values

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


if __name__ == "__main__":
    pass
