import sys
import os
from xgb_model import XGBmodel
from rf_model import RFmodel
from lr_model import LinearRegressor
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data.data_model_prep import DataModelPrep
from typing import List
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def prepare_data(pollutant, selected_features: List[str]):
    data_prep = DataModelPrep("merged_dataset_1.csv")
    test_train_data = data_prep.process(selected_features, pollutant)
    column_transformer = data_prep.column_transformer(pollutant)

    return test_train_data, column_transformer

def predict_pollutant(processed, model_name: str):
    test_train_list, preprocessor = processed
    X_train, y_train, X_test, y_test = test_train_list

    grid_search = True

    if model_name == "rf":
        model = RFmodel(preprocessor, grid_search, X_train, y_train)
    elif model_name == "xgb":
        model = XGBmodel(preprocessor, grid_search, X_train, y_train)
    elif model_name == "lin_reg":
        model = LinearRegressor(preprocessor, grid_search, X_train, y_train)

    if model is not None:
        model.learning_curve(X_train, y_train)
        model.train(X_train, y_train)
        model.predict_pollutant(X_test, y_test)

        print(f"{model.model_name} finished.")

def main():
    pollutant = 'nitrate'

    # do not use 'landuse code' (not defined for all years)
    features = ['population', 'groundwater depth', 'elevation', 'soil region',
                'precipitation','temperature', 'n deposition',
                'mainsoilclassification_1', 'organicmattercontent_1', 'density_1',
                'acidity_1']
    
    ##### Random Forest ######
    processed = prepare_data(pollutant, features)
    model = 'rf'
    predict_pollutant(processed, model)

    ###### XGBoost ########
    processed = prepare_data(pollutant, features)
    model = 'xgb'
    predict_pollutant(processed, model)

    ###### OLS Linear Regressor ######
    # Choose type of OLS: ["simple_ols", "fixed_eff_ols", "regimes_ols"]
    model = 'simple_ols'
    if model == 'fixed_eff_ols' or model == 'regimes_ols':
        holdout_cols = 'soil region'
    else:
        holdout_cols = None
    predict_pollutant(processed, model, holdout_cols)


if __name__ == "__main__":
    main()
