import pandas as pd
from datetime import date
from typing import List

def clean(
    df: pd.DataFrame,
    target: List = ['presupuestado'],
    features: List = ['estado', 'categoria', 'profesion', 'antiguedad_laboral', 'nivel', 'entidad', 'cargo', 'anho_ingreso']
) -> pd.DataFrame:
    
    print(f'clean data...')
    anho = 'anho_ingreso'
    df.drop_duplicates(inplace=True)
    
    list_features_target = features + target
    list_var_del = [var for var in df.columns.tolist() if var not in list_features_target]
    
    df.drop(columns=list_var_del, inplace=True)
    df = df[df[target[0]] > 0]
    
    if anho in df.columns.tolist():
        anho_actual = date.today().year  
        df = df[(df[anho] > 0) & (df[anho] <= anho_actual)]
    print(f'cleaning data successfully...')
    
    return df
