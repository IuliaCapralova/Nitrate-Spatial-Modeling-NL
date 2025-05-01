import pandas as pd
from dataset_nitrate import Dataset_Nitrate
from dataset_depth import Dataset_Depth
from dataset_saver import Dataset_Saver
from nitrate_preprocess import Nitrate_Preprocess
from depth_preprocess import Depth_Preprocess

def main():

    province = "utrecht"
    n_files = None

    # dataset = Dataset_Depth(province=province, max_files=n_files)
    # dataset = Dataset_Nitrate(province=province, max_files=n_files)

    dataset = Nitrate_Preprocess(province=province)

    if isinstance(dataset, Dataset_Nitrate) or isinstance(dataset, Nitrate_Preprocess):
        variable = "chem"
    if isinstance(dataset, Dataset_Depth) or isinstance(dataset, Depth_Preprocess):
        variable = "depth"

    if isinstance(dataset, Nitrate_Preprocess) or isinstance(dataset, Depth_Preprocess):
        type = "clean"
    else:
        type = "raw"

    saver = Dataset_Saver()
    saver(dataset, f"data/{type}/well_{variable}_data/{province}_well_{variable}_combined.csv")
    print(f"{variable.upper()} data from {province} is saved successfully!")


if __name__ == "__main__":
    main()
