import os
from bro_data_extraction_pipeline.dataset_nitrate import Dataset_Nitrate
from bro_data_extraction_pipeline.dataset_depth import Dataset_Depth
from preprocess_pipeline.nitrate_preprocess import Nitrate_Preprocess
from preprocess_pipeline.depth_preprocess import Depth_Preprocess
from preprocess_pipeline.population_preprocess import Population_Prepocess
from preprocess_pipeline.soil_type_preprocess import SoilType_Preprocess
from preprocess_pipeline.dataset import Dataset_Preprocess
from preprocess_pipeline.landuse_preprocess import LandUse_Preprocess
from preprocess_pipeline.n_deposition_preprocess import N_Deposition_Prepocess
from preprocess_pipeline.soil_comp_preprocess import Soil_Composition_Prepocess
from dataset_saver import Dataset_Saver
from align_pipeline.merged_dataset_builder import MergedDatasetBuilder
from generate_empty_grid import generate_empty_grid


def main():
    province = "overijssel"
    # provinces = ['drenthe', 'flevoland', 'fryslân', 'gelderland', 'groningen', 'limburg', 'noord-brabant', 'noord-holland', 'overijssel', 'utrecht', 'zeeland', 'zuid-holland']
    provinces = ["zuid-holland"]
    n_files = None
    filter = 1
    year_start = 2008
    year_end = 2023
    years = [2008]
    # years = list(range(2008, 2024))
    # years = [2008, 2012, 2018, 2019, 2020, 2021, 2022, 2023]
    # years = [2022, 2023]
    start_date = "20080101"
    end_date = "20231231"
    layer_list = [1]

    # DATA EXTRACTION
    # dataset = Dataset_Depth(province=province, max_files=n_files)
    # dataset = Dataset_Nitrate(province=province, max_files=n_files)

    # DATA PREPROCESSING
    # dataset = Nitrate_Preprocess(provinces=provinces, well_filter=filter, year_start=year_start, year_end=year_end)
    # dataset = Depth_Preprocess(province=provinces, well_filter=filter, year_start=year_start, year_end=year_end)
    # dataset = Population_Prepocess(years, provinces)
    # dataset = SoilType_Preprocess(provinces)
    # dataset = LandUse_Preprocess(years, provinces)
    # dataset = Environmental_Preprocess(provinces, start_date=start_date, end_date=end_date, variables=['TEMP', 'PRCP']) ## NOTE this does not take place anymore
    # dataset = N_Deposition_Prepocess(years, provinces)
    # dataset = Soil_Composition_Prepocess(layer_list, provinces)
    dataset = None

    if dataset is not None:
        if isinstance(dataset, Dataset_Preprocess):
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
        if isinstance(dataset, N_Deposition_Prepocess):
            variable = "n_deposition"
        if isinstance(dataset, Soil_Composition_Prepocess):
            variable = "soil_composition"


        ###### CHEM or DEPTH ######

        if variable == "chem" or variable == "depth":
            if type == "clean":
                folder = "for_Alignment"             # "for_Alignment"
                add_filter = f"_{filter}"

                path = f"../data/{type}/well_{variable}_data/{folder}"

            else:
                path = f"../data/{type}/well_{variable}_data/{province}_well_{variable}"


        ###### OTHER VARIABLES ########

        if variable == "population_density":
            path = f"../data/{type}/{variable}"

        elif variable == "type_of_soil":
            path = f"../data/{type}/{variable}"

        elif variable == "land_use":
            path = f"../data/{type}/{variable}"

        elif variable == "environment":
            path = f"../data/{type}/{variable}"

        elif variable == "n_deposition":
            path = f"../data/{type}/{variable}"

        elif variable == "soil_composition":
            path = f"../data/{type}/{variable}"

        saver = Dataset_Saver()
        saver(dataset, path)
        print(f"{variable.upper()} data is successfully preprocessed and saved!")


    # NOTE: Preprocessing of Environmental data now is happeining inside Environmental ALIGNMENT!


    ###### MERGE DATASETS ######

    # Variables to choose from:
                                # 'maparea_id', 'soilslope', 'normalsoilprofile_id', 'layernumber',
                                # 'faohorizonnotation', 'lowervalue', 'uppervalue',
                                # 'organicmattercontent', 'minimumorganicmattercontent',
                                # 'maximumorganicmattercontent', 'acidity', 'minimumacidity',
                                # 'maximumacidity', 'cnratio', 'peattype', 'calciccontent', 'fedith',
                                # 'loamcontent', 'minimumloamcontent', 'maximumloamcontent',
                                # 'lutitecontent', 'minimumlutitecontent', 'maximumlutitecontent',
                                # 'sandmedian', 'minimumsandmedian', 'maximumsandmedian', 'siltcontent',
                                # 'density', 'soilunit_code'

    # FOR NITRATE DATA
    variables_of_interest = ['bro-id', 'nitrate', 'geometry', 'date', 'groundwater_depth', \
                             'population', 'soil region', 'precipitation', \
                             'temperature', 'n deposition', 'landuse code',\
                             'mainsoilclassification_1', 'organicmattercontent_1', \
                             'density_1', 'acidity_1', 'minimumacidity_1', 'maximumacidity_1', 'cnratio_1',\
                             'peattype_1', 'calciccontent_1', 'fedith_1', 'loamcontent_1', 'minimumloamcontent_1',\
                             'maximumloamcontent_1', 'sandmedian_1', 'minimumsandmedian_1', 'maximumsandmedian_1',\
                             'siltcontent_1', "elevation", "lon", "lat"]

    # variables_of_interest = ['bro-id', 'nitrate', 'geometry', 'date', 'elevation']

    # # FOR GRID DATA
    # variables_of_interest = ['geometry', 'date', 'groundwater_depth', \
    #                          'population', 'soil region', 'precipitation', \
    #                          'temperature', 'n deposition', 'landuse code',\
    #                          'mainsoilclassification_1', 'organicmattercontent_1', \
    #                          'density_1', 'acidity_1', 'minimumacidity_1', 'maximumacidity_1', 'cnratio_1',\
    #                          'peattype_1', 'calciccontent_1', 'fedith_1', 'loamcontent_1', 'minimumloamcontent_1',\
    #                          'maximumloamcontent_1', 'sandmedian_1', 'minimumsandmedian_1', 'maximumsandmedian_1',\
    #                          'siltcontent_1', "elevation", "lon", "lat"]
    
    # variables_of_interest = ['geometry', 'date', 'groundwater_depth']

    # variables_of_interest = ['bro-id', 'nitrate', 'geometry', 'date', 'minimumacidity_1', 'maximumacidity_1', 'cnratio_1',\
    #                          'peattype_1', 'calciccontent_1', 'fedith_1', 'loamcontent_1', 'minimumloamcontent_1',\
    #                          'maximumloamcontent_1', 'sandmedian_1', 'minimumsandmedian_1', 'maximumsandmedian_1',\
    #                          'siltcontent_1']

    # provinces = ['utrecht', 'drenthe', 'flevoland', 'fryslân', 'gelderland', 'groningen', 'limburg', 'noord-brabant', 'noord-holland', 'overijssel', 'zeeland', 'zuid-holland']
    provinces = ['zeeland']

    connect_to = "nitrate_data"
    years = [2023]
    month = "07"
    day = "01"
    saver = Dataset_Saver()

    if connect_to == "grid_data":
        for province in provinces:
            path = f"../data/grids_for_prediction/grid_{years[0]}_{province}.csv"
            if not os.path.exists(path):
                print(f"Grid for year {years[0]}, province {province} does not exist. Generating now...")
                grid = generate_empty_grid([province], years[0], month, day)
                saver(grid, path)
            else:
                print(f"Grid for year {years[0]}, province {province} already exists at {path}. Skipping generation.")

    # For merged_dataset path, use '_'.join(provinces) if you want the filename to be readable.
    province_str = '_'.join(provinces)

    merged_dataset = MergedDatasetBuilder(variables_of_interest, provinces, filter, connect_to, years)
    if connect_to == "grid_data":
        path = f"../data/aligned/grid_{filter}_{years[0]}_{province_str}.csv"
    elif connect_to == "nitrate_data":
        path = f"../data/aligned/merged_dataset_{filter}_groundwater_zeeland.csv"


    ############## SAVER ###############

    saver(merged_dataset, path)
    print("Data is merged and waits in the folder!")


if __name__ == "__main__":
    main()
