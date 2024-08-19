from typing import Dict, Tuple, Union

from pandas import Series
from pandas import DataFrame
from category_encoders import CatBoostEncoder
from xgboost import Booster

from mlops.utils.modelos.xgboost import build_data, fit_model

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def train(
    settings: Tuple[
        Dict[str, Union[bool, float, int, str]],
        DataFrame,
        Series,
        CatBoostEncoder
    ],
    **kwargs,
) -> Tuple[Booster, CatBoostEncoder]:
    
    hyperparameters, X, y, cat_boost_encoder = settings

    if kwargs.get('max_depth'):
        hyperparameters['max_depth'] = int(kwargs.get('max_depth'))

    model = fit_model(
        build_data(X, y),
        hyperparameters,
        verbose_eval=kwargs.get('verbose_eval', 100),
        early_stopping_rounds=kwargs.get('early_stopping_rounds', 25),
        encoder=cat_boost_encoder
    )

    return model, cat_boost_encoder