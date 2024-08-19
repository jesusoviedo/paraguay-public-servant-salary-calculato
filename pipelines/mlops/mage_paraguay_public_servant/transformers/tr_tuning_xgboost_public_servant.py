from typing import Dict, Tuple, Union

import os
import pandas as pd
from pandas import Series
from pandas import DataFrame
from category_encoders import CatBoostEncoder

from mlops.utils.modelos.xgboost import build_data, tune_hyperparameters

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer


@transformer
def hyperparameter_tuning(
    training_set: Dict[str, Union[Series, DataFrame, CatBoostEncoder]],
    **kwargs
) -> Tuple[
    Dict[str, Union[bool, float, int, str]],
    DataFrame,
    Series,
    CatBoostEncoder
]:
    X, X_train, X_val, y, y_train, y_val, cat_boost_encoder = training_set['de_codificar_datos']

    training = build_data(X_train, y_train)
    validation = build_data(X_val, y_val)

    best_hyperparameters = tune_hyperparameters(
        training,
        validation,
        early_stopping_rounds = kwargs.get('early_stopping_rounds', 10),
        max_evaluations = kwargs.get('max_evaluations', 50),
        verbose_eval = kwargs.get('verbose_eval', 5)
    )

    X = pd.concat([X_train, X_val], axis=0)
    y = pd.concat([y_train, y_val], axis=0)

    return best_hyperparameters, X, y, cat_boost_encoder