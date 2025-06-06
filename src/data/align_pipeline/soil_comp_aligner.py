import os
import fiona
import re
import geopandas as gpd
from .align_data import BaseAligner


class Soil_Composition_Aligner(BaseAligner):
    def __init__(self, well_filter=1, layer_list=[1]):
        super().__init__(well_filter)
        self.layer_list = layer_list   # user's layer selection
        self._datasetdir = os.path.join(self.current_dir, "data", "clean", "soil_composition")
        self._file_paths = self._path_finder()
        self._dataframe = self._align()

    def _align(self):
        merged = self.nitrate_gdf
        print(merged)

        for path in self._file_paths:
            # makes sure we assign layer number to features after alignment
            match = re.search(r"\d+", os.path.basename(path))

            if match:
                layer_number = int(match.group(0))
            else:
                continue  # Skip files without a digit

            # check that this layer is in user's list of layers
            if layer_number not in self.layer_list:
                continue

            suffix = f"_{layer_number}"

            layers = fiona.listlayers(path)
            gdf = gpd.read_file(path, layer=layers[0])
            gdf = gdf.to_crs(self.nitrate_gdf.crs)

            excluded = {"geometry", "maparea id", "normalsoilprofile id", "layernumber"}
            renamed_cols = {col: f"{col}{suffix}" for col in gdf.columns if col not in excluded}
            gdf = gdf.rename(columns=renamed_cols)

            #spatial join
            merged = gpd.sjoin(merged, gdf, how="left", predicate="within")
            merged = merged.drop(columns=["index_right"])

        return merged

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
    instance = Soil_Composition_Aligner(well_filter, layer_list)
    print(instance._dataframe)
    # print(type(instance.get_variable(name=var_list)))
    # instance._dataframe.to_csv("temp.csv")
