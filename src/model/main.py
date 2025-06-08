from random_forest import RFmodel
from xgboost import XGBModel
from linear_reg import LinearRegressor
from data.data_model_prep import DataModelPrep
from typing import List


def prepare_data(pollutant, selected_features: List[str]):
    data_prep = DataModelPrep("merged_dataset_1.csv")
    test_train_data = data_prep.process(selected_features, pollutant, train_test=0.8)
    column_transformer = data_prep.column_transformer()

    return test_train_data, column_transformer

def predict_pollutant(processed, model_list: List[str]):
    X_train, y_train, X_test, y_test, preprocessor = processed

    for model_name in model_list:
        if model_name == "rf":
            model = RFmodel(preprocessor)
        if model_name == "xgb":
            model = XGBModel(preprocessor)
        if model_name == "lin_reg":
            model = LinearRegressor(preprocessor)

        if model is not None:
            model.train(X_train, y_train)
            # predict



def main():
    pollutant = 'nitrate'

    # do not use 'landuse code' (not defined for all years)
    features = ['population', 'groundwater depth', 'elevation', 'soil region',
                'landuse code', 'precipitation','temperature', 'n deposition',
                'mainsoilclassification_1', 'organicmattercontent_1', 'density_1',
                'acidity_1']
    
    processed = prepare_data(pollutant, features)

    predict_pollutant(processed)


if __name__ == "__main__":
    main()
