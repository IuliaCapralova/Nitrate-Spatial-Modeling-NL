import os
import re
import csv
import fiona
import pandas as pd
import geopandas as gpd
from dataset_preprocess import Dataset_Preprocess
from abc import ABC, abstractmethod


class Depth_Preprocess(Dataset_Preprocess):
    
    def __init__(self, province, filter) -> None:
        super().__init__(province, filter, type_of_data="well_depth_data")

    def _handle_missing_values(self):
        self._dataframe = self._dataframe.drop_duplicates(subset=["Well_ID", "BRO-ID", "Filter", "Date", "geometry", \
                                                                  "Ground Level","Bottom Screen","Top Screen","Year"], keep="first")

    def _filter_data(self):
        pass


if __name__ == "__main__":
    instance = Depth_Preprocess("utrecht")
    print(len(instance._file))
