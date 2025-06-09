import pandas as pd
import numpy as np
from spreg import OLS_Regimes
from pysal.model import spreg
import statsmodels.formula.api as smf
from libpysal.weights import KNN
from spreg import OLS
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from model_abc import ModelBase


class LinearRegressor(ModelBase):
    def __init__(self):
        pass

    def _create_model(self):
        model = spreg.OLS(y_train, X_train, name_y='nitrate', name_x=feature_names)
        self._model = model


if __name__ == "__main__":
    pass
