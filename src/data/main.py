import pandas as pd
from dataset_nitrate import Dataset_Nitrate
from dataset_depth import Dataset_Depth
from dataset_saver import Dataset_Saver
from nitrate_preprocess import Nitrate_Preprocess
from depth_preprocess import Depth_Preprocess
from population_preprocess import Population_Prepocess
from soil_type_preprocess import SoilType_Preprocess
from dataset import Dataset_Preprocess
from landuse_preprocess import LandUse_Preprocess
from env_preprocess import Environmental_Preprocess

def main():

    province = "utrecht"
    n_files = None
    filter = 3
    year_start = 2012
    year_end = 2020
    # years = list(range(2000, 2024))
    years = [2012, 2018, 2019, 2020]
    start_date = 20120101
    end_date = 20201231

    # DATA EXTRACTION
    # dataset = Dataset_Depth(province=province, max_files=n_files)
    # dataset = Dataset_Nitrate(province=province, max_files=n_files)

    # DATA PREPROCESSING
    # dataset = Nitrate_Preprocess(province=province, filter=filter)
    # dataset = Depth_Preprocess(province=province, well_filter=filter, year_start=year_start, year_end=year_end)
    # dataset = Population_Prepocess(years)
    # dataset = SoilType_Preprocess()
    # dataset = LandUse_Preprocess(years)
    dataset = Environmental_Preprocess()

    if isinstance(dataset, Dataset_Preprocess) or isinstance(dataset, Environmental_Preprocess):
        type = "clean"
    else:
        type = "raw"


    if isinstance(dataset, Dataset_Nitrate) or isinstance(dataset, Nitrate_Preprocess):
        variable = "chem"
    if isinstance(dataset, Dataset_Depth) or isinstance(dataset, Depth_Preprocess):
        variable = "depth"
    if isinstance(dataset, Population_Prepocess):
        variable = "population_density"
    if isinstance(dataset, SoilType_Preprocess):
        variable = "type_of_soil"
    if isinstance(dataset, LandUse_Preprocess):
        variable = "land_use"
    if isinstance(dataset, Environmental_Preprocess):
        variable = "environment"


    ###### CHEM or DEPTH ######

    if variable == "chem" or variable == "depth":
        if type == "clean":
            folder = "for_Alignment"
            add_filter = f"_{filter}"
        else:
            folder = ""
            add_filter = ""

        path = f"data/{type}/well_{variable}_data/{folder}/{province}_well_{variable}_combined{add_filter}.csv"


    ###### POPULATION ########

    if variable == "population_density":
        path = f"data/{type}/{variable}"

    if variable == "type_of_soil":
        path = f"data/{type}/{variable}"

    if variable == "land_use":
        path = f"data/{type}/{variable}"

    if variable == "environment":
        path = f"data/{type}/{variable}/environment.csv"


    saver = Dataset_Saver()
    saver(dataset, path)
    print(f"{variable.upper()} data from {province} is saved successfully!")


if __name__ == "__main__":
    main()
