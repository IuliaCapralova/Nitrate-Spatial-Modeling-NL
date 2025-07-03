import pandas as pd
import os
import geopandas as gpd
from .fertilizer_align import FertilizerAnigner
from .landuse_align import LanduseAligner
from .population_align import PopulationAlignment
from .statline_aligner import StatLineAligner
from .soil_type_align import SoilTypeAligner
from .depth_chem_align import DepthAligner
from .elevation_align import ElevationAligner
# from .environment_chem_align import EnvironmentalAligner
from align_pipeline.environment_chem_align import EnvironmentalAligner
from .n_deposition_align import NDepositionAligner
from .soil_comp_aligner import Soil_Composition_Aligner


class MergedDatasetBuilder:
    def __init__(self, variables: list[str], provinces, well_filter, connect_to, years):
        self.variables = [v.lower() for v in variables]  # make lowercase user's variable selection
        self.provinces = provinces
        self.well_filter = well_filter
        self.connect_to = connect_to
        self.years = years

        self.current_dir = os.getcwd()

        if self.connect_to == 'nitrate_data':
            # combine nitrate data from all needed provinces
            all_dfs = []
            for province in provinces:
                nitrate_dir = os.path.join(self.current_dir, '../data/clean', "well_chem_data", "for_Alignment", f"{province}_well_chem_combined_{well_filter}.csv")
                if os.path.exists(nitrate_dir):
                    df = pd.read_csv(nitrate_dir, parse_dates=['date'])
                    all_dfs.append(df)
                self.nitrate_df = pd.concat(all_dfs, ignore_index=True)

        elif self.connect_to == 'grid_data':
            year = self.years[0]
            nitrate_dir = os.path.join(self.current_dir, '../data/grids_for_prediction', f"grid_{year}.csv")
            self.nitrate_df = pd.read_csv(nitrate_dir, parse_dates=['date'])

        self.builder_map = {
            LanduseAligner: ["landuse code"],
            SoilTypeAligner: ["soil region"],
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
                                'density', 'soilunit_code', 'mainsoilclassification']
        }

        self._merged_dataframes = self._build_and_merge()

    def _build_and_merge(self):
        if self.connect_to == 'nitrate_data':
            nitrate_vars = ['nitrate', 'bro-id', 'geometry', 'date']
        elif self.connect_to == 'grid_data':
            nitrate_vars = ['geometry', 'date']

        base_columns = [v for v in self.variables if v in nitrate_vars and v in self.nitrate_df.columns]

        if base_columns:
            final_df = self.nitrate_df[base_columns].copy()
        else:
            final_df = pd.DataFrame()

        for cls, supported_var in self.builder_map.items():
            selected_vars = [v for v in self.variables 
                                    for base_var in supported_var
                                    if v.startswith(base_var)]
            if not selected_vars:
                continue

            print(f"Initializing {cls.__name__} for {selected_vars}")
            instance = cls(self.provinces, self.well_filter, self.connect_to, self.years)

            for var in selected_vars:
                if not hasattr(instance, "get_variable"):
                    raise AttributeError(f"{cls.__name__} must implement 'get_variable' method.")

                var_df = instance.get_variable(var)
                print(f"Type of df: {type(var_df)}")

                # add the variable as a new column, aligned by index
                if isinstance(var_df, (pd.Series, gpd.GeoSeries)):
                    final_df[var] = var_df
                    print(final_df)
                else:
                    raise ValueError(f"{var} not found in returned DataFrame.")
            print("\n")

        return final_df
    
    @property
    def merged_dataframes(self):
        return self._merged_dataframes


if __name__ == "__main__":
    # variables_of_interest = ['bro-id', 'nitrate', 'geometry', 'date', 'groundwater depth', \
    #                          'population', 'soil region', 'landuse code', 'precipitation', \
    #                          'temperature', 'elevation', 'lon', 'lat', 'n deposition', \
    #                          'soilunit_code_1', 'organicmattercontent_1', 'density_1']
    
    # variables_of_interest = ['bro-id', 'nitrate', 'geometry', 'date', 'groundwater depth', \
    #                          'population', 'soil region', 'landuse code', 'precipitation', \
    #                          'temperature', 'elevation', 'lon', 'lat', 'n deposition']

    variables_of_interest = ['bro-id', 'nitrate', 'geometry', 'date', 'mainsoilclassification_1', 'organicmattercontent_1', 'density_1']

    provinces = ["utrecht"]

    well_filter = 1
    
    merged_dataset = MergedDatasetBuilder(variables_of_interest, provinces, well_filter)
    print(merged_dataset.merged_dataframes)
    # merged_dataset.merged_dataframes.to_csv("merged_temp.csv")
