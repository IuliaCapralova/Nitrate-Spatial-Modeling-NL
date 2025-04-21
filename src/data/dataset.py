import os
import pandas as pd
from abc import ABC, abstractmethod

class DataSet(ABC):

    """
    Depending on the type of data (e.g. well data) user is interested in, we collect relevant files
    """

    def __init__(self, type_of_data: str, type_of_file:str) -> None:

        # get current directory
        # TODO: !! you should go a few folders back to reach "data" folder !!
        current_dir = os.getcwd()

        # go a few folders up
        two_levels_up = os.path.abspath(os.path.join(current_dir, "..", ".."))

        dataset_dir = os.path.join(two_levels_up, 'data/raw', type_of_data)
        
        # e.g., chemical analysis from wells
        self.type_of_data = type_of_data

        # e.g., .csv, .kml, .gpkg
        self.type_of_file = type_of_file
        
        # save directory to the general type of the data (like well data)
        self._datasetdir = dataset_dir

        # depeding on the type of data and the type of files, we need different
        # procedure of extracting paths
        self._datafiles = self._paths_finder() # containts all file paths


    def _paths_finder(self):

        if self.type_of_data == "well_chem_data":
            # Walk through the structured folders

            # 1. Iterate through "region_x" folders (x is a number)
            # 2. In each go to "BRO_Grondwatermonitoring" + "BRO_Grondwatermonitoringput"
            # 3. Iterate through each "GMW ..." folder
            # 4. Enter in each and separately store the path for each .csv

            files = []  # store all the file paths

            for region_folder in os.listdir(self._datasetdir):
                region_path = os.path.join(self._datasetdir, region_folder)
                # skips the current item if it's not a folder
                if not os.path.isdir(region_path):
                    continue

                monitoring_path = os.path.join(region_path, "BRO_Grondwatermonitoring", "BRO_Grondwatermonitoringput")
                if not os.path.isdir(monitoring_path):
                    continue

                for well_folder in os.listdir(monitoring_path):
                    well_path = os.path.join(monitoring_path, well_folder)
                    if not os.path.isdir(well_path) or not well_folder.startswith("GMW"):
                        continue

                    for file in os.listdir(well_path):
                        if file.endswith(self.type_of_file):  # e.g., '.csv'
                            full_path = os.path.join(well_path, file)
                            files.append(full_path)

        return sorted(files)
    
    def __getitem__(self, index:int):
        """
        Access the file path at a given index.
        """
        if index not in range(len(self)):
            raise IndexError("Index out of bounds.")
        return self._datafiles[index]

    def __len__(self) -> int:
        """
        Return the number of collected CSV files.
        """
        return len(self._datafiles)

    def get_df(self) -> list:
        return self._datafiles


if __name__ == "__main__":
    instance = DataSet(type_of_data = "well_chem_data", type_of_file = ".csv")
    path = instance[0]
    read_csv = pd.read_csv(path)
    print(read_csv.head())
    