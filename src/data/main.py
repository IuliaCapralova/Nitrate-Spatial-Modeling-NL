import pandas as pd
from dataset_well import Dataset_Well

def main():
    well_chem_data = Dataset_Well(type_of_data = "well_chem_data", type_of_file = ".csv")
    # define path where you want to save new csv
    # save it


if __name__ == "__main__":
    main()
