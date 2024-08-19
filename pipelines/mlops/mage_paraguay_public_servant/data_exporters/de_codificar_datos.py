import pandas as pd
from typing import Tuple, List
from category_encoders import CatBoostEncoder
from mlops.utils.preparacion_datos.encoders import codificar_features

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export(
    data: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, List], *args, **kwargs
) -> Tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.Series,
    pd.Series,
    pd.Series,
    CatBoostEncoder
]:
    df, df_train, df_val, features= data
    
    target = kwargs.get('target').split()
    features_categorica = kwargs.get('features_categorica').split(",")

    X = df[features]
    y = df[target[0]]
    

    X_train, y_train, X_val, y_val, cat_boost_encoder = codificar_features(df_train,
                                        features_categorica=features_categorica,
                                        target=target,
                                        features=features,
                                        validation_set=df_val)

    return X, X_train, X_val, y, y_train, y_val, cat_boost_encoder