from typing import List, Tuple
import pandas as pd
from category_encoders import CatBoostEncoder


def codificar_features(
    training_set: pd.DataFrame,
    features_categorica: List,
    target: List = ['presupuestado'],
    features: List = ['estado', 'categoria', 'profesion', 'antiguedad_laboral', 'nivel', 'entidad', 'cargo'],
    validation_set: pd.DataFrame = None
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, CatBoostEncoder]:
    training_set[features_categorica] = training_set[features_categorica].astype(str)
    validation_set[features_categorica] = validation_set[features_categorica].astype(str)
    
    cat_boost_encoder = CatBoostEncoder(cols=features_categorica)
    X_train = cat_boost_encoder.fit_transform(training_set[features], training_set[target[0]])
    y_train = training_set[target[0]]

    X_val = None
    y_val = None
    if validation_set is not None:
        X_val = cat_boost_encoder.transform(validation_set[features])
        y_val = validation_set[target[0]]

    return X_train, y_train, X_val, y_val, cat_boost_encoder



