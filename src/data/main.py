import pandas as pd
from dataset_well import Dataset_Well
from dataset_saver import Dataset_Saver

def main():
    dataset = Dataset_Well(type_of_data = "well_chem_data", type_of_file = ".csv")
    saver = Dataset_Saver()
    saver(dataset, "../../data/raw/well_filtered_combined.csv")


if __name__ == "__main__":
    main()
