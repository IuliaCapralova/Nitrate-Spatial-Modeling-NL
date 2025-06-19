import os
import geopandas as gpd
from .spatial_data import SpatialData


class SoilType_Preprocess(SpatialData):
    COLUMN_SELECTION = ['HGRnaam', 'geometry']

    def __init__(self, provinces):
        super().__init__(provinces, type_of_data="type_of_soil")
        self._dataframe = {}
        self._datapaths = self._paths_finder()
        self._populate_dataframe()

    # --------- preprocess part -----------

    def _preprocess(self, file_path):
        # for each file apply all preprocessing steps
        soil_type_gdf = gpd.read_file(file_path)
        reduced_file = self._column_selection(soil_type_gdf, self.COLUMN_SELECTION)
        final_gdf = self._crop_file(reduced_file) 
        return final_gdf
    
    # ------------------------------
    
    def _paths_finder(self):
        files_paths = []
        for file_name in os.listdir(self._datasetdir):
            if not file_name.endswith(".shp"):
                continue
            full_path = os.path.join(self._datasetdir, file_name)
            files_paths.append(full_path)
        return files_paths

    def _populate_dataframe(self):
        file_path = self._datapaths[0]
        final_gdf = self._preprocess(file_path)
        file_name = os.path.splitext(os.path.basename(file_path))[0]  # no extension
        self._dataframe[file_name] = final_gdf


if __name__ == "__main__":
    instance = SoilType_Preprocess()
    print(instance._dataframe)
