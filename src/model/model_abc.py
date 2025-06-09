import numpy as np
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
from numpy import sqrt
from sklearn.base import clone
from sklearn.model_selection import TimeSeriesSplit
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit, GridSearchCV
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, make_scorer
from sklearn.base import RegressorMixin


class ModelBase(ABC):
    def __init__(self):
        self._model = None

    def learning_curve(self, X_train, y_train):
        print("Creating learning curve...")

        n = len(X_train)

        train_errors = []
        val_errors = []

        train_sizes = np.linspace(0.1, 1.0, 10)

        for frac in train_sizes:
            split_idx = int(n * frac)

            X_subset = X_train.iloc[:split_idx]
            y_subset = y_train.iloc[:split_idx]

            tscv = TimeSeriesSplit(n_splits=7)
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
                
                fold_train_scores.append(mean_absolute_error(np.expm1(y_tr), np.expm1(y_tr_pred)))
                fold_val_scores.append(mean_absolute_error(np.expm1(y_val), np.expm1(y_val_pred)))

            train_errors.append(np.mean(fold_train_scores))
            val_errors.append(np.mean(fold_val_scores))

        plt.plot(train_sizes * len(X_train), train_errors, label="Train MAE")
        plt.plot(train_sizes * len(X_train), val_errors, label="Validation MAE")
        plt.xlabel("Training Set Size")
        plt.ylabel("Train MAE")
        plt.title("learning curve")
        plt.legend()
        plt.grid(True)
        plt.show()

    def grid_search(self, pipeline, X_train, y_train, cv=5):
        for name, step in pipeline.named_steps.items():
            if isinstance(step, RegressorMixin):
                model_name = name
                break

        print(f"Searching for good hyperparameters for {model_name}...")

        if model_name == 'rf':
            param_grid = {
                "rf__n_estimators": [50, 100, 150, 200],
                "rf__max_features": ["sqrt", 0.5, 1],
                "rf__max_depth": [None, 5, 10, 15],
                "rf__min_samples_split": [2, 4, 6],
                "rf__min_samples_leaf": [1, 2, 3]
            }
        elif model_name == 'xgb':
            param_grid = {
                "xgb__n_estimators": [30, 50, 100],
                "xgb__max_depth": [5, 7, 8],
                "xgb__learning_rate": [0.05, 0.1, 0.15],
                "xgb__subsample": [0.6, 0.8, 1.0],
                "xgb__colsample_bytree": [0.3, 0.4, 0.6]
            }

        tscv = TimeSeriesSplit(n_splits=cv)

        search = RandomizedSearchCV(
            pipeline,
            param_distributions=param_grid,
            n_iter=60,
            cv=tscv,
            scoring=make_scorer(mean_squared_error, greater_is_better=False),
            n_jobs=-1,
            random_state=9,
            verbose=1
        )

        search.fit(X_train, y_train)

        print("Best CV MSE:", -search.best_score_)
        print("Best params:", search.best_params_)

        return search.best_estimator_
    
    def train(self, X_train, y_train):
        self._model.fit(X_train, y_train)

        print(f"{self.model_name} was trained.")

    def predict_pollutant(self, X_test, y_test):
        y_pred = self._model.predict(X_test)

        print(f"Inspect performance:")
        print("Test R2:", r2_score(np.expm1(y_test), np.expm1(y_pred)))
        print("Test MAE:", mean_absolute_error(np.expm1(y_test), np.expm1(y_pred)))
        print("Test RMSE:", sqrt(mean_squared_error(np.expm1(y_test), np.expm1(y_pred))))

        return y_pred

    def get_history(self):
        pass

    def display_metrics(self):
        pass

    def display_predictions(self):
        pass

    @property
    def model(self):
        return self._model

    @abstractmethod
    def _create_model(self):
        pass


if __name__ == "__main__":
    pass
