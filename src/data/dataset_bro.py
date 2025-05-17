import os
import csv
from abc import ABC, abstractmethod


class Dataset_BRO():
    COLUMNS = []

    def __init__(self, province, type_of_data, max_files=None):
        super().__init__(type_of_data)

        # ---------
        current_dir = os.getcwd()
        dataset_dir = os.path.join(current_dir, 'data/raw', type_of_data)
        
        # e.g., chemical analysis from wells
        self.type_of_data = type_of_data
        
        # save directory to the general type of the data (like well data)
        self._datasetdir = dataset_dir
        # ---------

        self.province = province
        self.max_files = max_files

        # more specific path with added "province"
        self._datasetdir = os.path.join(self._datasetdir, self.province)

        # depeding on the type of data and the type of files, we need different
        # procedure of extracting paths
        self._datapaths, self._location_files, self.xml_files = self._paths_finder() 

        # limit the number of files if requested
        if self.max_files is not None:
            self._datapaths = self._datapaths[:self.max_files]
            self.xml_files = self.xml_files[:self.max_files]

        self._dataframe = self._extract_data()

    def _paths_finder(self):

        # check if type of data is appropriate
        if self.type_of_data not in ["well_chem_data", "well_depth_data"]:
            print("This dataset does not come from BRO. Please upload another dataset.")
            # TODO raise an error
            return None

        # Walk through the structured folders

        # 1. Iterate through "region_x" folders (x is a number)
        # 2. In each go to "BRO_Grondwatermonitoring" + "BRO_Grondwatermonitoringput"
        # 3. Iterate through each "GMW ..." folder
        # 4. Enter in each and separately store the path for each .csv

        files = []  # store all the file paths
        location_paths = []
        xml_paths = []

        for region_folder in os.listdir(self._datasetdir):
            region_path = os.path.join(self._datasetdir, region_folder)
            # skips the current item if it's not a folder
            if not os.path.isdir(region_path):
                continue

            # in this folder we can find location
            # so before moving on, we save these location files
            kml_path = self._location_paths_finder(region_path)
            if kml_path:
                location_paths.append(kml_path)


            #proceed with folders to find .csv paths
            monitoring_path = os.path.join(region_path, "BRO_Grondwatermonitoring", "BRO_Grondwatermonitoringput")
            if not os.path.isdir(monitoring_path):
                continue

            for well_folder in os.listdir(monitoring_path):
                well_path = os.path.join(monitoring_path, well_folder)
                if not os.path.isdir(well_path) or not well_folder.startswith("GMW"):
                    continue

                for file in os.listdir(well_path):
                    if file.endswith(".csv"):  # e.g., '.csv'
                        full_path = os.path.join(well_path, file)
                        files.append(full_path)
                    if file.endswith(".xml"):
                        full_path = os.path.join(well_path, file)
                        xml_paths.append(full_path)
            
        return sorted(files), sorted(location_paths), sorted(xml_paths)
    
    def _location_paths_finder(self, region_path):
        kml_files = [f for f in os.listdir(region_path) if f.endswith(".kml")]
        if kml_files:
            return os.path.join(region_path, kml_files[0])
        return None
    
    def _read_csv_rows(self, path):
        with open(path, newline='', encoding='utf-8') as f:
            return list(csv.reader(f))

    def __getitem__(self, index:int):
        """
        Access the file path at a given index.
        """
        if index not in range(len(self)):
            raise IndexError("Index out of bounds.")
        return self._datapaths[index]

    def __len__(self) -> int:
        """
        Return the number of collected CSV paths.
        """
        return len(self._datapaths)

    def get_paths(self) -> list:
        return self._datapaths

    @abstractmethod
    def _extract_data(self):
        pass

    @abstractmethod
    def _filter_file(self):
        pass

    @abstractmethod
    def _extract_metadata(self):
        pass

    @abstractmethod
    def _location_df_creator(self):
        pass


if __name__ == "__main__":
    pass
