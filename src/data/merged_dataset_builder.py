from functools import reduce
import pandas as pd
from fertilizer_align import FertilizerAnigner
from landuse_align import LanduseAligner
from population_align import PopulationAlignment
from statline_aligner import StatLineAligner
from soil_type_align import SoilTypeAligner
from depth_chem_align import DepthAligner
from elevation_align import ElevationAligner
from environment_chem_align import EnvironmentalAligner
from n_deposition_align import NDepositionAligner
from soil_comp_preprocess import Soil_Composition_Prepocess
from soil_comp_aligner import Soil_Composition_Aligner


class MergedDatasetBuilder:
    def __init__(self, variables: list[str], well_filter=1):
        self.variables = [v.lower() for v in variables]  # make lowercase user's variable selection
        self.well_filter = well_filter

        self.builder_map = {
            SoilTypeAligner: ["soil region"],
            LanduseAligner: ["landuse code"],
            PopulationAlignment: ["population"],
            DepthAligner: ["groundwater depth"],
            FertilizerAnigner: ["fertilizer"],
            ElevationAligner: ["elevation", "lon", "lat"],
            EnvironmentalAligner: ["precipitation", "temperature"],
            StatLineAligner: ["fertiliser use", "number of livestock", "excretion during grazing", \
                                "nitrogen losses in housing and storages", \
                                "use of livestock manure in agriculture",
                                "household organic waste"],
            NDepositionAligner: ["n deposition"],
            Soil_Composition_Aligner:['maparea_id', 'soilslope', 'normalsoilprofile_id', 'layernumber',
                                'faohorizonnotation', 'lowervalue', 'uppervalue',
                                'organicmattercontent', 'minimumorganicmattercontent',
                                'maximumorganicmattercontent', 'acidity', 'minimumacidity',
                                'maximumacidity', 'cnratio', 'peattype', 'calciccontent', 'fedith',
                                'loamcontent', 'minimumloamcontent', 'maximumloamcontent',
                                'lutitecontent', 'minimumlutitecontent', 'maximumlutitecontent',
                                'sandmedian', 'minimumsandmedian', 'maximumsandmedian', 'siltcontent',
                                'density', 'soilunit_code']
        }

        self._merged_dataframes = self._build_and_merge()

    def _build_and_merge(self):
        dfs = []
        for cls, supported_var in self.builder_map.items():
            selected_vars = [v for v in self.variables if v in supported_var]
            if not selected_vars:
                continue

            print(f"Initializing {cls.__name__} for {selected_vars}")
            instance = cls(self.well_filter)

    def _build_selected_dataframes(self):
        dfs = []
        for var in self.variables:
            print(f"Merging: {var}")
            cls = self.available_builders.get(var.lower())
            if cls is None:
                raise ValueError(f"Unknown variable: {var}")
            instance = cls(self.well_filter)
            dfs.append(instance._dataframe)
            print(dfs)
        return dfs

    def _merge_all(self, dfs, on="BRO-ID"):
        if not dfs:
            raise ValueError("No dataframes to merge.")

        base_df = dfs[0].copy()
        for df in dfs[1:]:
            # Only keep columns not already in base_df, excluding join key
            new_cols = [col for col in df.columns if col != on and col not in base_df.columns]
            df_subset = df[[on] + new_cols]
            base_df = pd.merge(base_df, df_subset, on=on, how="outer")
        return base_df
    
    @property
    def merged_dataframes(self):
        return self._merged_dataframes


if __name__ == "__main__":
    variables_of_interest = ['groundwater depth', 'population', 'soil type', 'landuse code', \
                 'precipitation', 'temperature', 'manure_and_waste', 'elevation', 'lon', \
                 'lat', 'n_deposition']
    
    merged_dataset = MergedDatasetBuilder(variables_of_interest)
    merged_dataset
    print(merged_dataset.merged_dataframes)
