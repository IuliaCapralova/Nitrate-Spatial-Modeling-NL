import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
from abc import ABC, abstractmethod


class ModelBase(ABC):
    def __init__(self, X_train):
        self._model = None

    def train(self, X_train, y_train):
        self._model.fit(X_train, y_train)

    def get_history(self):
        pass

    def predict(self):
        pass

    def display_metrics(self):
        pass

    def display_predictions(self):
        pass

    def plot_history(self):
        pass

    @abstractmethod
    def _create_model(self):
        pass


if __name__ == "__main__":
    pass
