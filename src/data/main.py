import pandas as pd
from dataset_well import Dataset_Well
from dataset_saver import Dataset_Saver

def main():
    
    # Ask user to name the province
    province = input("Please select one of the provinces: Zeeland, Flevoland, Noord-Holland, Utrecht: ").strip()

    # Zeeland data
    dataset = Dataset_Well(province = province, type_of_data = "well_chem_data")
    saver = Dataset_Saver()
    saver(dataset, f"data/raw/well_chem_data/{province}_well_combined.csv")
    print(f"Data from {province} is saved successfuly!")


if __name__ == "__main__":
    main()
