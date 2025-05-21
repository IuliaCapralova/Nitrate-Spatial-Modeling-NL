from fertilizer_align import FertilizerAnigner
from landuse_align import LanduseAligner
from population_align import PopulationAlignment
from statline_aligner import StatLineAligner
from soil_type_align import SoilTypeAligner
from depth_chem_align import DepthAligner
from elevation_align import ElevationAligner
from environment_chem_align import EnvironmentalAligner
from functools import reduce
import pandas as pd

class MergedDatasetBuilder:
    def __init__(self, variables: list[str], well_filter=2):
        self.variables = variables
        self.well_filter = well_filter
        self.available_builders = {
            "soil type": SoilTypeAligner,
            "land use": LanduseAligner,
            "population": PopulationAlignment,
            "groundwater depth": DepthAligner,
            "fertilizer": FertilizerAnigner,
            "elevation": ElevationAligner,
            "precipitation temperature": EnvironmentalAligner,
            "environment": StatLineAligner
        }
        dataframes = self._build_selected_dataframes()
        self._merged_dataframes = self._merge_all(dataframes)

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
    variables_of_interest = ['groundwater depth', 'population', 'soil type', 'land use', \
                 'precipitation temperature', 'environment', 'elevation', 'fertilizer']
    
    merged_dataset = MergedDatasetBuilder(variables_of_interest)
    merged_dataset
    print(merged_dataset.merged_dataframes)
