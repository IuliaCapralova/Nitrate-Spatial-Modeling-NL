import os
import re
import geopandas as gpd
import numpy as np
import rioxarray
from rasterio.features import shapes
from shapely.geometry import shape
from shapely.geometry import mapping
from concurrent.futures import as_completed
from concurrent.futures import ProcessPoolExecutor

try:
    from .spatial_data import SpatialData
except ImportError:
    from spatial_data import SpatialData


class LandUse_Preprocess(SpatialData):
    AVAILABLE_YEARS = {2003, 2004, 2007, 2008, 2012, 2018, 2019, 2020, 2021, 2022, 2023}

    def __init__(self, years: list[int], provinces: list[str]):
        # year alias pairs (these refer to the same file)
        duplicate_pairs = [(2003, 2004), (2007, 2008)]

        if len(provinces) == 12:
            self._entire_nl_flag = True
        else:
            self._entire_nl_flag = False

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

    # def _preprocess(self, file_path: str):
    #     # for each file apply all preprocessing steps
    #     lgn_raw = rioxarray.open_rasterio(file_path, masked=False)
    #     cropped_lgn = self._crop_file(lgn_raw)
    #     final_gdf = self._to_geo_table(cropped_lgn)
    #     return final_gdf

    # def _crop_file(self, file):
    #     # crops pixel grid based on vector boundary
    #     mask_proj = self._utrecht_mask.to_crs(file.rio.crs)  # match CRS to raster
    #     aoi_geom = [mapping(mask_proj.iloc[0].geometry)]
    #     lgn_cropped = file.rio.clip(aoi_geom, mask_proj.crs, drop=True)
    #     return lgn_cropped
    
    # def _to_geo_table(self, lgn):
    #     band_float = lgn[0].values
    #     mask = ~np.isnan(band_float) # create mask before converting to int
    #     band = band_float.astype("int32")
    #     # extract polygons
    #     results = (
    #         {"geometry": shape(geom), "code": int(value)}
    #         for geom, value in shapes(band, mask=mask, transform=lgn.rio.transform())
    #     )
    #     gdf = gpd.GeoDataFrame.from_records(results)
    #     gdf = gdf.set_geometry("geometry")
    #     gdf.set_crs(lgn.rio.crs, inplace=True)
    #     return gdf

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
        
    # def _populate_dataframe(self):
    #     for file_path in self._datapaths:
    #         final_gdf = self._preprocess(file_path)
    #         file_name = os.path.splitext(os.path.basename(file_path))[0]  # no extension
    #         self._dataframe[file_name] = final_gdf
    #         print(f"Preprocessed file: {file_path}")

    # def _populate_dataframe(self):
    #     from shapely.geometry import mapping
    #     import os

    #     utrecht_mask_geom = self._utrecht_mask.iloc[0].geometry
    #     utrecht_mask_wkt = utrecht_mask_geom.wkt

    #     args_list = [(path, utrecht_mask_wkt) for path in self._datapaths]
    #     self._dataframe = {}

    #     if self._entire_nl_flag:
    #         ...
    #     else:
    #         with ProcessPoolExecutor(max_workers=6) as executor:
    #             futures = [executor.submit(preprocess_landuse_file, path, utrecht_mask_wkt) for path in self._datapaths]

    #             for future in as_completed(futures):
    #                 file_name, gdf = future.result()
    #                 self._dataframe[os.path.splitext(file_name)[0]] = gdf
    #                 print(f"Preprocessed file: {file_name}")


    def _populate_dataframe(self):

        self._dataframe = {}

        for file_path in self._datapaths:
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            print(f"Processing {file_name}...")

            # Open raster
            lgn_raw = rioxarray.open_rasterio(file_path, masked=False)

            # Optional crop
            if not self._entire_nl_flag:
                utrecht_mask = self._utrecht_mask
                mask_proj = utrecht_mask.to_crs(lgn_raw.rio.crs)
                lgn_raw = lgn_raw.rio.clip(
                    [mapping(mask_proj.iloc[0].geometry)],
                    mask_proj.crs,
                    drop=True
                )

            # Polygonize
            band_float = lgn_raw[0].values
            mask = ~np.isnan(band_float)
            band = band_float.astype("int32")

            results = (
                {"geometry": shape(geom), "code": int(value)}
                for geom, value in shapes(band, mask=mask, transform=lgn_raw.rio.transform())
            )

            gdf = gpd.GeoDataFrame.from_records(results)
            gdf.set_geometry("geometry", inplace=True)
            gdf.set_crs(lgn_raw.rio.crs, inplace=True)

            # Save to dataframe
            self._dataframe[file_name] = gdf
            print(f"→ Added {file_name} to dataframe.")


# def preprocess_landuse_file(file_path, utrecht_mask_wkt):

#     # Reload vector mask from WKT
#     utrecht_mask = gpd.GeoDataFrame(geometry=[wkt.loads(utrecht_mask_wkt)], crs="EPSG:4326")

#     # Open raster
#     lgn_raw = rioxarray.open_rasterio(file_path, masked=False)

#     # Crop raster
#     mask_proj = utrecht_mask.to_crs(lgn_raw.rio.crs)
#     aoi_geom = [mapping(mask_proj.iloc[0].geometry)]
#     lgn_cropped = lgn_raw.rio.clip(aoi_geom, mask_proj.crs, drop=True)

#     # Polygonize
#     band_float = lgn_cropped[0].values
#     mask = ~np.isnan(band_float)
#     band = band_float.astype("int32")
#     results = (
#         {"geometry": shape(geom), "code": int(value)}
#         for geom, value in shapes(band, mask=mask, transform=lgn_cropped.rio.transform())
#     )
#     gdf = gpd.GeoDataFrame.from_records(results)
#     gdf = gdf.set_geometry("geometry")
#     gdf.set_crs(lgn_cropped.rio.crs, inplace=True)

#     return os.path.basename(file_path), gdf


if __name__ == "__main__":
    years = [2008]
    # provinces = ["utrecht"]
    provinces = ['drenthe', 'flevoland', 'fryslân', 'gelderland', 'groningen', 'limburg', 'noord-brabant', 'noord-holland', 'overijssel', 'utrecht', 'zeeland', 'zuid-holland']
    instance = LandUse_Preprocess(years, provinces)
    print(instance.dataframe)
