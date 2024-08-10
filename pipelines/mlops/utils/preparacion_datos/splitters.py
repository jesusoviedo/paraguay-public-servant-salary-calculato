import pandas as pd
from typing import List, Tuple
from sklearn.model_selection import train_test_split

def split_traint_test(
   df: pd.DataFrame,
   test_percentage: float,
   target: List = ['presupuestado'],
   features: List = ['estado', 'categoria', 'profesion', 'antiguedad_laboral', 'nivel', 'entidad', 'cargo', 'anho_ingreso']
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    
    print("splitting traint/test...")
    X_train, y_train = df[features], df[target]
    X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=test_percentage, random_state=42)

    train_df = pd.concat([X_train, y_train], axis=1)
    test_df = pd.concat([X_test, y_test], axis=1)

    print("split traint/test successfully...")
    return train_df, test_df