import os
from align_spatial import SpatialTimeseriesBaseAligner


class LanduseAligner(SpatialTimeseriesBaseAligner):
    def __init__(self, well_filter=1):
        super().__init__(well_filter)
        path = os.path.join(self.current_dir, "data", "clean", "land_use")
        self._dataframe = self._align(path, column='code', predicate ="intersects")


if __name__ == "__main__":
    instance = LanduseAligner()
    print(instance._dataframe)
    # print(instance.get_variable(name="landuse code"))
    # landuse_counts = gdf['Landuse_Code'].value_counts(dropna=True).sort_index()
    # print(landuse_counts)
