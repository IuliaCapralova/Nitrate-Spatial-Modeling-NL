import os

try:
    from .align_spatial import SpatialTimeseriesBaseAligner
except ImportError:
    from align_spatial import SpatialTimeseriesBaseAligner


class NDepositionAligner(SpatialTimeseriesBaseAligner):
    def __init__(self, provinces, well_filter, connect_to, years):
        super().__init__(provinces, well_filter, connect_to, years)
        path = os.path.join(self.current_dir, "../data", "clean", "n_deposition")
        self._dataframe = self._align(path=path, column='deposition_kg', predicate='intersects')


if __name__ == "__main__":
    provinces = ["utrecht"]
    well_filter = 1
    connect_to = "nitrate_data"
    years = [2010]

    instance = NDepositionAligner(provinces, well_filter, connect_to, years)
    print(instance.dataframe)
    # print(instance.get_variable(name="n deposition"))
