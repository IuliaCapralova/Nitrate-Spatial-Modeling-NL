import os
import numpy as np
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
from numpy import sqrt
from sklearn.base import clone
import joblib
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, make_scorer

import warnings
warnings.filterwarnings(
    "ignore",
    message="Found unknown categories in columns",  # exact phrase start
    category=UserWarning,
    module="sklearn.preprocessing._encoders",
)

class ModelBase(ABC):
    def __init__(self):
        self._model = None

    def learning_curve(self, X_train, y_train):
        print("Creating learning curve...")

        n_samples = len(X_train)

        train_errors = []
        val_errors = []

        train_sizes = np.linspace(0.1, 1.0, 10)

        for frac in train_sizes:
            split_idx = int(n_samples * frac)

            X_subset = X_train.iloc[:split_idx]
            y_subset = y_train.iloc[:split_idx]

            tscv = TimeSeriesSplit(n_splits=5)
            fold_train_scores = []
            fold_val_scores = []

            for train_idx, val_idx in tscv.split(X_subset):
                X_tr, X_val = X_subset.iloc[train_idx], X_subset.iloc[val_idx]
                y_tr, y_val = y_subset.iloc[train_idx], y_subset.iloc[val_idx]
                
                # create fresh model
                curr_model = clone(self._model)
                curr_model.fit(X_tr, y_tr)

                y_tr_pred = curr_model.predict(X_tr)
                y_val_pred = curr_model.predict(X_val)

                # clip predictions
                y_tr_pred = np.clip(y_tr_pred, 0, 10)
                y_val_pred = np.clip(y_val_pred, 0, 10)
                
                fold_train_scores.append(mean_absolute_error(y_tr, y_tr_pred))
                fold_val_scores.append(mean_absolute_error(y_val, y_val_pred))

            train_errors.append(np.mean(fold_train_scores))
            val_errors.append(np.mean(fold_val_scores))

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(train_sizes * n_samples, train_errors, label="Train MAE")
        ax.plot(train_sizes * n_samples, val_errors,  label="Val MAE")
        ax.set_xlabel("Training set size")
        ax.set_ylabel("MAE")
        ax.set_title(f"{self.model_name} – learning curve")
        ax.legend()
        ax.grid(True)

        # save in plot in folder
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.join(curr_dir, "..", "..", "plots", "learning_curves")
        out_dir = os.path.abspath(out_dir)        # normalise to an absolute path
        os.makedirs(out_dir, exist_ok=True)       # create the folders if missing
        file_path = os.path.join(out_dir, f"{self.model_name}_curve.png")
        fig.savefig(file_path, dpi=300)
        plt.close(fig)

    def train(self, X_train, y_train):
        self._model.fit(X_train, y_train)
        self._save_model()
        print(f"{self.model_name} was trained and saved.")

    def predict_pollutant(self, X_test, y_test):
        y_pred = self._model.predict(X_test)
        y_pred = np.maximum(y_pred, 0)

        print(f"Inspect performance on Test set:")
        print("Test R2:", r2_score(y_test, y_pred))
        print("Test MAE:", mean_absolute_error(y_test, y_pred))
        print("Test RMSE:", sqrt(mean_squared_error(y_test, y_pred)))
        return y_pred
    
    def _save_model(self):
        current_dir = os.getcwd()
        model_dir = os.path.join(current_dir, "../trained_models")
        save_path = os.path.join(model_dir, f"{self.model_name}_trained.pkl")

        # save
        joblib.dump(self._model, save_path)

    def get_history(self):
        pass

    def display_metrics(self):
        pass

    def display_predictions(self):
        pass

    @property
    def model(self):
        return self._model

    def _create_model(self):
        pass


if __name__ == "__main__":
    pass
