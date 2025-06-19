import os
import pandas as pd
from typing import Union
from bro_data_extraction_pipeline.dataset_bro import Dataset_BRO
from preprocess_pipeline.spatial_data import SpatialData
from preprocess_pipeline.dataset import Dataset_Preprocess
from preprocess_pipeline.timeseries_preprocess import TimeseriesPreprocess
# from preprocess_pipeline.env_preprocess import Environmental_Preprocess
# from align_pipeline.merged_dataset_builder import MergedDatasetBuilder
from align_pipeline import merged_dataset_builder
from align_pipeline import env_preprocess


class Dataset_Saver():
    def __call__(self, dataset: Union[Dataset_BRO, Dataset_Preprocess, pd.DataFrame, merged_dataset_builder.MergedDatasetBuilder], path:str):
        
        file_path = os.path.join(os.getcwd(), path)

        if isinstance(dataset, TimeseriesPreprocess) or isinstance(dataset, env_preprocess.Environmental_Preprocess):
            for file_name, data in dataset.dataframe.items():
                output_path = os.path.join(path, f"{file_name}.csv")
                data.to_csv(output_path, index = False)

        elif isinstance(dataset, Dataset_BRO):
            dataset._dataframe.to_csv(file_path, index = False)

        elif isinstance(dataset, merged_dataset_builder.MergedDatasetBuilder):
            dataset.merged_dataframes.to_csv(file_path, index = False)

        elif isinstance(dataset, SpatialData):
            for file_name, gdf in dataset._dataframe.items():
                output_path = os.path.join(path, f"{file_name}_processed.gpkg")
                gdf.to_file(output_path, driver="GPKG")

        else:
            raise ValueError("Can only load objects of type pd.DataFrame and DataSet.")


if __name__ == "__main__":
    pass
