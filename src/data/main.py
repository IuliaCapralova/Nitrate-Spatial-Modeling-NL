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
from merged_dataset_builder import MergedDatasetBuilder
from n_deposition_preprocess import N_Deposition_Prepocess
from soil_comp_preprocess import Soil_Composition_Prepocess


def main():
    province = "utrecht"
    n_files = None
    filter = 1
    year_start = 2000
    year_end = 2022
    years = list(range(2005, 2024))
    # years = [2020]
    start_date = 20120101
    end_date = 20201231
    layer_list = [1]

    # DATA EXTRACTION
    # dataset = Dataset_Depth(province=province, max_files=n_files)
    # dataset = Dataset_Nitrate(province=province, max_files=n_files)

    # DATA PREPROCESSING
    # dataset = Nitrate_Preprocess(filter=filter, province=province)
    # dataset = Depth_Preprocess(province=province, well_filter=filter, year_start=year_start, year_end=year_end)
    # dataset = Population_Prepocess(years)
    # dataset = SoilType_Preprocess()
    # dataset = LandUse_Preprocess(years)
    # dataset = Environmental_Preprocess()
    # dataset = N_Deposition_Prepocess(years)
    # dataset = Soil_Composition_Prepocess(layer_list)
    dataset = None

    if dataset is not None:
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
        if isinstance(dataset, N_Deposition_Prepocess):
            variable = "n_deposition"
        if isinstance(dataset, Soil_Composition_Prepocess):
            variable = "soil_composition"


        ###### CHEM or DEPTH ######

        if variable == "chem" or variable == "depth":
            if type == "clean":
                folder = "for_Alignment"
                add_filter = f"_{filter}"
            else:
                folder = ""
                add_filter = ""

            path = f"data/{type}/well_{variable}_data/{folder}/{province}_well_{variable}_combined{add_filter}.csv"


        ###### OTHER VARIABLES ########

        if variable == "population_density":
            path = f"data/{type}/{variable}"

        elif variable == "type_of_soil":
            path = f"data/{type}/{variable}"

        elif variable == "land_use":
            path = f"data/{type}/{variable}"

        elif variable == "environment":
            path = f"data/{type}/{variable}/environment.csv"

        elif variable == "n_deposition":
            path = f"data/{type}/{variable}"

        elif variable == "soil_composition":
            path = f"data/{type}/{variable}"

        saver = Dataset_Saver()
        saver(dataset, path)
        print(f"{variable.upper()} data is successfully preprocessed and saved!")


    ###### MERGE DATASETS ######
    
    variables_of_interest = ['bro-id', 'nitrate', 'geometry', 'date', 'groundwater depth', \
                             'population', 'soil region', 'landuse code', 'precipitation', \
                             'temperature', 'elevation', 'lon', 'lat', 'n deposition', \
                             'soilunit_code_1', 'organicmattercontent_1', 'density_1']

    merged_dataset = MergedDatasetBuilder(variables_of_interest)
    path = f"data/clean/merged_dataset_1.csv"


    ############## SAVER ###############

    saver = Dataset_Saver()
    saver(merged_dataset, path)
    print("Data is merged and waits in the folder!")


if __name__ == "__main__":
    main()
