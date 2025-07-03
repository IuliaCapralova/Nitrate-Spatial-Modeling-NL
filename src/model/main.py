import sys
import os
import contextily as ctx
import pandas as pd
import numpy as np
from numpy import sqrt
from typing import List
import seaborn as sns
from xgb_model import XGBmodel
from rf_model import RFmodel
from lr_model import LRmodel
from simple_ols_model import Simple_OLS
from data_model_prep import DataModelPrep
import matplotlib.pyplot as plt
import geopandas as gpd
import matplotlib.pyplot as plt
from typing import List
from matplotlib.colors import ListedColormap, BoundaryNorm
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from model.data_model_prep import DataModelPrep, DatasetSplit

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")


def prepare_data(pollutant: str, selected_features: List[str], holdout_cols: List[str]=None, train_years: List[int] = None, test_years: List[int] = None):
    data_prep = DataModelPrep("merged_dataset_1.csv")
    dataset_split, column_transformer, test_coords = data_prep.prepare(
        features=selected_features,
        target=pollutant,
        holdout_cols=holdout_cols,
        train_years=train_years,
        test_years=test_years
    )
    return dataset_split, column_transformer, test_coords

def ensemble_predictions(
    dataset_bundle,
    models_to_train: List[str],
    models_in_ensemble: List[str],
    include_ensemble_bar: bool = True,
    selected_models_for_plot: List[str] = None,
):
    # Unpack exactly as prepare_data() returns:
    dataset, preprocessor, test_coords = dataset_bundle
    X_train, y_train = dataset.X_train, dataset.y_train
    X_test,  y_test  = dataset.X_test,  dataset.y_test

    # 1) Train all requested models
    all_preds = {}
    for model_name in models_to_train:
        if model_name == "rf":
            model = RFmodel(preprocessor, grid_search=True, X_train=X_train, y_train=y_train)
        elif model_name == "xgb":
            model = XGBmodel(preprocessor, grid_search=True, X_train=X_train, y_train=y_train)
        elif model_name == "lr":
            model = LRmodel(preprocessor, grid_search=True, X_train=X_train, y_train=y_train)
        else:
            continue

        model.learning_curve(X_train, y_train)
        model.train(X_train, y_train)
        model.get_summary()
        y_pred = model.predict_pollutant(X_test, y_test)
        all_preds[model.model_name] = y_pred
        print(f"{model.model_name} finished and saved.")

    # return all_preds

    # 2) Build ensemble from only the subset
    ensemble_inputs = [all_preds[name] for name in models_in_ensemble if name in all_preds]
    if not ensemble_inputs:
        raise ValueError(f"No valid models found in models_in_ensemble: {models_in_ensemble}")

    stds = np.array([np.std(pred) for pred in ensemble_inputs])
    inv_stds = 1 / (stds + 1e-8)
    weights = inv_stds / inv_stds.sum()
    ensemble_pred = np.average(ensemble_inputs, axis=0, weights=weights)
    print("Ensemble weights:", dict(zip(models_in_ensemble, weights)))

    if include_ensemble_bar:
        all_preds["Ensemble"] = ensemble_pred

    # 3) Decide which models to plot
    plot_names = selected_models_for_plot or list(all_preds.keys())
    # Ensure Ensemble is included if requested
    if include_ensemble_bar and "Ensemble" not in plot_names:
        plot_names.append("Ensemble")
    plot_names = [name for name in plot_names if name in all_preds]

    # 4) Compute metrics
    r2_scores = [r2_score(y_test, all_preds[name]) for name in plot_names]
    # mae_scores = [mean_squared_error(y_test, all_preds[name]) for name in plot_names]
    # rmse_scores = [sqrt(mean_squared_error(y_test, all_preds[n])) for n in plot_names]

    y_test.to_csv("y_test.csv", index=False)
    pd.DataFrame(all_preds).to_csv("all_preds.csv", index=False)

    # 5) Plot
    plot_model_performance(plot_names, r2_scores, metric_name="R2")
    plot_true_vs_pred(y_test, ensemble_pred, title="Ensemble: true vs predicted", label="Ensemble")
    plot_spatial_predictions(test_coords, y_test, ensemble_pred, title="Ensemble predictions on map")

    # 6) Print summary
    print("\nR² scores:")
    for name, score in zip(plot_names, r2_scores):
        print(f"  {name:>10}: {score:.3f}")

    # print("\nMAE scores:")
    # for name, score in zip(plot_names, mae_scores):
    #     print(f"  {name:>10}: {score:.3f}")

    # print("\nRMSE scores:")
    # for name, score in zip(plot_names, rmse_scores):
    #     print(f"  {name:>10}: {score:.3f}")

