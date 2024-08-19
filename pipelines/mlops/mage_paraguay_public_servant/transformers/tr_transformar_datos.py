from typing import Tuple, List

import pandas as pd

from mlops.utils.preparacion_datos.cleaning import clean
from mlops.utils.preparacion_datos.feature_engineering import create_features
from mlops.utils.preparacion_datos.splitters import split_traint_test

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer


@transformer
def transform(
    df: pd.DataFrame, **kwargs
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, List]:
    
    
    target = kwargs.get('target').split()
    features_raw = kwargs.get('features').split(",")
    test_percentage = kwargs.get('test_percentage')
    

    df = clean(df, target=target, features=features_raw)
    df, features = create_features(df, features=features_raw)
    df_train, df_val = split_traint_test(df, test_percentage, target=target, features=features)

    return df, df_train, df_val, features