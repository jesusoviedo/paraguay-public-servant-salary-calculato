

if 'sensor' not in globals():
    from mage_ai.data_preparation.decorators import sensor


@sensor
def check_condition(*args, **kwargs) -> bool:
    """
    Template code for checking if block or pipeline run completed.
    """
