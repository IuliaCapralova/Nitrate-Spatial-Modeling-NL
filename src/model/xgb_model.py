import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.pipeline import Pipeline
from model_abc import ModelBase
from sklearn.base import clone
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from sklearn.metrics import make_scorer, mean_absolute_error
from sklearn.compose import TransformedTargetRegressor

import warnings
warnings.filterwarnings(
    "ignore",
    message="Found unknown categories in columns",  # exact phrase start
    category=UserWarning,
    module="sklearn.preprocessing._encoders",
)


class XGBmodel(ModelBase):
    def __init__(self, preprocessor, grid_search=False, X_train=None, y_train=None, n_estimators=50, max_depth=7, learning_rate=0.1, colsample_bytree=0.6):
        super().__init__()
        self._create_model(preprocessor, grid_search, X_train, y_train, n_estimators, max_depth, learning_rate, colsample_bytree)

        final_estimator = self._model.regressor.named_steps["xgb"]
        self.model_name = type(final_estimator).__name__

    def _create_model(self, preprocessor, grid_search, X_train, y_train, n_estimators, max_depth, learning_rate, colsample_bytree):
        # Find hyperparameters using grid search
        if grid_search:
            xgb_model = xgb.XGBRegressor(objective="reg:squarederror", n_jobs=-1, random_state=123)
    
            pipe = Pipeline([
                ("prep", preprocessor),
                ("xgb", xgb_model)
                ])
            
            full_pipeline = TransformedTargetRegressor(
                regressor=pipe,
                # func=np.log1p,
                # inverse_func=np.expm1
            )

            best_model = self.grid_search(full_pipeline, X_train, y_train, cv=5)
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
            
            full_pipeline = TransformedTargetRegressor(
                regressor=pipe,
                # func=np.log1p,
                # inverse_func=np.expm1
            )

            self._model = full_pipeline

    def grid_search(self, full_pipeline, X_train, y_train, cv=5):
        model_name = type(full_pipeline.regressor.named_steps["xgb"]).__name__
        print(f"Searching for good hyperparameters for {model_name}...")

        # param_grid = {
        #         "regressor__xgb__n_estimators": [30, 50, 100],
        #         "regressor__xgb__max_depth": [5, 7, 8],
        #         "regressor__xgb__learning_rate": [0.05, 0.1, 0.15],
        #         "regressor__xgb__subsample": [0.6, 0.8, 1.0],
        #         "regressor__xgb__colsample_bytree": [0.3, 0.4, 0.6]
        #     }

        param_grid = {
                "regressor__xgb__n_estimators": [50, 100, 150, 200, 250],
                "regressor__xgb__max_depth": [3, 4, 6, 10, 15, 20],
                "regressor__xgb__learning_rate": [0.05, 0.01, 0.1],
                "regressor__xgb__subsample": [0.4, 0.5, 0.6, 0.8],
                "regressor__xgb__colsample_bytree": [0.4, 0.6, 0.8],
                "regressor__xgb__reg_alpha": [0.1, 0.5, 0.7],
                "regressor__xgb__reg_lambda": [2, 3, 5, 8]
            }

        tscv = TimeSeriesSplit(n_splits=cv)

        search = RandomizedSearchCV(
            full_pipeline,
            param_distributions=param_grid,
            n_iter=100,
            cv=tscv,
            scoring="r2",   # make_scorer(mean_absolute_error, greater_is_better=False)
            n_jobs=-1,
            random_state=9,
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
        fitted_model = inner_pipeline.named_steps['xgb']

        feature_names = fitted_preprocessor.get_feature_names_out()

        importances = fitted_model.feature_importances_

        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values(by='importance', ascending=False)

        print(importance_df)
        print("\n")


if __name__ == "__main__":
    pass