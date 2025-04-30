import os
import csv
import pandas as pd
from typing import Union
from pathlib import Path
from dataset import DataSet


class Dataset_Saver():
    def __call__(self, dataset: Union[DataSet, pd.DataFrame], path:str):
        
        file_path = os.path.join(os.getcwd(), path)

        if isinstance(dataset, DataSet):
            dataset._dataframe.to_csv(file_path, index = False)
        elif isinstance(dataset, pd.DataFrame):
            dataset.to_csv(file_path, index = False)
        else:
            raise ValueError("Can only load objects of type pd.DataFrame and DataSet.")

if __name__ == "__main__":
    pass
