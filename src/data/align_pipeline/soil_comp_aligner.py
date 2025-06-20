import os
import fiona
import re
import geopandas as gpd
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

try:
    from .align_data import BaseAligner
except ImportError:
    from align_data import BaseAligner


class Soil_Composition_Aligner(BaseAligner):
    def __init__(self, provinces, well_filter, connect_to, years, layer_list=[1]):
        super().__init__(provinces, well_filter, connect_to, years)
        self.layer_list = layer_list   # user's layer selection
        self._datasetdir = os.path.join(self.current_dir, "../data", "clean", "soil_composition")
        self._file_paths = self._path_finder()
        self._dataframe = self._align()

    # def _align(self):
    #     merged = self.nitrate_gdf
    #     print(merged)

    #     for path in self._file_paths:
    #         # makes sure we assign layer number to features after alignment
    #         match = re.search(r"\d+", os.path.basename(path))

    #         if match:
    #             layer_number = int(match.group(0))
    #         else:
    #             continue  # Skip files without a digit

    #         # check that this layer is in user's list of layers
    #         if layer_number not in self.layer_list:
    #             continue

    #         suffix = f"_{layer_number}"

    #         layers = fiona.listlayers(path)
    #         gdf = gpd.read_file(path, layer=layers[0])
    #         gdf = gdf.to_crs(self.nitrate_gdf.crs)

    #         excluded = {"geometry", "maparea id", "normalsoilprofile id", "layernumber"}
    #         renamed_cols = {col: f"{col}{suffix}" for col in gdf.columns if col not in excluded}
    #         gdf = gdf.rename(columns=renamed_cols)

    #         #spatial join
    #         merged = gpd.sjoin(merged, gdf, how="left", predicate="within")
    #         merged = merged.drop(columns=["index_right"])

    #     return merged
    
    def _align(self):
        nitrate = self.nitrate_gdf.copy()
        print(nitrate)

        with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            futures = [
                executor.submit(
                    self._process_soil_layer,
                    path,
                    nitrate.crs,
                    nitrate,
                    self.layer_list
                )
                for path in self._file_paths
            ]

            results = [f.result() for f in futures if f.result() is not None]

        # Sequentially merge the enriched nitrate frames
        merged = nitrate
        for r in results:
            r = r.drop(columns=["geometry"])
            cols_to_drop = ["Well_ID", "bro-id", "date", "nitrate", "Filter", "Year"]
            merged = merged.join(r.drop(columns=cols_to_drop, errors="ignore"))


        return gpd.GeoDataFrame(merged, geometry="geometry", crs=nitrate.crs)
    
    def _process_soil_layer(self, path, nitrate_gdf_crs, nitrate_gdf, selected_layers):
        import geopandas as gpd
        import fiona
        import os
        import re

        # check layer number
        match = re.search(r"\d+", os.path.basename(path))
        if not match:
            return None
        layer_number = int(match.group(0))
        if layer_number not in selected_layers:
            return None

        suffix = f"_{layer_number}"
        layers = fiona.listlayers(path)
        gdf = gpd.read_file(path, layer=layers[0])
        gdf = gdf.to_crs(nitrate_gdf_crs)

        excluded = {"geometry", "maparea id", "normalsoilprofile id", "layernumber"}
        renamed_cols = {col: f"{col}{suffix}" for col in gdf.columns if col not in excluded}
        gdf = gdf.rename(columns=renamed_cols)

        # Perform spatial join
        joined = gpd.sjoin(nitrate_gdf, gdf, how="left", predicate="within")
        joined = joined.drop(columns=["index_right"])
        return joined

    def _path_finder(self):
        files_paths = []
        for file_name in os.listdir(self._datasetdir):
            if not file_name.endswith(".gpkg") or file_name.startswith("."):
                continue
            full_path = os.path.join(self._datasetdir, file_name)
            files_paths.append(full_path)
        return files_paths


if __name__ == "__main__":

# Index(['maparea_id', 'soilslope', 'normalsoilprofile_id', 'layernumber',
#        'faohorizonnotation', 'lowervalue', 'uppervalue',
#        'organicmattercontent', 'minimumorganicmattercontent',
#        'maximumorganicmattercontent', 'acidity', 'minimumacidity',
#        'maximumacidity', 'cnratio', 'peattype', 'calciccontent', 'fedith',
#        'loamcontent', 'minimumloamcontent', 'maximumloamcontent',
#        'lutitecontent', 'minimumlutitecontent', 'maximumlutitecontent',
#        'sandmedian', 'minimumsandmedian', 'maximumsandmedian', 'siltcontent',
#        'density', 'soilunit_code', 'geometry']

    layer_list = [1]
    well_filter = 1
    var_list = ["soilunit_code_1", "organicmattercontent_1", "density_1", "mainsoilclassification_1"]
    provinces = ["utrecht", "flevoland"]
    connect_to = 'nitrate_data'
    years = [2010]

    instance = Soil_Composition_Aligner(provinces, well_filter, connect_to, years, layer_list)

    print(instance.dataframe)
    # print(type(instance.get_variable(name=var_list)))
    # instance._dataframe.to_csv("soil_comp_temp.csv")
