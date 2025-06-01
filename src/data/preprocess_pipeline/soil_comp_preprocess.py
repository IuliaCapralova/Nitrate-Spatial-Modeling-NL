import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pyogrio")

import os
import pandas as pd
import geopandas as gpd
from .spatial_data import SpatialData


class Soil_Composition_Prepocess(SpatialData):
    LAYERS = ["soilarea", "soilarea_normalsoilprofile", "soilhorizon", "soilarea_soilunit"]
    MERGE_PLAN = [
    ("soilarea_soilunit", "maparea_id"),
    ("soilarea_normalsoilprofile", "maparea_id"),
    ("soilhorizon", "normalsoilprofile_id")
    ]
    COLUMN_SELECTION = ["maparea_collection", "beginlifespan", "endlifespan", "staringseriesblock", "inspireid", "validfrom", "beginlifespanversion", "soilunit_sequencenumber"]

    def __init__(self, layer_list):
        super().__init__(type_of_data="soil_composition")
        self.layer_list = layer_list
        self._dataframe = {}
        self._datapaths = self._paths_finder()
        self._populate_dataframe()

    # --------- preprocess part -----------

    def _preprocess(self, file_path: str):
        layers = self._read_all_layers(file_path)
        combined_gdf = self._merge_layers(layers)
        cropped_file = self._crop_file(combined_gdf)
        reduced_file = self._drop_columns(cropped_file) # remove columns that do not include features
        return reduced_file
    
    def _read_all_layers(self, file_path: str) -> dict:
        layers = {}
        for layer in self.LAYERS:
            gdf = gpd.read_file(file_path, layer=layer)
            
            # select only 0th sequence number (as it describes main soil type)
            if layer == "soilarea_soilunit":
                gdf = gdf[gdf["soilunit_sequencenumber"] == 0].copy()
            
            layers[layer] = gdf
        return layers
    
    def _merge_layers(self, tables: dict) -> gpd.GeoDataFrame:
        merged = tables["soilarea"] # base

        for right_name, on_key in self.MERGE_PLAN:
            right = tables[right_name]
            merged = pd.merge(merged, right, on=on_key, how="left")

        merged_gdf = gpd.GeoDataFrame(merged, geometry="geometry", crs=merged.crs)
        return merged_gdf
    
    def _drop_columns(self, gdf):
        gdf = gdf.drop(columns=self.COLUMN_SELECTION)
        return gdf

    # ------------------------------

    def _paths_finder(self):
        files_paths = []
        for file_name in os.listdir(self._datasetdir):
            if not file_name.endswith(".gpkg") or file_name.startswith("."):
                continue
            full_path = os.path.join(self._datasetdir, file_name)
            files_paths.append(full_path)
        return files_paths
    
    def _populate_dataframe(self):
        for file_path in self._datapaths:
            # preprocess function will take care of merging tables, cropping and selecting relevant columns
            final_gdf = self._preprocess(file_path)
            self._dataframe = self._gdf_separator_by_layer(final_gdf) # creates several gdf, one per layer number

    def _gdf_separator_by_layer(self, gdf):
        if "layernumber" not in gdf.columns:
            raise KeyError("Expected 'layernumber' column is missing from the merged GeoDataFrame.")

        dictionary_by_layer = {}
        for soil_layer_number in self.layer_list:
            dictionary_by_layer[f"layernumber_{soil_layer_number}"] = gdf[gdf["layernumber"]==soil_layer_number].copy()

        return dictionary_by_layer

if __name__ == "__main__":
    layer_list = [1]
    instance = Soil_Composition_Prepocess(layer_list)
    df = instance._dataframe
    print(df)

    # # check if we have duplicated geometries in each table
    # for layer_name, gdf in df.items():
    #     geom_col = gdf.geometry.name  # gets the geometry column name
    #     duplicated_mask = gdf[geom_col].apply(lambda g: g.wkt).duplicated(keep=False)
    #     num_duplicates = duplicated_mask.sum()

    # print(f"Layer: {layer_name} → {num_duplicates} duplicated geometries")
