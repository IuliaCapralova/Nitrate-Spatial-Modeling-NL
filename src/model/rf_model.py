import pandas as pd
import numpy as np
import joblib
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit
from sklearn.metrics import make_scorer, mean_squared_error
from model_abc import ModelBase
from sklearn.compose import TransformedTargetRegressor
from sklearn.base import clone


class RFmodel(ModelBase):
    def __init__(self, preprocessor, grid_search=False, X_train=None, y_train=None, n_estimators=200, max_depth=15, min_samples_split=2, min_samples_leaf=1, max_features=0.5):
        super().__init__()
        self._create_model(preprocessor, grid_search, X_train, y_train, n_estimators, max_depth, min_samples_split, min_samples_leaf, max_features)

        final_estimator = self._model.regressor.named_steps["rf"]
        self.model_name = type(final_estimator).__name__

    def _create_model(self, preprocessor, grid_search, X_train, y_train, n_estimators, max_depth, min_samples_split, min_samples_leaf, max_features):
        # Find hyperparameters using grid search
        if grid_search:
            rf_model = RandomForestRegressor(random_state=42, oob_score=False)

            pipe = Pipeline([
                ("prep", preprocessor),
                ("rf", rf_model)
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
            rf_model = RandomForestRegressor(n_estimators=n_estimators,
                                            max_depth=max_depth,
                                            min_samples_split=min_samples_split,
                                            min_samples_leaf=min_samples_leaf,
                                            max_features=max_features,
                                            random_state=4)
            pipe = Pipeline([("prep", preprocessor),
                            ("rf", rf_model)])

            full_pipeline = TransformedTargetRegressor(
                regressor=pipe,
                func=np.log1p,
                inverse_func=np.expm1)

            self._model = full_pipeline

        print("RandomForestRegressor model was created.")

    def grid_search(self, full_pipeline, X_train, y_train, cv):
        model_name = type(full_pipeline.regressor.named_steps["rf"]).__name__
        print(f"Searching for good hyperparameters for {model_name}...")

        param_grid = {
                "regressor__rf__n_estimators": [50, 100, 150, 200],
                "regressor__rf__max_features": ["sqrt", 0.5, 1],
                "regressor__rf__max_depth": [None, 5, 10, 15],
                "regressor__rf__min_samples_split": [2, 4, 6],
                "regressor__rf__min_samples_leaf": [1, 2, 3]
            }

        tscv = TimeSeriesSplit(n_splits=cv)
        search = RandomizedSearchCV(
            full_pipeline,
            param_distributions=param_grid,
            n_iter=60,
            cv=tscv,
            scoring=make_scorer(mean_absolute_error, greater_is_better=False),
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
        fitted_model = inner_pipeline.named_steps['rf']

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