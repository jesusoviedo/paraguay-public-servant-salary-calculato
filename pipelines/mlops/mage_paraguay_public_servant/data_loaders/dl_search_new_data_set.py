import pandas as pd
from datetime import datetime
from mlops.utils.monitoreo.monitoring_util import validate_new_dataset
from typing import Tuple, Union

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader


@data_loader
def load_data(*args, **kwargs) -> Tuple[int, Union[int, pd.DataFrame], Union[int, pd.DataFrame]]:

    now = datetime.now()
    year = now.year
    month = 7 #now.month
    bucket_name = kwargs.get('bucket_name')

    code, df_dataset_actual, df_dataset_last = validate_new_dataset(year, month, bucket_name)

    return code, df_dataset_actual, df_dataset_last
