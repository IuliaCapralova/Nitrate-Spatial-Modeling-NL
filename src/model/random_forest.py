import os
import contextily as ctx
import geopandas as gpd
import seaborn as sns
import pandas as pd
import numpy as np
from numpy import sqrt
import matplotlib.pyplot as plt
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
    def __init__(self, preprocessor, n_estimators=200, max_depth=15, min_samples_split=4, min_samples_leaf=1, max_features=0.5):
        super().__init__()
        self._create_model(n_estimators=200, max_depth=15, min_samples_split=4, min_samples_leaf=1, max_features=0.5)

    def _create_model(self, preprocessor, n_estimators=200, max_depth=15, min_samples_split=4, min_samples_leaf=1, max_features=0.5):
        rf_model = RandomForestRegressor(n_estimators=200,
                                        max_depth=10,
                                        min_samples_split=5,
                                        random_state=42
                                        )
        pipe = Pipeline([
        ("prep", preprocessor),
        ("rf", rf_model)
        ])

        self._model = pipe


if __name__ == "__main__":
    pass
