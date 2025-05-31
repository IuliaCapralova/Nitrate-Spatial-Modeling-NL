import os
import re
import csv
import fiona
import copy
import pandas as pd
import geopandas as gpd
from timeseries_preprocess import TimeseriesPreprocess
from abc import ABC, abstractmethod


class Nitrate_Preprocess(TimeseriesPreprocess):
    
    def __init__(self, filter, province="utrecht", year_start=2012, year_end=2020) -> None:
        super().__init__(province, filter, year_start, year_end,type_of_data="well_chem_data")

    def _filter_columns(self):
        columns = ["Well_ID", "BRO-ID", "Filter", "Date", "Nitrate", "geometry"]
        self._dataframe = self._dataframe[columns].copy()

    def _handle_missing_values(self):
        # Drop rows with any NaNs in Niterate column
        self._dataframe = self._dataframe.dropna(subset=["Nitrate"])

    def _rename_cols(self):
        self._dataframe.rename(columns={"BRO-ID":"bro-id", "Date": "date", "Nitrate": "nitrate"}, inplace=True)


if __name__ == "__main__":
    instance = Nitrate_Preprocess(1, "utrecht")
    # print(len(instance._dataframe))
    print(instance._dataframe)

    # cols = ['nitrate', 'geometry', 'date']
    # print(instance.get_variable(cols))
