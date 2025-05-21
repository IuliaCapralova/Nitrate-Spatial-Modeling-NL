import os
import re
import geopandas as gpd
from align_data import BaseAligner


class SpatialBaseAligner(BaseAligner):
    def __init__(self, well_filter=1):
        super().__init__(well_filter)

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
        landuse_years = set(self._extract_years_from_filenames(path))
        overlap_years = nitrate_years.intersection(landuse_years)
        print(sorted(overlap_years))

        for year in sorted(overlap_years):
            # Get nitrate rows for this year
            nitrate_year = nitrate_gdf[nitrate_gdf["Year"] == year].copy()

            lu_file = next(
                (f for f in os.listdir(path) if str(year) in f and f.endswith(".gpkg")),
                None
            )
            print(lu_file)
            if not lu_file:
                print(f"No file found for year {year}")
                continue

            lu_path = os.path.join(path, lu_file)
            landuse_gdf = gpd.read_file(lu_path)
            landuse_gdf = landuse_gdf.to_crs(nitrate_year.crs)

            # spatial join
            joined = gpd.sjoin(
                nitrate_year,
                landuse_gdf[[column, "geometry"]],
                how="left",
                predicate=predicate
            )
            if column == 'aantal_inwoners':
                nitrate_gdf.loc[
                    nitrate_gdf["Well_ID"].isin(joined["Well_ID"]) &
                    nitrate_gdf["Date"].isin(joined["Date"]),
                    "Population"
                ] = joined[column].values
            else:
                nitrate_gdf.loc[
                    nitrate_gdf["Well_ID"].isin(joined["Well_ID"]) &
                    nitrate_gdf["Date"].isin(joined["Date"]),
                    "Landuse_Code"
                ] = joined[column].values

        return nitrate_gdf


if __name__ == "__main__":
    pass