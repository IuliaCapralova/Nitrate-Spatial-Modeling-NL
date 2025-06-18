import numpy as np
import matplotlib.pyplot as plt
from spreg import OLS
from numpy import sqrt
from sklearn.base import clone
from model_abc import ModelBase
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error


class Simple_OLS(ModelBase):
    def __init__(self, preprocessor, feature_names_in):
        super().__init__()
        self.preprocessor = preprocessor
        self.feature_names_in = feature_names_in

    def get_feature_names(self):
        return list(self.preprocessor.get_feature_names_out(self.feature_names_in))
    
    # def learning_curve(self, X_train, y_train):
    #     pass

    def learning_curve(self, X_train, y_train):
        print("Creating learning curve...")

        n = len(X_train)

        train_errors = []
        val_errors = []

        train_sizes = np.linspace(0.3, 1.0, 10)

        for frac in train_sizes:
            split_idx = int(n * frac)

            X_subset = X_train.iloc[:split_idx]
            y_subset = y_train.iloc[:split_idx]

            print(f"Length of subset before cv: {len(X_subset)}")

            tscv = TimeSeriesSplit(n_splits=2)
            fold_train_scores = []
            fold_val_scores = []

            for train_idx, val_idx in tscv.split(X_subset):

                X_tr, X_val = X_subset.iloc[train_idx], X_subset.iloc[val_idx]
                y_tr, y_val = y_subset.iloc[train_idx], y_subset.iloc[val_idx]

                # prep = clone(self.preprocessor)

                X_tr = self.preprocessor.fit_transform(X_tr)
                X_val = self.preprocessor.transform(X_val)

                y_tr = y_tr.values.reshape(-1, 1)
                y_val = y_val.values.reshape(-1, 1)

                feature_names = self.get_feature_names()
                
                # create fresh model
                y_tr_transformed = np.log1p(y_tr)
                curr_model = OLS(y_tr_transformed, X_tr, name_y='nitrate', name_x=feature_names)

                beta = curr_model.betas.flatten()
                X_train_with_const = np.hstack([np.ones((X_tr.shape[0], 1)), X_tr])
                X_val_with_const = np.hstack([np.ones((X_val.shape[0], 1)), X_val])
                # X_val_with_const = X_val
                # X_train_with_const = X_tr

                y_tr_pred = X_train_with_const @ beta
                y_val_pred = X_val_with_const @ beta
                
                fold_train_scores.append(mean_absolute_error(y_tr, np.expm1(y_tr_pred)))
                fold_val_scores.append(mean_absolute_error(y_val, np.expm1(y_val_pred)))

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

    def train(self, X_train, y_train):
        print(X_train)

        X_train = self.preprocessor.fit_transform(X_train)
        y_train = y_train.values.reshape(-1, 1)

        feature_names = self.get_feature_names()
        print(feature_names)
        print(len(X_train[0]))

        y_transformed = np.log1p(y_train)

        model = OLS(y_transformed, X_train, name_y='nitrate', name_x=feature_names)
        self._model = model

        self.model_name = type(self._model).__name__
        self._save_model()
        print(f"{self.model_name} was trained and saved.")

    def get_summary(self):
        print(self._model.summary)

    def predict_pollutant(self, X_test, y_test):
        X_test = self.preprocessor.transform(X_test)
        
        beta = self._model.betas.flatten()
        X_test_with_const = np.hstack([np.ones((X_test.shape[0], 1)), X_test])
        y_pred = np.expm1(X_test_with_const @ beta)
        y_pred = np.clip(y_pred, 0, None)

        print(f"Inspect performance:")
        print("Test R2:", r2_score(y_test, y_pred))
        print("Test MAE:", mean_absolute_error(y_test, y_pred))
        print("Test RMSE:", sqrt(mean_squared_error(y_test, y_pred)))

        return y_pred


if __name__ == "__main__":
    pass