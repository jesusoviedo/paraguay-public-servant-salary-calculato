import pandas as pd
from datetime import date
from typing import List, Tuple


def create_features(
        df: pd.DataFrame,
        features: List = ['estado', 'categoria', 'profesion', 'antiguedad_laboral', 'nivel', 'entidad', 'cargo', 'anho_ingreso']
) -> Tuple[pd.DataFrame, List]:
    
    print("creating features...")
    anho_actual = date.today().year    
    column_drop = 'anho_ingreso'

    if column_drop in features:
        df['antiguedad_laboral'] = anho_actual - df[column_drop]
        df.drop(columns=[column_drop], inplace=True)
        features.remove(column_drop)
        df = df[df['antiguedad_laboral'] <= 50]

    print(f'create features successfully...')
    return df, features