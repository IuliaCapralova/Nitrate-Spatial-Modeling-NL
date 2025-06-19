import os
import re
import geopandas as gpd
import numpy as np
import rioxarray
from rasterio.features import shapes
from shapely.geometry import shape
from shapely.geometry import mapping
from .spatial_data import SpatialData

## !!! TODO: safe as tif file


class LandUse_Preprocess(SpatialData):
    AVAILABLE_YEARS = {2003, 2004, 2007, 2008, 2012, 2018, 2019, 2020, 2021, 2022, 2023}

    def __init__(self, years: list[int], provinces: list[str]):
        # year alias pairs (these refer to the same file)
        duplicate_pairs = [(2003, 2004), (2007, 2008)]

        cleaned_years = set(years) # copy to avoid mutating user input

        # drop duplicates from user-provided year list
        for y1, y2 in duplicate_pairs:
            if y1 in cleaned_years and y2 in cleaned_years:
                cleaned_years.remove(y2)  # Keep only one of them

        invalid_years = [year for year in cleaned_years if year not in self.AVAILABLE_YEARS]
        if invalid_years:
            raise ValueError(
                f"The following year(s) are unavailable: {invalid_years}. "
                f"Available years are: {sorted(self.AVAILABLE_YEARS)}")

        super().__init__(provinces, type_of_data="land_use")
        self.year_list = cleaned_years
        self._dataframe = {}
        self._datasetdir = os.path.join(self._datasetdir)
        self._datapaths = self._paths_finder()
        self._populate_dataframe()

    # --------- preprocess part -----------

    def _preprocess(self, file_path: str):
        # for each file apply all preprocessing steps
        lgn_raw = rioxarray.open_rasterio(file_path, masked=False)
        cropped_lgn = self._crop_file(lgn_raw)
        final_gdf = self._to_geo_table(cropped_lgn)
        return final_gdf

    def _crop_file(self, file):
        # crops pixel grid based on vector boundary
        mask_proj = self._utrecht_mask.to_crs(file.rio.crs)  # match CRS to raster
        aoi_geom = [mapping(mask_proj.iloc[0].geometry)]
        lgn_cropped = file.rio.clip(aoi_geom, mask_proj.crs, drop=True)
        return lgn_cropped
    
    def _to_geo_table(self, lgn):
        band_float = lgn[0].values
        mask = ~np.isnan(band_float) # create mask before converting to int
        band = band_float.astype("int32")
        # extract polygons
        results = (
            {"geometry": shape(geom), "code": int(value)}
            for geom, value in shapes(band, mask=mask, transform=lgn.rio.transform())
        )
        gdf = gpd.GeoDataFrame.from_records(results)
        gdf = gdf.set_geometry("geometry")
        gdf.set_crs(lgn.rio.crs, inplace=True)
        return gdf

    # ---------------------------

    def _paths_finder(self):
        pop_files_paths = []
        for folder in os.listdir(self._datasetdir):
            if not (folder.startswith("LGN") and not folder.startswith(".")):
                continue

            folder_path = os.path.join(self._datasetdir, folder)

            match = re.findall(r'\d{4}', folder)
            years = [int(y) for y in match]

            for file_name in os.listdir(folder_path):
                if not file_name.endswith(".tif"):
                    continue
                # only process folder if any of the years match
                if not any(y in self.year_list for y in years):
                    continue
                full_path = os.path.join(folder_path, file_name)
                pop_files_paths.append(full_path)

        return pop_files_paths
        
    def _populate_dataframe(self):
        for file_path in self._datapaths:
            final_gdf = self._preprocess(file_path)
            file_name = os.path.splitext(os.path.basename(file_path))[0]  # no extension
            self._dataframe[file_name] = final_gdf
            print(f"Preprocessed file: {file_path}")


if __name__ == "__main__":
    years = [2012]
    instance = LandUse_Preprocess(years)
    print(instance._dataframe)
