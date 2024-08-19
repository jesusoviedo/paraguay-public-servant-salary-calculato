from typing import Tuple
from utils.modelos.logging_utils import search_best_experiment_model

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def transform_custom(*args, **kwargs) -> Tuple[str, dict]:
    
    run, metrics = search_best_experiment_model()
    return run, metrics

