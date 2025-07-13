import os
import fiona
import geopandas as gpd

try:
    from .align_data import BaseAligner
except ImportError:
    from align_data import BaseAligner


class SoilTypeAligner(BaseAligner):
    def __init__(self, provinces, well_filter: int, connect_to, years) -> None:
        super().__init__(provinces, well_filter, connect_to, years)
        soil_type_path = os.path.join(self.current_dir, "../data", "clean", "type_of_soil", "LMM14_HGR_processed.gpkg")
        layers = fiona.listlayers(soil_type_path)
        self.soil_type_df = gpd.read_file(soil_type_path, layer=layers[0])

        self._dataframe = self._align()

    def _align(self):
        self.soil_type_gdf = self.soil_type_df.to_crs(self.nitrate_gdf.crs)
        self.soil_type_gdf = self.soil_type_gdf.rename(columns={"HGRnaam":"soil region"})
        nitrate_with_soil = gpd.sjoin(
            self.nitrate_gdf,
            self.soil_type_gdf[["geometry", "soil region"]],
            how="left",
            predicate="within"
        )
        print("Point CRS:", self.nitrate_gdf.crs)
        print("Polygon CRS:", self.soil_type_gdf.crs)
        nitrate_with_soil = nitrate_with_soil.drop(columns=["index_right"])
        return nitrate_with_soil


if __name__ == "__main__":
    provinces = ["flevoland"]
    well_filter = 1
    connect_to = "grid_data"
    years = [2010]

    instance = SoilTypeAligner(provinces, well_filter=1, connect_to=connect_to, years=years)
    print(instance.dataframe)
    instance.dataframe.to_csv("soil_type_align.csv", index=False)
