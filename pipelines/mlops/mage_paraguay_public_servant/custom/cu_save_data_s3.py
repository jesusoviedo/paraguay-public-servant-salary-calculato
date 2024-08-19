import pandas as pd
import boto3
import os
import io
from typing import Tuple
from category_encoders import CatBoostEncoder

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom

@custom
def transform_custom(data_set: Tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.Series,
    pd.Series,
    pd.Series,
    CatBoostEncoder],
    **kwargs
):

    X, _, _, y, _, _, _ = data_set
    AWS_REGION = os.getenv('AWS_REGION')
    AWS_ENPOINT_LOCAL = os.getenv('AWS_ENPOINT_LOCAL')

    s3 = None

    if AWS_ENPOINT_LOCAL:
        s3 = boto3.client('s3', region_name=AWS_REGION, endpoint_url=AWS_ENPOINT_LOCAL)
    else:
        s3 = boto3.client('s3', region_name=AWS_REGION)

    with io.BytesIO() as buffer:
        X.to_parquet(buffer, index=False, engine='pyarrow')  
        buffer.seek(0) 
        s3.put_object(
            Bucket='data-clean-trams',
            Key=f"funcionario_publico_{kwargs.get('anho')}_{kwargs.get('mes')}.parquet",
            Body=buffer 
        )

    return True


