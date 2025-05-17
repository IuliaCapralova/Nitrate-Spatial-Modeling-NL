import pandas as pd
import os
import geopandas as gpd
from align_data import BaseAligner


class SoilTypeAligner(BaseAligner):
    def __init__(self, well_filter: int) -> None:
        super().__init__(well_filter)
        soil_type_path = os.path.join(self.current_dir, "data", "raw", "type_of_soil_data", "LMM14_HGR.shp")
        self.soil_type_df = gpd.read_file(soil_type_path)
        joined = self._align()

    def _align(self):
        self.soil_type_gdf = self.soil_type_df.to_crs("EPSG:4326") 
        nitrate_with_soil = gpd.sjoin(
            self.nitrate_gdf,
            self.soil_type_gdf[["geometry", "groep"]],
            how="left",
            predicate="within"
        )
        nitrate_with_soil = nitrate_with_soil.drop(columns=["index_right"])
        return nitrate_with_soil

if __name__ == "__main__":
    instance = SoilTypeAligner(well_filter=1)
    joined = instance._align()
    print(joined)