def plot_model_performance(model_names: List[str], scores: List[float], metric_name: str = "R2"):
    plt.figure(figsize=(8, 5))

    bar_width = 0.6
    bars = plt.bar(
        model_names,
        scores,
        width=bar_width,
        color='lightsteelblue',
        edgecolor='navy',
        linewidth=1.5
    )

    plt.ylabel(metric_name, fontsize=14)
    plt.xlabel("Models", fontsize=14)
    plt.title(f"Model Performance ({metric_name})", fontsize=16)

    plt.ylim(0, 1)  # Fixed y-axis range for R²

    plt.xticks(rotation=30, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.6)

    for bar, score in zip(bars, scores):
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.02,
            f"{score:.3f}",
            ha='center',
            va='bottom',
            fontsize=10
        )

    plt.tight_layout()
    plt.show()

def plot_true_vs_pred(y_true, y_pred, title="true vs predicted", label="ensemble"):
    plt.figure(figsize=(10, 5))
    ax = plt.gca()

    sns.scatterplot(x=y_true, y=y_true, ax=ax, label="Ground truth", color="steelblue", linestyle="--")
    sns.scatterplot(x=y_true, y=y_pred, ax=ax, label=label, color="salmon", alpha=0.7)

    ax.set_xlabel("true ")
    ax.set_ylabel("predicted")
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.show()


def plot_spatial_predictions(coords, y_true, y_pred, title="Nitrate Map"):
    gdf = gpd.GeoDataFrame({
        'lon': coords['lon'].reset_index(drop=True),
        'lat': coords['lat'].reset_index(drop=True),
        'nitrate_pred': y_pred,
        'nitrate_true': y_true.reset_index(drop=True)
    }, geometry=gpd.points_from_xy(coords['lon'], coords['lat']), crs="EPSG:4326")
    
    # Remove top 3 nitrate_true outliers
    # gdf = gdf.sort_values(by="nitrate_true", ascending=False).iloc[3:]

    # Shared color scale
    vmin = min(gdf["nitrate_true"].min(), gdf["nitrate_pred"].min())
    vmax = max(gdf["nitrate_true"].max(), gdf["nitrate_pred"].max())

    fig, axs = plt.subplots(1, 2, figsize=(16, 8))

    # Plot in WGS84 (no reprojection)
    gdf.plot(ax=axs[0], column="nitrate_true", cmap="coolwarm", vmin=vmin, vmax=vmax, markersize=40, legend=False)
    ctx.add_basemap(axs[0], source=ctx.providers.OpenStreetMap.Mapnik, crs=gdf.crs, alpha=0.5)
    axs[0].set_title("True Nitrate", fontsize=18)

    gdf.plot(ax=axs[1], column="nitrate_pred", cmap="coolwarm", vmin=vmin, vmax=vmax, markersize=40, legend=False)
    ctx.add_basemap(axs[1], source=ctx.providers.OpenStreetMap.Mapnik, crs=gdf.crs, alpha=0.5)
    axs[1].set_title("Predicted Nitrate", fontsize=18)

    for ax in axs:
        ax.set_xlabel("Longitude", fontsize=14)
        ax.set_ylabel("Latitude", fontsize=14)
        ax.tick_params(axis='both', labelsize=12)
        ax.grid(True)

    # Shared colorbar
    sm = plt.cm.ScalarMappable(cmap="coolwarm", norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm._A = []
    cbar = fig.colorbar(sm, ax=axs, orientation="vertical", fraction=0.02, pad=0.02)
    cbar.set_label("Nitrate (mg/L)", fontsize=14)
    cbar.ax.tick_params(labelsize=12)

    plt.suptitle(title, fontsize=20)
    plt.tight_layout()
    plt.show()

def main():
    features = ['population', 'groundwater depth', 'elevation', 'landuse code',
                'precipitation', 'temperature', 'n deposition',
                'mainsoilclassification_1', 'organicmattercontent_1', 'density_1',
                'acidity_1', 'lon', 'lat'] # 'soil region', 'landuse code'
    holdout = ['lon', 'lat']
    pollutant = 'nitrate'
    train_years = list(range(2008, 2021))
    test_years = [2021, 2022, 2023]
    # test_years = [2021]

    # Choose model:
    models=["rf", "xgb", "lr"]
    # models=["rf", "xgb"]
    # models=["lr"]

    # Prepare data:
    dataset_bundle = prepare_data(pollutant, features, holdout, train_years, test_years)

    ###### Ensemble ######
    # ensemble_predictions(dataset_bundle, models)

    ensemble_predictions(
    dataset_bundle=dataset_bundle,
    models_to_train=["rf","xgb","lr"],
    models_in_ensemble=["RandomForestRegressor","XGBRegressor"],
    include_ensemble_bar=True,
    selected_models_for_plot=["RandomForestRegressor","XGBRegressor","Ridge"]
)

if __name__ == "__main__":
    main()
