import json
import os
from typing import Dict, Optional, Tuple, Union

import mlflow
import uuid
from datetime import date
import numpy as np
import pandas as pd
import scipy
import xgboost as xgb
from hyperopt import STATUS_OK, Trials, fmin, hp, tpe
from hyperopt.pyll import scope
from sklearn.metrics import root_mean_squared_error, mean_squared_error, r2_score
from xgboost import Booster, DMatrix
from category_encoders import CatBoostEncoder
from mlops.utils.hiperparametros.shared import build_hyperparameters_space
from mlops.utils.modelos.logging_utils import setup_experiment, return_tag, save_encoder

HYPERPARAMETERS_WITH_CHOICE_INDEX = []


def fit_model(
    data_set: np.ndarray,
    hyperparameters: Dict,
    early_stopping_rounds: int,
    encoder: CatBoostEncoder,
    verbose_eval: Union[bool, int] = 10,
) -> Booster:
    
    uri_tracking, experiment_name = setup_experiment()
    mlflow.set_tracking_uri(uri_tracking)
    date_now = date.today()
    mlflow.set_experiment(f'{experiment_name}')

    with mlflow.start_run() as run:
        num_boost_round = int(hyperparameters.pop('num_boost_round'))

        model, metrics, y_pred = train_model(
            data_set,
            data_set,
            early_stopping_rounds=early_stopping_rounds,
            hyperparameters=hyperparameters,
            num_boost_round=num_boost_round,
            verbose_eval=verbose_eval,
        )

        name_file = save_encoder(encoder)
        dict_tag = return_tag(add_tag_best=True, name_model=model.__class__.__name__)
        mlflow.set_tags(dict_tag)
        mlflow.log_params(hyperparameters)
        mlflow.log_param("early_stopping_rounds", early_stopping_rounds)
        mlflow.log_param("num_boost_round", num_boost_round)
        mlflow.log_param("verbose_eval", verbose_eval)
        mlflow.log_param("model", {model.__class__.__name__})
        mlflow.log_metrics(metrics)
        path = "model_location"
        mlflow.log_artifact(name_file, artifact_path=path)
        mlflow.xgboost.log_model(model, artifact_path=path) 

    return model, metrics, y_pred


def build_data(
    X: pd.DataFrame, y: Optional[pd.Series] = None
) -> np.ndarray:

    return DMatrix(X, y)


def train_model(
    training_set: np.ndarray,
    validation_set: np.ndarray,
    early_stopping_rounds: Optional[int] = 50,
    hyperparameters: Dict = {},
    num_boost_round: int = 1000,
    verbose_eval: Union[bool, int] = 10,
) -> Tuple[Booster, Dict[str, float], np.ndarray]:
    
    if 'max_depth' in hyperparameters:
        hyperparameters['max_depth'] = int(hyperparameters['max_depth'])

    model = xgb.train(
        hyperparameters,
        training_set,
        early_stopping_rounds=early_stopping_rounds,
        evals=[(validation_set, 'validation')],
        num_boost_round=num_boost_round,
        verbose_eval=verbose_eval,
    )

    y_pred = model.predict(validation_set)

    y_val = validation_set.get_label()
    rmse = root_mean_squared_error(y_val, y_pred)
    mse = mean_squared_error(y_val, y_pred)
    r2 = r2_score(y_val, y_pred)

    return model, dict(mse=mse, rmse=rmse, r2=-r2), y_pred


def tune_hyperparameters(
    training_set: np.ndarray,
    validation_set: np.ndarray,
    early_stopping_rounds: int,
    max_evaluations: int,
    verbose_eval: int,
    tranking_mlflow: bool = True,
    random_state: int = 42,
    verbosity: int = 1
) -> Dict:
    
    def __objective(
        params: Dict,
        early_stopping_rounds=early_stopping_rounds,
        training_set=training_set,
        validation_set=validation_set,
        verbosity=verbosity,
        tranking_mlflow=tranking_mlflow,
    ) -> Dict[str, Union[float, str]]:

        uri_tracking, _ = setup_experiment()
        mlflow.set_tracking_uri(uri_tracking)
        mlflow.set_experiment(f"{xgb.__name__}")

        metrics = {}
        with mlflow.start_run(nested=True) as run:  
            num_boost_round = int(params.pop('num_boost_round'))

            model, metrics, predictions = train_model(
                training_set,
                validation_set,
                early_stopping_rounds=early_stopping_rounds,
                hyperparameters={**params, **dict(verbosity=verbosity)},
                num_boost_round=num_boost_round,
                verbose_eval=verbose_eval,
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


    space, choices = build_hyperparameters_space(Booster, random_state=random_state)

    best_hyperparameters: Dict = fmin(
        algo=tpe.suggest,
        fn=__objective,
        max_evals=max_evaluations,
        space=space,
        trials=Trials()
    )

    for key in HYPERPARAMETERS_WITH_CHOICE_INDEX:
        if key in best_hyperparameters and key in choices:
            idx = int(best_hyperparameters[key])
            best_hyperparameters[key] = choices[key][idx]

    if 'max_depth' in best_hyperparameters:
        best_hyperparameters['max_depth'] = int(best_hyperparameters['max_depth'])

    return best_hyperparameters


def load_model(model_dir: str, model_filename: str, config_filename: str) -> Booster:
    model_path = os.path.join(model_dir, model_filename)
    model = Booster()
    model.load_model(model_path)

    config_path = os.path.join(model_dir, config_filename)
    with open(config_path, 'r') as file:
        model_config = json.load(file)

    model_config_str = json.dumps(model_config)
    model.load_config(model_config_str)

    return model