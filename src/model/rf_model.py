import os
import contextily as ctx
import geopandas as gpd
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import make_scorer, mean_squared_error
from model_abc import ModelBase


class RFmodel(ModelBase):
    def __init__(self, preprocessor, grid_search=False, X_train=None, y_train=None, n_estimators=200, max_depth=15, min_samples_split=2, min_samples_leaf=1, max_features=0.5):
        super().__init__()
        self._create_model(preprocessor, grid_search, X_train, y_train, n_estimators, max_depth, min_samples_split, min_samples_leaf, max_features)

        final_estimator = self._model.steps[-1][1]
        self.model_name = type(final_estimator).__name__

    def _create_model(self, preprocessor, grid_search, X_train, y_train, n_estimators, max_depth, min_samples_split, min_samples_leaf, max_features):
        # Find hyperparameters using grid search
        if grid_search:
            rf_model = RandomForestRegressor(random_state=4, oob_score=False)
    
            pipe = Pipeline([
                ("prep", preprocessor),
                ("rf", rf_model)
                ])

            best_model = self.grid_search(pipe, X_train, y_train, cv=5)
            self._model = best_model
        
        # User defined hyperparameters
        else:
            rf_model = RandomForestRegressor(n_estimators=n_estimators,
                                            max_depth=max_depth,
                                            min_samples_split=min_samples_split,
                                            min_samples_leaf=min_samples_leaf,
                                            max_features=max_features,
                                            random_state=4
                                            )
            pipe = Pipeline([("prep", preprocessor),
                            ("rf", rf_model)])

            self._model = pipe

        print("RandomForestRegressor model was created.")


if __name__ == "__main__":
    pass
