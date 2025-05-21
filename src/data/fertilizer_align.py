import os
import pandas as pd
from align_data import BaseAligner


class FertilizerAnigner(BaseAligner):
    def __init__(self, well_filter=1):
        super().__init__(well_filter)
        fertilizer_path = os.path.join(self.current_dir, 'data/clean', "fertilizer use", "mineral_fertilizer_N.xlsx")
        self.fertilizer_df = pd.read_excel(fertilizer_path)

        self._dataframe = self._align()

    def _align(self):
        self.fertilizer_df = self.fertilizer_df[["Year", "Mineral fertiliser N/ha in kg"]].copy()
        merged_df = pd.merge(self.nitrate_gdf, self.fertilizer_df, on="Year", how="left")
        return merged_df


if __name__ == "__main__":
    instance = FertilizerAnigner()
    print(instance._dataframe)
