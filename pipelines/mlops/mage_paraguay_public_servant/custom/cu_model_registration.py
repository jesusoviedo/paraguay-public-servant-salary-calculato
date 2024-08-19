from typing import Tuple
from utils.modelos.logging_utils import model_registration_flow

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def transform_custom(best_model: Tuple[str, dict], **kwargs) -> str:

    run_id, _ = best_model
    result = model_registration_flow(run_id)
    
    if result:
        return "new model registration"
    else:
        return "no changes in the record"
        
