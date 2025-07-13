import os
import json
import datetime

class ExperimentLogger:
    def __init__(self, save_path=None):
        self.logs = []
        self.save_path = save_path
        if self.save_path and os.path.exists(self.save_path):
            self.load()  # load existing logs into self.logs

    def log(self, model, data_file, features, hyperparams, outlier_method, train_score, test_score, extra_info=None):
        entry = {
            "model": model,
            "data_file": data_file,
            "features": features,
            "timestamp": datetime.datetime.now().isoformat(),
            "hyperparameters": hyperparams,
            "outlier_method": outlier_method,
            "train_score": train_score,
            "test_score": test_score,
        }
        if extra_info is not None:
            entry.update(extra_info)
        self.logs.append(entry)
        if self.save_path:
            self.save()
        return entry

    def save(self):
        with open(self.save_path, "w") as f:
            json.dump(self.logs, f, indent=2)

    def load(self):
        if self.save_path:
            with open(self.save_path, "r") as f:
                self.logs = json.load(f)

if __name__ == "__main__":
    pass
