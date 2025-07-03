import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import make_scorer, mean_squared_error
from model_abc import ModelBase
from sklearn.compose import TransformedTargetRegressor
from sklearn.base import clone

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")


class LRmodel(ModelBase):
    def __init__(self, preprocessor, grid_search=False, X_train=None, y_train=None, alpha=0.01):
        super().__init__()
        self._create_model(preprocessor, grid_search, X_train, y_train,alpha)

        final_estimator = self._model.regressor.named_steps["lr"]
        self.model_name = type(final_estimator).__name__

    def _create_model(self, preprocessor, grid_search, X_train, y_train, alpha):
        # Find hyperparameters using grid search
        if grid_search:
            lr_model = Ridge(random_state=4)

            pipe = Pipeline([
                ("prep", preprocessor),
                ("lr", lr_model)
            ])

            full_pipeline = TransformedTargetRegressor(
                regressor=pipe,
                func=np.log1p,
                inverse_func=np.expm1
            )

            best_model = self.grid_search(full_pipeline, X_train, y_train, cv=5)
            self._model = best_model

        # User defined hyperparameters
        else:
            lr_model = Ridge(alpha=alpha, random_state=4)

            pipe = Pipeline([
                ("prep", preprocessor),
                ("lr", lr_model)
            ])

            full_pipeline = TransformedTargetRegressor(
                regressor=pipe,
                func=np.log1p,
                inverse_func=np.expm1
            )

            self._model = full_pipeline

        print("Linear Regression model was created.")

    def grid_search(self, full_pipeline, X_train, y_train, cv):
        model_name = type(full_pipeline.regressor.named_steps["lr"]).__name__
        print(f"Searching for good hyperparameters for {model_name}...")

        # alphas = np.logspace(-4, 4, 50)
        alphas = np.logspace(-3, 1, 10)
        tscv = TimeSeriesSplit(n_splits=5)
        param_grid = {
            "regressor__lr__alpha": alphas
        }

        search = GridSearchCV(
            estimator=full_pipeline,
            param_grid=param_grid,
            scoring="neg_mean_absolute_error",  # or "neg_root_mean_squared_error"
            cv=tscv,
            n_jobs=-1,
            verbose=1
        )
        search.fit(X_train, y_train)

        print("Best CV MAE:", -search.best_score_)
        print("Best params:", search.best_params_)

        best_model = search.best_estimator_
        model = clone(best_model)

        return model
    
    def get_summary(self):

        if isinstance(self._model, TransformedTargetRegressor):
            print("Yes, this is a TransformedTargetRegressor.")
        else:
            print("Nope, it's not.")

        print("Inspect feature importances")

        inner_pipeline = self._model.regressor_
        fitted_preprocessor = inner_pipeline.named_steps['prep']
        fitted_model = inner_pipeline.named_steps['lr']

        feature_names = fitted_preprocessor.get_feature_names_out()

        coefficients = fitted_model.coef_

        importance_df = pd.DataFrame({
            'feature': feature_names,
            'coefficient': coefficients
        }).sort_values(by='coefficient', key=np.abs, ascending=False)
        print(importance_df)
        print("\n")


if __name__ == "__main__":
    pass