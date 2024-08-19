from typing import Tuple, Union
import pandas as pd
from mlops.utils.monitoreo.monitoring_util import generate_report_evidently

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def transform_custom(data_set_encoder: Tuple[int, pd.DataFrame, pd.DataFrame], **kwargs) -> Tuple[bool, bool, int]:

    code, df_actual_ds, df_last_ds = data_set_encoder

    retrain = False
    train = False


    if code == 1:
        train = True

    if code == 2:
        retrain = generate_report_evidently(df_actual_ds, df_last_ds)

    return retrain, train, code