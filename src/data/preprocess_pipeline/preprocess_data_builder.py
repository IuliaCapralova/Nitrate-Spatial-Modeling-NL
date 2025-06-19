import os
from typing import Any, Dict, List
from .nitrate_preprocess import Nitrate_Preprocess
from .depth_preprocess import Depth_Preprocess
from .population_preprocess import Population_Prepocess
from .soil_type_preprocess import SoilType_Preprocess
from .landuse_preprocess import LandUse_Preprocess
from .env_preprocess import Environmental_Preprocess
from .n_deposition_preprocess import N_Deposition_Prepocess
from .soil_comp_preprocess import Soil_Composition_Prepocess
from ..dataset_saver import Dataset_Saver


class PreprocessingPipelineBuilder:
    def __init__(
        self,
        pipeline_vars: List[str],
        province: List[str],
        well_filter: int,
        year_start: int,
        year_end: int,
        years: List[int],
        station_id: int,
        start_date: str,
        end_date: str,
        layer_list: List[int],
    ):
        self.pipeline_vars = [v.lower() for v in pipeline_vars]
        self.province = province
        self.well_filter = well_filter
        self.year_start = year_start
        self.year_end = year_end
        self.years = years
        self.station_id = station_id
        self.start_date = start_date
        self.end_date = end_date
        self.layer_list = layer_list


if __name__ == "__init__":
    pass