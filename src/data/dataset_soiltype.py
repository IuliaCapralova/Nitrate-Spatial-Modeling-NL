import os
import pandas as pd
from spatial_data import SpatialData


class Dataset_SoilType(SpatialData):
    def __init__(self):
        super().__init__()

    def crop_file(self):
        for file in self._datapaths:
            pass

if __name__ == "__main__":
    pass