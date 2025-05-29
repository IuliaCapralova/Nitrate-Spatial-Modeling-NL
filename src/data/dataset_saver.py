import os
import csv
import pandas as pd
from typing import Union
from dataset import Dataset_Preprocess
from dataset_bro import Dataset_BRO
from spatial_data import SpatialData
from timeseries_preprocess import TimeseriesPreprocess
from env_preprocess import Environmental_Preprocess
from merged_dataset_builder import MergedDatasetBuilder


class Dataset_Saver():
    def __call__(self, dataset: Union[Dataset_BRO, Dataset_Preprocess, pd.DataFrame, MergedDatasetBuilder], path:str):
        
        file_path = os.path.join(os.getcwd(), path)

        if isinstance(dataset, Dataset_BRO) or isinstance(dataset, TimeseriesPreprocess) or isinstance(dataset, Environmental_Preprocess):
            dataset._dataframe.to_csv(file_path, index = False)

        elif isinstance(dataset, MergedDatasetBuilder):
            dataset.merged_dataframes.to_csv(file_path, index = False)

        elif isinstance(dataset, SpatialData):
            for file_name, gdf in dataset._dataframe.items():
                output_path = os.path.join(path, f"{file_name}_processed.gpkg")
                gdf.to_file(output_path, driver="GPKG")

        else:
            raise ValueError("Can only load objects of type pd.DataFrame and DataSet.")


if __name__ == "__main__":
    pass
