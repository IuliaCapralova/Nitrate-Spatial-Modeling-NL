import pandas as pd
from dataset_nitrate import Dataset_Nitrate
from dataset_depth import Dataset_Depth
from dataset_saver import Dataset_Saver

def main():

    # dataset = Dataset_Nitrate(province=province)
    # saver = Dataset_Saver()
    # saver(dataset, f"data/raw/well_chem_data/{province}_well_combined.csv")
    # print(f"Data from {province} is saved successfuly!")

    province = "flevoland"
    n_files = None

    dataset = Dataset_Depth(province=province, max_files=n_files)

    if isinstance(dataset, Dataset_Nitrate):
        variable = "chem"
    if isinstance(dataset, Dataset_Depth):
        variable = "depth"

    saver = Dataset_Saver()
    saver(dataset, f"data/raw/well_depth_data/{province}_well_{variable}_combined.csv")
    print(f"{variable.upper()} data from {province} is saved successfully!")


if __name__ == "__main__":
    main()
