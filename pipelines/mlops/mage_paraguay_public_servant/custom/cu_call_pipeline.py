from mlops.utils.monitoreo.monitoring_util import training_flow
from typing import Tuple

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom



@custom
def transform_custom(sensor_retrain:Tuple[bool, bool, int], **kwargs):

    retrain, train, code = sensor_retrain
    now = datetime.now()
    year = now.year
    month = 7 #now.month

    if code == 0:
        return True

    if train or retrain:
        training_flow(year, month, **kwargs)
        return True