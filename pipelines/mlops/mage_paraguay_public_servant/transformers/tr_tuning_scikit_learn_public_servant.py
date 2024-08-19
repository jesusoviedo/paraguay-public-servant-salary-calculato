from typing import Callable, Dict, Tuple, Union

import os
import pandas as pd
from pandas import Series
from pandas import DataFrame
from sklearn.base import BaseEstimator
from category_encoders import CatBoostEncoder

from mlops.utils.modelos.sklearn import load_class, tune_hyperparameters

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer

@transformer
def hyperparameter_tuning(
    training_set: Dict[str, Union[Series, DataFrame]],
    model_class_name: str,
    *args,
    **kwargs
) -> Tuple[
    Dict[str, Union[bool, float, int, str]],
    DataFrame,
    Series,
    Dict[str, Union[Callable[..., BaseEstimator], str]],
    CatBoostEncoder
]:
    X, X_train, X_val, y, y_train, y_val, cat_boost_encoder = training_set['de_codificar_datos']

    model_class = load_class(model_class_name)


    X = pd.concat([X_train, X_val], axis=0)
    y = pd.concat([y_train, y_val], axis=0)
    
    best_hyperparameters = tune_hyperparameters(
        model_class,
        X_train,
        y_train,
        X_val,
        y_val,
        max_evaluations=kwargs.get('max_evaluations')
    )

    return best_hyperparameters, X, y, dict(cls=model_class, name=model_class_name), cat_boost_encoder
