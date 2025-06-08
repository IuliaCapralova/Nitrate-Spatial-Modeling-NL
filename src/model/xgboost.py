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
    def __init__(self):
        pass

    def _create_model(self):
        xgb_model =  xgb(n_estimators=50,
                        max_depth=8,
                        learning_rate=00.15,
                        subsample=0.6,
                        colsample_bytree=0.6,
                        objective='reg:squarederror',
                        random_state=42,
                        n_jobs=-1
                    )
        self._model = xgb_model


if __name__ == "__main__":
    pass
