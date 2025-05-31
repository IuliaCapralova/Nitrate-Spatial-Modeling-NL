import os
from align_spatial import SpatialTimeseriesBaseAligner


class NDepositionAligner(SpatialTimeseriesBaseAligner):
    def __init__(self, well_filter=1):
        super().__init__(well_filter)
        path = os.path.join(self.current_dir, "data", "clean", "n_deposition")
        self._dataframe = self._align(path=path, column='deposition_kg', predicate='intersects')


if __name__ == "__main__":
    instance = NDepositionAligner()
    print(instance._dataframe)
    print(instance.get_variable(name="n deposition"))
