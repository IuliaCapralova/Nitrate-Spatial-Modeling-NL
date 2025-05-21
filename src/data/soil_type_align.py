import pandas as pd
import os
import fiona
import geopandas as gpd
from align_data import BaseAligner


class SoilTypeAligner(BaseAligner):
    def __init__(self, well_filter: int) -> None:
        super().__init__(well_filter)
        soil_type_path = os.path.join(self.current_dir, "data", "clean", "type_of_soil", "LMM14_HGR_processed.gpkg")
        layers = fiona.listlayers(soil_type_path)
        self.soil_type_df = gpd.read_file(soil_type_path, layer=layers[0])

        self._dataframe = self._align()

    def _align(self):
        self.soil_type_gdf = self.soil_type_df.to_crs("EPSG:4326") 
        nitrate_with_soil = gpd.sjoin(
            self.nitrate_gdf,
            self.soil_type_gdf[["geometry", "HGRnaam"]],
            how="left",
            predicate="within"
        )
        nitrate_with_soil = nitrate_with_soil.drop(columns=["index_right"])
        return nitrate_with_soil

if __name__ == "__main__":
    instance = SoilTypeAligner(well_filter=1)
    print(instance._dataframe.head(30))
