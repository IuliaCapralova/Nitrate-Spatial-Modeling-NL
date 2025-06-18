import sys
import os
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
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from model.data_model_prep import DataModelPrep, DatasetSplit


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

def ensemble_predictions(dataset_bundle, models: str):
    dataset, preprocessor, test_coords = dataset_bundle

    X_train, y_train = dataset.X_train, dataset.y_train
    X_test, y_test = dataset.X_test, dataset.y_test

    grid_search = True
    predictions = []
    model_names = []
    r2_scores = []

    for model_name in models:
        if model_name == "rf":
            model = RFmodel(preprocessor, grid_search, X_train, y_train)
        elif model_name == "xgb":
            model = XGBmodel(preprocessor, grid_search, X_train, y_train)
        elif model_name == "lr":
            model = LRmodel(preprocessor, grid_search, X_train, y_train)
        elif model_name == "simple_ols":
            model = Simple_OLS(preprocessor, X_train.columns)

        if model is not None:
            model.learning_curve(X_train, y_train)
            model.train(X_train, y_train)
            model.get_summary()
            y_pred = model.predict_pollutant(X_test, y_test)

            predictions.append(y_pred)
            model_names.append(model.model_name)
            r2_scores.append(r2_score(y_test, y_pred))

            print(f"{model.model_name} finished.")

    # ensemble_pred = np.mean(predictions, axis=0)
    # ---- Ensemble construction ----

    print(predictions)
    model_stds = [np.std(pred) for pred in predictions]
    print(model_stds)
    inv_model_stds = 1 / (np.array(model_stds) + 1e-8)
    model_weights = inv_model_stds / inv_model_stds.sum()

    ensemble_pred = np.average(predictions, axis=0, weights=model_weights)

    # --------------------------------

    ensemble_r2 = r2_score(y_test, ensemble_pred)
    r2_scores.append(ensemble_r2)
    model_names.append("Ensemble")

    print("\nEnsemble Performance:")
    print("Test R2:", r2_score(y_test, ensemble_pred))
    print("Test MAE:", mean_absolute_error(y_test, ensemble_pred))
    print("Test RMSE:", sqrt(mean_squared_error(y_test, ensemble_pred)))

    plot_model_performance(model_names, r2_scores, metric_name="R2")
    plot_true_vs_pred(y_test, ensemble_pred, title="Ensemble: true vs predicted Nitrate", label="Ensemble prediction")

    plot_spatial_predictions(test_coords, y_test, ensemble_pred, title="Ensemble predictions on map")

def plot_model_performance(model_names: List[str], scores: List[float], metric_name: str = "MAE"):
    plt.figure(figsize=(8, 5))
    bars = plt.bar(model_names, scores)
    plt.ylabel(metric_name)
    plt.title(f"Model Performance ({metric_name})")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=15)
    
    # annotate each bar with score
    for bar, score in zip(bars, scores):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height + 0.01, f"{score:.3f}", 
                ha='center', va='bottom', fontsize=9)

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

# def plot_spatial_predictions(coords, y_true, y_pred, title="Nitrate Map"):
#     gdf = gpd.GeoDataFrame({
#         'lon': coords['lon'].reset_index(drop=True),
#         'lat': coords['lat'].reset_index(drop=True),
#         'nitrate_pred': y_pred,
#         'nitrate_true': y_true.reset_index(drop=True)
#     }, geometry=gpd.points_from_xy(coords['lon'], coords['lat']))
    
#     gdf.crs = "EPSG:4326"

#     fig, axs = plt.subplots(1, 2, figsize=(16, 8))

#     gdf.plot(ax=axs[0], column="nitrate_true", cmap="plasma", legend=True, markersize=40)
#     axs[0].set_title("True Nitrate")

#     gdf.plot(ax=axs[1], column="nitrate_pred", cmap="plasma", legend=True, markersize=40)
#     axs[1].set_title("Predicted Nitrate")

#     for ax in axs:
#         ax.set_xlabel("Longitude")
#         ax.set_ylabel("Latitude")
#         ax.grid(True)

#     plt.tight_layout()
#     plt.show()

def plot_spatial_predictions(coords, y_true, y_pred, title="Nitrate Map"):
    gdf = gpd.GeoDataFrame({
        'lon': coords['lon'].reset_index(drop=True),
        'lat': coords['lat'].reset_index(drop=True),
        'nitrate_pred': y_pred,
        'nitrate_true': y_true.reset_index(drop=True)
    }, geometry=gpd.points_from_xy(coords['lon'], coords['lat']))
    
    gdf.crs = "EPSG:4326"

    # Shared color scale
    vmin = min(gdf["nitrate_true"].min(), gdf["nitrate_pred"].min())
    vmax = max(gdf["nitrate_true"].max(), gdf["nitrate_pred"].max())

    fig, axs = plt.subplots(1, 2, figsize=(16, 8))

    gdf.plot(ax=axs[0], column="nitrate_true", cmap="plasma", vmin=vmin, vmax=vmax, legend=True, markersize=40)
    axs[0].set_title("True Nitrate")

    gdf.plot(ax=axs[1], column="nitrate_pred", cmap="plasma", vmin=vmin, vmax=vmax, legend=True, markersize=40)
    axs[1].set_title("Predicted Nitrate")

    for ax in axs:
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.grid(True)

    plt.tight_layout()
    plt.show()


def main():
    features = ['population', 'groundwater depth', 'elevation', 'soil region',
                'precipitation', 'temperature', 'n deposition',
                'mainsoilclassification_1', 'organicmattercontent_1', 'density_1',
                'acidity_1', 'lon', 'lat'] # 'soil region', 'landuse code'
    holdout = ['lon', 'lat']
    pollutant = 'nitrate'
    train_years = list(range(2008, 2021))
    test_years = [2021]

    # Choose model:
    models=["rf", "xgb", "lr"]

    # Prepare data:
    dataset_bundle = prepare_data(pollutant, features, holdout, train_years, test_years)

    ###### Ensemble ######
    ensemble_predictions(dataset_bundle, models)


if __name__ == "__main__":
    main()
