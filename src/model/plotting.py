from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import contextily as ctx
from sklearn.metrics import r2_score


# ───────────────────────────────────────────────────────── choose_models
def choose_models(
    all_preds: Dict[str, np.ndarray],
    include_ensemble: bool = True,
    selected: Optional[List[str]] = None,
) -> List[str]:
    names = selected or list(all_preds.keys())
    if include_ensemble and "Ensemble" in all_preds and "Ensemble" not in names:
        names.append("Ensemble")
    return [n for n in names if n in all_preds]

# ───────────────────────────────────────────────────── compute_and_dump
def compute_and_dump_metrics(
    y_test: pd.Series,
    all_preds: Dict[str, np.ndarray],
    model_names: List[str],
    out_dir: str = "outputs",
) -> List[float]:
    import os
    os.makedirs(out_dir, exist_ok=True)
    y_test.to_csv(f"{out_dir}/y_test.csv", index=False)
    pd.DataFrame({m: all_preds[m] for m in model_names}).to_csv(
        f"{out_dir}/preds.csv", index=False
    )
    r2_vals = [r2_score(y_test, all_preds[m]) for m in model_names]
    print("\nR² scores")
    for m, v in zip(model_names, r2_vals):
        print(f"  {m:>15}: {v:.3f}")
    return r2_vals

# ───────────────────────────────────────────────────── spatial scatter
def plot_spatial_predictions(
    coords: pd.DataFrame,
    y_true: pd.Series,
    y_pred: np.ndarray,
    title: str = "Nitrate map",
    save_path: Optional[str] = None,
):
    gdf = gpd.GeoDataFrame(
        {
            "lon": coords["lon"].reset_index(drop=True),
            "lat": coords["lat"].reset_index(drop=True),
            "true": y_true.reset_index(drop=True),
            "pred": y_pred,
        },
        geometry=gpd.points_from_xy(coords["lon"], coords["lat"]),
        crs="EPSG:4326",
    )

    vmin, vmax = gdf[["true", "pred"]].to_numpy().min(), gdf[["true", "pred"]].to_numpy().max()
    fig, axs = plt.subplots(1, 2, figsize=(16, 8))

    gdf.plot(ax=axs[0], column="true", cmap="plasma", vmin=vmin, vmax=vmax,
             markersize=40, legend=False)
    ctx.add_basemap(axs[0], source=ctx.providers.OpenStreetMap.Mapnik, crs=gdf.crs)
    axs[0].set_title("True nitrate")

    gdf.plot(ax=axs[1], column="pred", cmap="plasma", vmin=vmin, vmax=vmax,
             markersize=40, legend=False)
    ctx.add_basemap(axs[1], source=ctx.providers.OpenStreetMap.Mapnik, crs=gdf.crs)
    axs[1].set_title("Predicted nitrate")

    for ax in axs:
        ax.set_xlabel("Lon")
        ax.set_ylabel("Lat")
        ax.grid(True)

    sm = plt.cm.ScalarMappable(cmap="plasma", norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm._A = []
    cbar = fig.colorbar(sm, ax=axs, fraction=0.03, pad=0.02)
    cbar.set_label("mg/L")

    plt.suptitle(title)
    plt.tight_layout()
    if save_path:
        save_path = os.path.join(save_path, "test_performance")
        file_path = os.path.join(save_path, f"spatial_test_pred.png")
        plt.savefig(file_path, dpi=300)
        plt.close(fig)
        print("Spatial test predictions are saved!")

def plot_metric_bars(
    model_metrics: Dict[str, Dict[str, float]],
    models_to_show: Optional[List[str]] = None,
    metrics_order: Optional[List[str]] = None,
    title: str = "Model comparison across MAE, RMSE and R²",
    save_path: Optional[str] = None,
):
    """
    Grouped-bar chart for multiple error metrics.

    Parameters
    ----------
    model_metrics   {model: {metric: value}}
                    e.g. {"Random Forest": {"MAE":0.29,"RMSE":1.04,"R2":0.75}, ...}
    models_to_show  list[str] | None
                    If given, filter/order bars to exactly these models.
    metrics_order   list[str] | None
                    How the metrics appear on the x-axis. Defaults to keys order.
    title           str
    save_path       str | None
    """
    # ------------------------------------------------ pick models / metrics
    models = models_to_show or list(model_metrics.keys())
    metrics = metrics_order or list(next(iter(model_metrics.values())).keys())

    # convert to 2-D array [metric_index, model_index]
    data = np.array([[model_metrics[m][met] for m in models] for met in metrics])

    # ------------------------------------------------ plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    n_metrics, n_models = data.shape
    bar_w = 0.8 / n_models          # total width ~0.8

    x = np.arange(n_metrics)        # metric positions

    palette = plt.cm.Blues(np.linspace(0.4, 0.9, n_models))
    for j, (model_name, color) in enumerate(zip(models, palette)):
        ax.bar(
            x + j * bar_w,
            data[:, j],
            width=bar_w,
            label=model_name,
            color=color,
        )
        # annotate each bar
        for xi, val in zip(x, data[:, j]):
            ax.text(
                xi + j * bar_w,
                val + 0.02 * (data.max() - data.min()),
                f"{val:.2f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    ax.set_xticks(x + bar_w * (n_models - 1) / 2)
    ax.set_xticklabels(metrics, fontsize=12)
    ax.set_ylabel("Error metrics", fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend(title="Model")
    ax.set_ylim(0, data.max() * 1.15)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()

    if save_path:
        save_path = os.path.join(save_path, "performance_hist")
        file_path = os.path.join(save_path, f"plot_metric_bars.png")
        plt.savefig(file_path, dpi=300)
        plt.close(fig)
        print("Metric histogram is saved!")
