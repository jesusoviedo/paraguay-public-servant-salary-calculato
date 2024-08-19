from typing import Dict, Tuple, Union

from pandas import Series
from pandas import DataFrame
from category_encoders import CatBoostEncoder
from xgboost import Booster

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def source(
    settings: Tuple[
        Dict[str, Union[bool, float, int, str]],
        DataFrame,
        Series,
        CatBoostEncoder
    ],
    training_results: Tuple[Booster, CatBoostEncoder],
    **kwargs
) -> Tuple[Booster, DataFrame, Series]:


    model, _ = training_results
    _, X, y, _ = settings

    return model, X, y