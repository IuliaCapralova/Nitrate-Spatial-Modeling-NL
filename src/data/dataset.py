import os
import pandas as pd
from abc import ABC, abstractmethod


class DataSet(ABC):
    """
    Depending on the type of data (e.g. well data) user is interested in, we collect relevant files
    """

    def __init__(self, type_of_data: str) -> None:
        # get current directory
        current_dir = os.getcwd()
        dataset_dir = os.path.join(current_dir, 'data/raw', type_of_data)
        
        # e.g., chemical analysis from wells
        self.type_of_data = type_of_data
        
        # save directory to the general type of the data (like well data)
        self._datasetdir = dataset_dir

    @abstractmethod
    def _paths_finder(self):
        pass
    
    @abstractmethod
    def __getitem__(self):
        """
        Access the file path at a given index.
        """
        pass

    @abstractmethod
    def __len__(self):
        """
        Return the number of collected CSV files.
        """
        pass

    @abstractmethod
    def get_paths(self):
        pass


if __name__ == "__main__":
    pass
    