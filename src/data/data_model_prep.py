import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from typing import List


class DataModelPrep():
    def __init__(self, file_name):
        curr_dir = os.getcwd()
        dataset_path = f"data/aligned/{file_name}"
        self._data = pd.read_csv(dataset_path)

    def process(self, selected_features: List[str], target: str, train_test=0.7):
        # remove rows in "veen" soil region, we do this step regardless of
        # wether it is included or not in "selected_features"
        self._filter_by_soil_region()

        self._columns_of_interest(selected_features, target)

        self._sort_by_date()

        # by droping Nans we exclude city regions
        # NOTE: should be changed
        self._data = self._data.dropna()

        self._fix_data_types(selected_features)

        self._transform_target(target)

        X_train, y_train, X_test, y_test = self._split_train_test(train_test, target)
        print(f"Train: {len(X_train)}")
        print(f"Test: {len(X_test)}")

        return [X_train, y_train, X_test, y_test]

    def _filter_by_soil_region(self):
        self._data = self._data[self._data["soil region"] != "veen"].copy()

    def _columns_of_interest(self, selected_features, target):
        if 'date' not in selected_features:
            columns_to_keep = selected_features + [target] + ['date']
        else:
            columns_to_keep = selected_features + [target]

        self._data = self._data[columns_to_keep].copy()

    def _sort_by_date(self):
        self._data["date"] = pd.to_datetime(self._data["date"])
        self._data = self._data.sort_values("date").reset_index(drop=True)

        # drop date after sorting
        self._data = self._data.drop(columns='date')
    
    def _fix_data_types(self, selected_features):
        if 'landuse code' in selected_features:
            self._data['landuse code'].astype('category')

        object_cols = self._data.select_dtypes(include='object').columns
        for col in object_cols:
            self._data[col] = self._data[col].astype('category')

    def _transform_target(self, target):
        self._data[target] = np.log1p(self._data[target])

    def _split_train_test(self, train_test, target):
        print(f"train_test: {train_test}")

        n = len(self._data)
        train_size = int(n * train_test)  # usually: n * 0.8

        train_df = self._data.iloc[:train_size]
        test_df = self._data.iloc[train_size:]

        print(train_df)

        X_train = train_df.drop(columns=[target]).copy()
        y_train = train_df[target]

        X_test = test_df.drop(columns=[target]).copy()
        y_test = test_df[target]

        return X_train, y_train, X_test, y_test
    
    def column_transformer(self, target):
        features = self._data.drop(columns=target).copy()
        categorical_cols = features.select_dtypes(include="category").columns.tolist()
        numerical_cols = features.select_dtypes(include=["float64", "int64"]).columns.tolist()

        preprocessor = ColumnTransformer([
            ("cat_ohe", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols),
            ("num_scaler", StandardScaler(), numerical_cols)
        ])

        return preprocessor


if __name__ == "__main__":
    pollutant = 'nitrate'

    # do not use 'landuse code' (not defined for all years)
    features = ['population', 'groundwater depth', 'elevation', 'soil region',
                'precipitation','temperature', 'n deposition',
                'mainsoilclassification_1', 'organicmattercontent_1', 'density_1',
                'acidity_1']
    
    data_prep = DataModelPrep("merged_dataset_1.csv")
    data_prep.process(features, pollutant, train_test=0.8)
