import os
import shap
import pandas as pd
import numpy as np
import xgboost as xgb
import seaborn as sns
from numpy import sqrt
import matplotlib.pyplot as plt
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score, balanced_accuracy_score, roc_auc_score, make_scorer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import mean_absolute_error
from sklearn.inspection import permutation_importance
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import make_scorer, mean_squared_error
from model_abc import ModelBase


class XGBmodel(ModelBase):
    def __init__(self, preprocessor, grid_search=False, X_train=None, y_train=None, n_estimators=50, max_depth=7, learning_rate=0.1, colsample_bytree=0.6):
        super().__init__()
        self._create_model(preprocessor, grid_search, X_train, y_train, n_estimators, max_depth, learning_rate, colsample_bytree)

        final_estimator = self._model.steps[-1][1]
        self.model_name = type(final_estimator).__name__

    def _create_model(self, preprocessor, grid_search, X_train, y_train, n_estimators, max_depth, learning_rate, colsample_bytree):
        # Find hyperparameters using grid search
        if grid_search:
            xgb_model = xgb.XGBRegressor(objective="reg:squarederror", n_jobs=-1, random_state=4)
    
            pipe = Pipeline([
                ("prep", preprocessor),
                ("xgb", xgb_model)
                ])

            best_model = self.grid_search(pipe, X_train, y_train, cv=5)
            self._model = best_model
        
        # User defined hyperparameters
        else:
            xgb_model = xgb.XGBRegressor(n_estimators=n_estimators,
                            max_depth=max_depth,
                            learning_rate=learning_rate,
                            colsample_bytree=colsample_bytree,
                            objective='reg:squarederror',
                            random_state=4,
                            n_jobs=-1
                            )
            pipe = Pipeline([("prep", preprocessor),
                            ("xgb", xgb_model)
                            ])

            self._model = pipe


if __name__ == "__main__":
    pass
