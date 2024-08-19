from typing import Callable, Dict, Tuple, Union

from pandas import Series
from pandas import DataFrame
from sklearn.base import BaseEstimator
from category_encoders import CatBoostEncoder
from mlops.utils.modelos.sklearn import fit_model

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def train(
    settings: Tuple[
        Dict[str, Union[bool, float, int, str]],
        DataFrame,
        Series,
        Dict[str, Union[Callable[..., BaseEstimator], str]],
        CatBoostEncoder
    ],
    **kwargs
) -> Tuple[BaseEstimator, CatBoostEncoder]:
    
    hyperparameters, X, y, model_info, cat_boost_encoder = settings
    
    model_class = model_info['cls']
    model, metrics, y_pred = fit_model(model_class, X, y, X, y, hyperparameters, cat_boost_encoder)

    return model, cat_boost_encoder