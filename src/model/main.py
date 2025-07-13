import os, sys, warnings
from typing import List

warnings.filterwarnings(
    "ignore",
    message=r"^Found unknown categories in columns \[.*\] during transform",
    category=UserWarning,
    module=r"sklearn\.preprocessing\._encoders",
)

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx
from sklearn.metrics import r2_score
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from math import sqrt
from pathlib import Path

from rf_model       import RFmodel
from xgb_model      import XGBmodel
from lr_model       import LRmodel
from data_model_prep import DataModelPrep
from ensemble       import create_ensemble
from plotting        import (
    choose_models,
    compute_and_dump_metrics,
    plot_spatial_predictions,
    plot_metric_bars
)


# ───────────────────────────────────────────────────────────────────────────────
# 1)  DATA PREP
# ───────────────────────────────────────────────────────────────────────────────
def prepare_data(pollutant: str, selected_features, holdout_cols, train_years, test_years):
    prep = DataModelPrep("merged_dataset_1.csv")
    dataset_split, col_transformer, test_coords = prep.prepare(
        features=selected_features,
        target=pollutant,
        holdout_cols=holdout_cols,
        train_years=train_years,
        test_years=test_years,
    )
    return dataset_split, col_transformer, test_coords


# ───────────────────────────────────────────────────────────────────────────────
# 2)  TRAINING
# ───────────────────────────────────────────────────────────────────────────────
def train_models( dataset_bundle, model_keys: List[str]) -> tuple[dict[str, np.ndarray], pd.Series]:

    dataset, preproc, _coords = dataset_bundle
    X_train, y_train = dataset.X_train, dataset.y_train
    X_test,  y_test  = dataset.X_test,  dataset.y_test

    all_preds, model_metrics = {}, {}

    for key in model_keys:
        if key == "rf":
            model = RFmodel(preproc, grid_search=True, X_train=X_train, y_train=y_train)
        elif key == "xgb":
            model = XGBmodel(preproc, grid_search=True, X_train=X_train, y_train=y_train)
        elif key == "lr":
            model = LRmodel(preproc, grid_search=True, X_train=X_train, y_train=y_train)
        else:
            continue

        model.learning_curve(X_train, y_train)
        model.train(X_train, y_train)
        model.get_summary()
        y_pred = model.predict_pollutant(X_test, y_test)
        all_preds[model.model_name] = y_pred
        print(f"{model.model_name} trained and saved.")

        model_metrics[model.model_name] = {
            "MAE":  mean_absolute_error(y_test, y_pred),
            "RMSE": sqrt(mean_squared_error(y_test, y_pred)),
            "R2":   r2_score(y_test, y_pred),
        }

    return all_preds, y_test, model_metrics


# ───────────────────────────────────────────────────────────────────────────────
# 3)  MAIN
# ───────────────────────────────────────────────────────────────────────────────
def main() -> None:
    FEATURES = [
        "population",
        "groundwater depth",
        "elevation",
        "landuse code",
        "precipitation",
        "temperature",
        "n deposition",
        "mainsoilclassification_1",
        "organicmattercontent_1",
        "density_1",
        "acidity_1",
        "lon",
        "lat",
    ]
    HOLDOUT    = ["lon", "lat"]
    TRAIN_YRS  = list(range(2008, 2021))
    TEST_YRS   = [2021, 2022, 2023]
    MODELS     = ["rf", "xgb", "lr"]
    ENS_MODELS = ["RandomForestRegressor", "XGBRegressor"]


    # set up plot saving
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(curr_dir, "..", "..", "plots")
    SAVE_PLOT_PATH = out_dir

    # -------- data --------
    data_bundle = prepare_data("nitrate", FEATURES, HOLDOUT, TRAIN_YRS, TEST_YRS)
    dataset_split, col_transformer, test_coords = data_bundle 

    # -------- training --------
    all_preds, y_test, metrics_dict = train_models(data_bundle, MODELS)

    # -------- ensemble --------
    ens_pred, weights = create_ensemble(all_preds, ENS_MODELS)
    all_preds["Ensemble"] = ens_pred
    print("Ensemble weights:", {k: f"{w:.2f}" for k, w in zip(ENS_MODELS, weights)})

    metrics_dict["Ensemble"] = {
        "MAE":  mean_absolute_error(y_test, ens_pred),
        "RMSE": sqrt(mean_squared_error(y_test, ens_pred)),
        "R2":   r2_score(y_test, ens_pred),
    }

    # --------- metric histogram --------
    models_for_bars = ["RandomForestRegressor", "XGBRegressor", "Ensemble"]

    plot_metric_bars(
        model_metrics=metrics_dict,
        models_to_show=models_for_bars,
        metrics_order=["MAE", "RMSE", "R2"],
        save_path = SAVE_PLOT_PATH
    )

    # --------- spatial map --------
    plot_spatial_predictions(
        coords=test_coords,
        y_true=y_test,
        y_pred=ens_pred,
        title="Ensemble nitrate map",
        save_path=SAVE_PLOT_PATH,
    )


if __name__ == "__main__":
    main()
