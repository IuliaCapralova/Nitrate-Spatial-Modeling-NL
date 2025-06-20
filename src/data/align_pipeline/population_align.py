import os

try:
    from .align_spatial import SpatialTimeseriesBaseAligner
except ImportError:
    from align_spatial import SpatialTimeseriesBaseAligner


class PopulationAlignment(SpatialTimeseriesBaseAligner):
    def __init__(self, provinces, well_filter, connect_to, years):
        super().__init__(provinces, well_filter)
        path = os.path.join(self.current_dir, "../data", "clean", "population_density")
        self._dataframe = self._align(path=path, column='aantal_inwoners', predicate='intersects')


if __name__ == "__main__":
    provinces = ["utrecht"]
    well_filter = 1
    connect_to = "nitrate_data"
    years = [2010]

    instance = PopulationAlignment(provinces, well_filter, connect_to, years)
    print(instance.dataframe)
    instance.dataframe.to_csv("population_align.csv", index=False)
    # print(instance.get_variable(name="population"))
