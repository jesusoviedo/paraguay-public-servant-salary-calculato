import pandas as pd

from mlops.utils.preparacion_datos.downlad import download_data_set

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader

@data_loader
def ingest_files(**kwargs) -> pd.DataFrame:

    anho = kwargs['anho']
    mes = kwargs['mes']
    
    df = download_data_set(anho, mes)

    return df