import pandas as pd

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader

@data_loader
def ingest_files(**kwargs) -> pd.DataFrame:

    anho = kwargs['anho']
    mes = kwargs['mes']
    
    #descomentar esto para produccion
    #df = pd.read_csv(f'https://datos.sfp.gov.py/data/funcionarios_{anho}_{mes}.csv.zip', compression='zip', encoding='latin-1')


    df = pd.read_csv(f'https://github.com/jesusoviedo/paraguay-public-servant-salary-calculato/raw/main/data/ejemplo_funcionarios_{anho}_{mes}.csv.zip', compression='zip', encoding='latin-1') 
    
    return df