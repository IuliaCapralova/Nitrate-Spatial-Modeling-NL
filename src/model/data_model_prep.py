import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from typing import List
from dataclasses import dataclass


@dataclass
class DatasetSplit:
    X_train: pd.DataFrame
    y_train: pd.Series
    X_test: pd.DataFrame
    y_test: pd.Series

class DataModelPrep():
    def __init__(self, file_name):
        curr_dir = os.getcwd()
        dataset_path = f"../data/aligned/{file_name}"
        self._data = pd.read_csv(dataset_path)
        self._original_coords = None
        self._holdout_cols = None

    def prepare(self, features: List[str], target: str, holdout_cols: Optional[List[str]]=None, train_years: List[int] = None, test_years: List[int] = None) -> Tuple[DatasetSplit, ColumnTransformer]:
        self._holdout_cols = holdout_cols

        # remove rows in "veen" soil region, we do this step regardless of
        # wether it is included or not in "selected_features"
        # self._filter_soil()
        print(len(self._data))
        self._select_columns(features, target)
        print(len(self._data))

        self._sort_and_drop_date()
        print(len(self._data))

        self._drop_nans()                      # NOTE: should be changed
        print(len(self._data))

        self._remove_outliers(target_col=target, top_n=10)
        print(len(self._data))

        self._fix_dtypes()
        print(len(self._data))

        data_split = self._split(target, train_years, test_years)
        preprocessor = self._build_column_transformer(data_split.X_train, holdout_cols)

        print(f"Train: {len(data_split.X_train)}")
        print(f"Test: {len(data_split.X_test)}")

        coords = self._data[self._holdout_cols].copy()
        return data_split, preprocessor, coords.loc[data_split.X_test.index].reset_index(drop=True)

    def _filter_soil(self):
        # self._data = self._data[self._data["soil region"] != "veen"].copy()
        pass

    def _select_columns(self, features, target):
        required = set(features + [target, 'date'])
        available = set(self._data.columns)
        selected = list(required & available)
        
        # print(f"required: {required}")
        # print(f"available: {available}")
        # print(f"selected: {selected}")

        self._data = self._data[selected].copy()

    def _sort_and_drop_date(self):
        self._data["date"] = pd.to_datetime(self._data["date"])
        self._data["year"] = self._data["date"].dt.year
        self._data.sort_values("date", inplace=True)
        self._data.reset_index(drop=True, inplace=True)
        self._data.drop(columns="date", inplace=True)

    def _drop_nans(self):
        # self._data.dropna(inplace=True)
        self._data = self._data.dropna()

    def _remove_outliers(self, *, target_col: str, top_n: int = 10):
        df = self._data

        top_nitrate_outliers = list(df[target_col].sort_values()[-10:].index)
        df = df.drop(top_nitrate_outliers)
        print(f"len(df): {len(df)}")

        self._data = df
    
    def _fix_dtypes(self):
        for col in self._data.select_dtypes(include='object').columns:
            self._data[col] = self._data[col].astype('category')
        if 'landuse code' in self._data.columns:
            self._data['landuse code'] = self._data['landuse code'].astype('category')

    def _split(self, target, train_years, test_years):
        self._original_coords = self._data[["lon", "lat"]].copy()

        train_df = self._data[self._data["year"].isin(train_years)].copy()
        test_df = self._data[self._data["year"].isin(test_years)].copy()

        drop_cols = [target] + self._holdout_cols + ["year"]

        X_train = train_df.drop(columns=drop_cols).copy()
        y_train = train_df[target]

        X_test = test_df.drop(columns=drop_cols).copy()
        y_test = test_df[target]

        return DatasetSplit(X_train, y_train, X_test, y_test)
    
    def _build_column_transformer(self, X, holdout_cols:List[str]=None):
        # in case linear reg with regimes or fixed effects is applied
        if holdout_cols is None:
            holdout_cols = []

        categorical = X.select_dtypes(include="category").columns.difference(holdout_cols).tolist()
        numerical = X.select_dtypes(include=["float64", "int64"]).columns.difference(holdout_cols).tolist()

        preprocessor = ColumnTransformer([
            ("cat_ohe", OneHotEncoder(handle_unknown="ignore", drop='first', sparse_output=False), categorical),
            ("num_scaler", StandardScaler(), numerical)
        ], remainder="passthrough")

        self._save_preprocessor(preprocessor)

        return preprocessor
    
    def _save_preprocessor(self, preprocessor):
        current_dir = os.getcwd()
        model_dir = os.path.join(current_dir, "../trained_models")
        save_path = os.path.join(model_dir, f"preprocessor.pkl")

        # save
        joblib.dump(preprocessor, save_path)


if __name__ == "__main__":
    # do not use 'landuse code' (not defined for all years)
    features = ['population', 'groundwater depth', 'elevation', 'soil region',
                'precipitation','temperature', 'n deposition',
                'organicmattercontent_1', 'density_1',
                'acidity_1', 'lon', 'lat'] # 'mainsoilclassification_1', 
    holdout = ['lon', 'lat']
    pollutant = 'nitrate'
    
    data_prep = DataModelPrep("merged_dataset_1.csv")
    dataset, preprocessor, test_coords = data_prep.prepare(features, pollutant, holdout_cols=holdout)

    # print(dataset.X_test)
    print(test_coords)

    X_train_scaled = preprocessor.fit_transform(dataset.X_train)
    X_test_scaled = preprocessor.transform(dataset.X_test)

    # print(X_train_scaled)
