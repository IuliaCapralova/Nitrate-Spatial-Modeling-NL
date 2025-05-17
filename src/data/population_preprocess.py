import fiona
import re
import os
import numpy as np
import geopandas as gpd
from spatial_data import SpatialData


class Population_Prepocess(SpatialData):
    COLUMN_SELECTION = ['aantal_inwoners', 'geometry']
    AVAILABLE_YEARS = set(range(2000, 2024)) # actually till 2023

    def __init__(self, years:list[int]):
        invalid_years = [year for year in years if year not in self.AVAILABLE_YEARS]
        if invalid_years:
            raise ValueError(
                f"The following year(s) are unavailable: {invalid_years}. "
                f"Available years are: {sorted(self.AVAILABLE_YEARS)}")

        super().__init__(type_of_data="population_density")
        self.year_list = years
        self._dataframe = {}
        self._datasetdir = os.path.join(self._datasetdir, "500m")
        self._datapaths = self._paths_finder()
        self._populate_dataframe()

    # --------- preprocess part -----------

    def _preprocess(self, file_path):
        # for each file apply all preprocessing steps
        pop_gdf = self._read_gpkg(file_path)
        reduced_file = self._column_selection(pop_gdf, self.COLUMN_SELECTION)
        cropped_file = self._crop_file(reduced_file)
        final_gdf = self._impute_values(cropped_file)
        return final_gdf

    def _read_gpkg(self, file_path):
        # read file
        layers = fiona.listlayers(file_path)
        pop_gdf = gpd.read_file(file_path, layer=layers[0])
        return pop_gdf
    
    def _impute_values(self, gdf):
        gdf.loc[gdf['aantal_inwoners'] < 0, 'aantal_inwoners'] = np.nan
        gdf = gdf.fillna(0)       # fill all missing values with '0'
        return gdf

    # ------------------------------

    def _paths_finder(self):
        pop_files_paths = []
        for file_name in os.listdir(self._datasetdir):
            if not file_name.endswith(".gpkg") or file_name.startswith("."):
                continue
            match = re.search(r'\d{4}', file_name)
            year = int(match.group(0))
            if year not in self.year_list:
                continue
            full_path = os.path.join(self._datasetdir, file_name)
            pop_files_paths.append(full_path)
        return pop_files_paths
    
    def _populate_dataframe(self):
        for file_path in self._datapaths:
            final_gdf = self._preprocess(file_path)
            file_name = os.path.splitext(os.path.basename(file_path))[0]  # no extension
            self._dataframe[file_name] = final_gdf


if __name__ == "__main__":
    years = [2000, 2020]
    instance = Population_Prepocess(years)
    print(instance._dataframe)
