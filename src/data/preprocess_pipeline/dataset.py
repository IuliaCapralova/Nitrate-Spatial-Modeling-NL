import os
from abc import ABC, abstractmethod


class Dataset_Preprocess(ABC):
    """
    Depending on the type of data (e.g. well data) user is interested in, we collect relevant files
    """

    def __init__(self, provinces, type_of_data: str) -> None:
        # get current directory
        current_dir = os.getcwd()
        self._datasetdir = os.path.join(current_dir, '../data/raw', type_of_data)
        self._provinces = [p.lower() for p in provinces]

    # @abstractmethod
    def __getitem__(self):
        """
        Access the file path at a given index.
        """
        pass

    # @abstractmethod
    def __len__(self):
        """
        Return the number of collected CSV files.
        """
        pass


if __name__ == "__main__":
    pass
