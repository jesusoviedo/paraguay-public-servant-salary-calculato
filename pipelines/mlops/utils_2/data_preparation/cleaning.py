import pandas as pd
from datetime import date
from typing import List

def clean(
    df: pd.DataFrame,
    target: str = 'presupuestado',
    features: List = ['estado', 'categoria', 'profesion', 'antiguedad_laboral', 'nivel', 'entidad', 'cargo', 'anho_ingreso']
) -> pd.DataFrame:
    anho_actual = date.today().year  
    df.drop_duplicates(inplace=True)

    list_var_del = [var for var in df.columns.tolist() if var not in features]
    df.drop(columns=list_var_del, axis=1, inplace=True)

    df = df[(df[target] > 0) & (df['anho_ingreso'] > 0) & (df['anho_ingreso'] <= anho_actual)]

    return df
