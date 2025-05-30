import fiona
import re
import os
import pandas as pd
import numpy as np
import geopandas as gpd
import periodictable as pt
from spatial_data import SpatialData


class N_Deposition_Prepocess(SpatialData):
    COLUMN_SELECTION = ['deposition_kg', 'geometry']
    AVAILABLE_YEARS = set(range(2005, 2024)) # actually till 2023
    MOLAR_MASS_N = pt.elements.symbol('N').mass
    GRAMS_TO_KILOGRAMS = 1000

    def __init__(self, years:list[int]):
        invalid_years = [year for year in years if year not in self.AVAILABLE_YEARS]
        if invalid_years:
            raise ValueError(
                f"The following year(s) are unavailable: {invalid_years}. "
                f"Available years are: {sorted(self.AVAILABLE_YEARS)}")

        super().__init__(type_of_data="n_deposition")
        self.year_list = years
        self._dataframe = {}
        self._datapaths = self._paths_finder()
        self._populate_dataframe()

    # --------- preprocess part -----------

    def _preprocess(self, file_path, layer):
        gdf = self._read_gpkg(file_path, layer)
        cropped_file = self._crop_file(gdf)
        gdf_kg_units = self._unit_changer(cropped_file)
        reduced_file = self._column_selection(gdf_kg_units, self.COLUMN_SELECTION)
        return reduced_file

    def _unit_changer(self, gdf):
        gdf["deposition_kg"] = gdf["deposition"] * self.MOLAR_MASS_N / self.GRAMS_TO_KILOGRAMS
        return gdf

    def _read_gpkg(self, file_path, layer):
        # read file
        gdf = gpd.read_file(file_path, layer=layer)
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
            # for each layer in file apply all the preprocessing steps
            layers_gdf = self._layer_list_finder(file_path)
            for layer in layers_gdf:
                final_gdf = self._preprocess(file_path, layer)
                self._dataframe[layer] = final_gdf

    def _layer_list_finder(self, file_path):
        needed_layers = []
        layers = fiona.listlayers(file_path)
        for layer in layers:
            match = re.search(r'\d{4}', layer)
            if not match:
                continue
            year = int(match.group(0))
            if year not in self.year_list:
                continue
            needed_layers.append(layer)
        return needed_layers


if __name__ == "__main__":
    years = [2008, 2020]
    instance = N_Deposition_Prepocess(years)
    print(instance._dataframe)
