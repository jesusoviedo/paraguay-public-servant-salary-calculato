from typing import Tuple, Union
import pandas as pd
from mlops.utils.preparacion_datos.cleaning import clean
from mlops.utils.preparacion_datos.feature_engineering import create_features

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer


@transformer
def transform(
    encoder, 
    data_set: Tuple[int, pd.DataFrame, pd.DataFrame], 
    **kwargs) -> Tuple[int, pd.DataFrame, pd.DataFrame]:
        
    _, _, _, _, _, _, cat_boost_encoder = encoder['de_codificar_datos']
    code_result, df_actual_ds, df_last_ds = data_set

    if code_result != 0:

        target = kwargs.get('target').split()
        features_raw = kwargs.get('features').split(",")
        
        df_actual_ds = clean(df_actual_ds, target=target, features=features_raw)
        df_actual_ds, features = create_features(df_actual_ds, features=features_raw)
        df_actual_ds = cat_boost_encoder.transform(df_actual_ds[features])

        if code_result == 2:
            df_last_ds = cat_boost_encoder.transform(df_last_ds[features])

        return code_result, df_actual_ds, df_last_ds
    
    else:

        return code_result, pd.DataFrame(), pd.DataFrame()