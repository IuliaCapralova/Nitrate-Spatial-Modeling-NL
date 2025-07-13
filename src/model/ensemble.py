import numpy as np


def create_ensemble(all_preds, models_in_ensemble):
    # Build ensemble from only the subset
    ensemble_inputs = [all_preds[name] for name in models_in_ensemble if name in all_preds]
    if not ensemble_inputs:
        raise ValueError(f"No valid models found in models_in_ensemble: {models_in_ensemble}")

    stds = np.array([np.std(pred) for pred in ensemble_inputs])
    inv_stds = 1 / (stds + 1e-8)
    model_weights = inv_stds / inv_stds.sum()
    ensemble_pred = np.average(ensemble_inputs, axis=0, weights=model_weights)
    print("Ensemble weights:", dict(zip(models_in_ensemble, model_weights)))

    return ensemble_pred, model_weights
