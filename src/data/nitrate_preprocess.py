import os
import re
import csv
import fiona
import pandas as pd
import geopandas as gpd
from dataset_preprocess import Dataset_Preprocess
from abc import ABC, abstractmethod


class Nitrate_Preprocess(Dataset_Preprocess):
    
    def __init__(self, province, filter) -> None:
        super().__init__(province, filter, type_of_data="well_chem_data")

    def _handle_missing_values(self):
        # Drop rows with any NaNs in Niterate column
        self._dataframe = self._dataframe.dropna(subset=["Nitrate"])

    def _filter_data(self):
        pass


if __name__ == "__main__":
    instance = Nitrate_Preprocess("utrecht")
    print(len(instance._dataframe))
    print(instance._dataframe)
