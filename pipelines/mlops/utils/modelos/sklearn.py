from typing import Callable, Dict, Optional, Tuple, Union

import mlflow
import numpy as np
import sklearn
import uuid
from datetime import date
from hyperopt import STATUS_OK, Trials, fmin, hp, tpe
from pandas import Series, DataFrame
from sklearn.base import BaseEstimator
from category_encoders import CatBoostEncoder
from sklearn.metrics import root_mean_squared_error, mean_squared_error, r2_score

from mlops.utils.hiperparametros.shared import build_hyperparameters_space
from mlops.utils.modelos.logging_utils import setup_experiment, return_tag, save_encoder

HYPERPARAMETERS_WITH_CHOICE_INDEX = [
    'fit_intercept',
]


def load_class(module_and_class_name: str) -> BaseEstimator:
    parts = module_and_class_name.split('.')
    cls = sklearn
    for part in parts:
        cls = getattr(cls, part)

    return cls


def train_model(
    model: BaseEstimator,
    X_train: DataFrame,
    y_train: Series,
    X_val: DataFrame,
    y_val: Series,
    fit_params: Optional[Dict] = None,
    **kwargs,
) -> Tuple[BaseEstimator, Optional[Dict], Optional[np.ndarray]]:
    model.fit(X_train, y_train, **(fit_params or {}))
    y_pred = model.predict(X_val)

    rmse = root_mean_squared_error(y_val, y_pred)
    mse = mean_squared_error(y_val, y_pred)
    r2 = r2_score(y_val, y_pred)

    return model, dict(mse=mse, rmse=rmse, r2=-r2), y_pred


def tune_hyperparameters(
    model_class: Callable[..., BaseEstimator],
    X_train: DataFrame,
    y_train: Series,
    X_val: DataFrame,
    y_val: Series,
    tranking_mlflow: bool = True,
    fit_params: Optional[Dict] = None,
    hyperparameters: Optional[Dict] = None,
    verbosity: bool = False,
    max_evaluations: int = 50,
    random_state: int = 42,
) -> Dict:
    
    def __objective(
        params: Dict,
        model_class=model_class,
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        fit_params=fit_params,
        verbosity=verbosity    
    ) -> Dict[str, Union[float, str, int, bool]]:
        
        uri_tracking, _ = setup_experiment()
        mlflow.set_tracking_uri(uri_tracking)
        mlflow.set_experiment(f"{model_class.__name__}")

        metrics = {}
        with mlflow.start_run() as run:
            model, metrics, predictions = train_model(
                model_class(**params),
                X_train,
                y_train,
                X_val=X_val,
                y_val=y_val,
                fit_params=fit_params
            )

            dict_tag = return_tag()
            mlflow.set_tags(dict_tag)
            if verbosity:
                print(f'Logged tag {dict_tag}.')

            mlflow.log_params(params)
            if verbosity:
                print(f'Logged hyperparameter {params}.')

            mlflow.log_metrics(metrics)
            if verbosity:
                print(f'Logged metric {metrics}.')
  
        return dict(loss=metrics['rmse'], status=STATUS_OK)


    space, choices = build_hyperparameters_space(
        model_class,
        random_state=random_state,
        **(hyperparameters or {}),
    )

    best_hyperparameters = fmin(
        fn=__objective,
        space=space,
        algo=tpe.suggest,
        max_evals=max_evaluations,
        trials=Trials()
    )

    for key in HYPERPARAMETERS_WITH_CHOICE_INDEX:
        if key in best_hyperparameters and key in choices:
            idx = int(best_hyperparameters[key])
            best_hyperparameters[key] = choices[key][idx]


    for key in [
        'max_depth',
        'max_iter',
        'min_samples_leaf',
        'min_samples_split',
        'n_estimators'
    ]:
        if key in best_hyperparameters:
            best_hyperparameters[key] = int(best_hyperparameters[key])

    return best_hyperparameters


def fit_model(
        model_class: BaseEstimator,    
        X_train: DataFrame,
        y_train: Series,
        X_val: DataFrame,
        y_val: Series,
        hyperparameters: Dict[str, Union[float, str, bool, int]],
        encoder: CatBoostEncoder
) -> Tuple[BaseEstimator, Optional[Dict], Optional[np.ndarray]]:
    
    uri_tracking, experiment_name = setup_experiment()
    mlflow.set_tracking_uri(uri_tracking)
    date_now = date.today()
    mlflow.set_experiment(f'{experiment_name}')

    with mlflow.start_run() as run:
        model, metrics, y_pred = train_model(
                model_class(**hyperparameters),
                X_train,
                y_train,
                X_val=X_train,
                y_val=y_train
            )
        
        name_file = save_encoder(encoder)
        dict_tag = return_tag(add_tag_best=True, name_model=model.__class__.__name__)
        mlflow.set_tags(dict_tag)
        mlflow.log_params(hyperparameters)
        mlflow.log_param("model", {model.__class__.__name__})
        mlflow.log_metrics(metrics)
        path = "model_location"
        mlflow.log_artifact(name_file, artifact_path=path)
        mlflow.sklearn.log_model(model, artifact_path=path)

    return model, metrics, y_pred
