import os
import pandas as pd
from align_data import BaseAligner


class StatLineAligner(BaseAligner):
    def __init__(self, well_filter=1, variables=['livestock', 'excretion_during_grazing', 'municipal_waste', 'nitrogen_losses_in_housing', 'use_of_livestock_manure_in_agriculture']):
        # TODO: check and standardize variables names user gave
        super().__init__(well_filter)
        self.variables = variables

        self._align()

    def _align(self):
        for var in self.variables:
            path = os.path.join(self.current_dir, 'data/clean', "statline_data", f"{var}.csv")
            with open(path, 'r') as f:
                sample = f.readline()
                delimiter = ';' if ';' in sample else ','
                
            df = pd.read_csv(path, delimiter=delimiter)
            df = df.rename(columns={"Periods": "Year"})

            self.nitrate_gdf = pd.merge(self.nitrate_gdf, df, on="Year", how="left")
            print(self.nitrate_gdf)
            print(f"{var} was added!")

        self._dataframe = self.nitrate_gdf


if __name__ == "__main__":
    instance = StatLineAligner()
    instance
