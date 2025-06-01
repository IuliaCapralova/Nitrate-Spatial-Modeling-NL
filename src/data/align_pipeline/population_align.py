import os
from .align_spatial import SpatialTimeseriesBaseAligner


class PopulationAlignment(SpatialTimeseriesBaseAligner):
    def __init__(self, well_filter=1):
        super().__init__(well_filter)
        path = os.path.join(self.current_dir, "data", "clean", "population_density")
        self._dataframe = self._align(path=path, column='aantal_inwoners', predicate='intersects')


if __name__ == "__main__":
    instance = PopulationAlignment()
    print(instance._dataframe)
    # print(instance.get_variable(name="population"))
