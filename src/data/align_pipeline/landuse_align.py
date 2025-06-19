import os

try:
    from .align_spatial import SpatialTimeseriesBaseAligner
except ImportError:
    from align_spatial import SpatialTimeseriesBaseAligner


class LanduseAligner(SpatialTimeseriesBaseAligner):
    def __init__(self, provinces, well_filter, connect_to, years):
        super().__init__(provinces, well_filter,  connect_to, years)
        path = os.path.join(self.current_dir, "../data", "clean", "land_use")
        self._dataframe = self._align(path, column='code', predicate ="intersects")


if __name__ == "__main__":
    provinces = ["utrecht"]
    well_filter = 1
    connect_to = "nitrate_data"
    years = [2010]

    instance = LanduseAligner(provinces, well_filter, connect_to, years)
    print(instance.dataframe)
    # print(instance.get_variable(name="landuse code"))
    # landuse_counts = gdf['Landuse_Code'].value_counts(dropna=True).sort_index()
    # print(landuse_counts)
