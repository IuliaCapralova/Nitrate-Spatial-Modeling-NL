from sklearn.model_selection import RandomizedSearchCV, TimeSeriesSplit, GridSearchCV
from sklearn.base import RegressorMixin


def grid_search(pipeline, X_train, y_train, cv=3):
    for name, step in pipeline.named_steps.items():
        if isinstance(step, RegressorMixin):
            model_name = name
            break

    if model_name == 'rf':
        param_grid = {
            "rf__n_estimators": [50, 100, 150, 200],
            "rf__max_features": ["sqrt", 0.5, 1],
            "rf__max_depth": [None, 5, 10, 15],
            "rf__min_samples_split": [2, 4, 6],
            "rf__min_samples_leaf": [1, 2, 3]
        }
    elif model_name == 'xgb':
        param_dist = {
            "xgb__n_estimators": [30, 50, 100],
            "xgb__max_depth": [5, 7, 8],
            "xgb__learning_rate": [0.05, 0.1, 0.15],
            "xgb__subsample": [0.6, 0.8, 1.0],
            "xgb__colsample_bytree": [0.3, 0.4, 0.6]
        }

    tscv = TimeSeriesSplit(n_splits=5)

    grid_search = GridSearchCV(
    estimator=pipeline,
    param_grid=param_grid,
    scoring="neg_mean_squared_error",  # or 'r2', 'neg_mae', etc.
    cv=tscv,
    verbose=1,
    n_jobs=-1
    )

    grid_search.fit(X_train, y_train)

    print("Best parameters:", grid_search.best_params_)
    print("Best score (neg MSE):", grid_search.best_score_)
