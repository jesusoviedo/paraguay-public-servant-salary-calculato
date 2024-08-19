import os
from typing import Dict, Optional, Tuple, Union
from datetime import date
from category_encoders import CatBoostEncoder
import pickle
from mlflow import MlflowClient
import mlflow

def setup_experiment() -> Tuple[str, str]:
    return os.getenv('EXPERIMENT_TRACKING_URI'), os.getenv('EXPERIMENT_NAME') 


def return_tag(add_tag_best: Optional[bool]=False,
               name_model: Optional[str]=None,
               developer: Optional[str]=None
    ) -> Dict[str, Union[bool, float, int, str]]:
    
    date_now = date.today()
    dict_tag = dict(developer = (developer or os.getenv('EXPERIMENTS_DEVELOPER')), 
                        date = f"{date_now.year}_{date_now.month}_{date_now.day}")
    if add_tag_best:
        dict_tag["best_model"] = f"best_model_{name_model}"

    return dict_tag


def save_encoder(encoder: CatBoostEncoder) -> str:
    name = "catboost_encoder.pkl"
    with open(name, "wb") as f:
        pickle.dump(encoder, f)

    return name


def search_best_experiment_model() -> Tuple[str, dict]:

    client = MlflowClient(tracking_uri=os.getenv('EXPERIMENT_TRACKING_URI'))
    experiment = client.get_experiment_by_name(os.getenv('EXPERIMENT_NAME') )

    runs = client.search_runs(experiment_ids=[experiment.experiment_id])
    best_run = min(runs, key=lambda run: run.data.metrics.get("rmse"))
    sorted_runs = sorted(runs, key=lambda run: (run.data.metrics.get("rmse"), -run.data.metrics.get("r2")))
    best_run = sorted_runs[0]

    print("Best run:", best_run.info.run_id)
    print("Metrics :", best_run.data.metrics)
    return best_run.info.run_id, best_run.data.metrics


def search_registered_model() -> Union[str, None]:
    
    mlflow.set_tracking_uri(os.getenv('EXPERIMENT_TRACKING_URI'))
    filter_string = f"name='{os.getenv('REGISTERED_MODEL_NAME')}'"
    results = mlflow.search_registered_models(filter_string=filter_string)

    for model in results:
        latest_version = model.latest_versions[0]
        if os.getenv('TAG_KEY_REGISTERED_MODEL') in latest_version.tags and latest_version.tags[os.getenv('TAG_KEY_REGISTERED_MODEL')] == os.getenv('TAG_VALUE_REGISTERED_MODEL_ACTIVE'):
            print("Model found")
            print(latest_version.run_id)            
            return latest_version.run_id
    else:
        print("Model not found")
        return None


def registered_model(run_id:str) -> int:

    mlflow.set_tracking_uri(os.getenv('EXPERIMENT_TRACKING_URI'))
    model_uri = f"runs:/{run_id}/model_location" 
    result_register = mlflow.register_model(model_uri=model_uri, name=os.getenv('REGISTERED_MODEL_NAME'))
    result_add = add_alias_and_tag_active()

    print(f"Model registered")   
    return 1


def add_alias_and_tag_active() -> bool:
    
    client = MlflowClient(tracking_uri=os.getenv('EXPERIMENT_TRACKING_URI'))
    latest_versions = client.search_model_versions(f"name='{os.getenv('REGISTERED_MODEL_NAME')}'")

    client.set_registered_model_alias(name=os.getenv('REGISTERED_MODEL_NAME'), 
                                      alias=os.getenv('ALIAS_ACTIVE'), 
                                      version=latest_versions[0].version
                                      )
    
    client.set_model_version_tag(
        name=os.getenv('REGISTERED_MODEL_NAME'),
        version=latest_versions[0].version,
        key=os.getenv('TAG_KEY_REGISTERED_MODEL'),
        value=os.getenv('TAG_VALUE_REGISTERED_MODEL_ACTIVE'),
    )

    print("add alias and tag new run id")
    return True


def change_alias_and_tag_to_deactive() -> int:
    
    client = MlflowClient(tracking_uri=os.getenv('EXPERIMENT_TRACKING_URI'))
    latest_versions = client.search_model_versions(f"name='{os.getenv('REGISTERED_MODEL_NAME')}'")

    client.set_registered_model_alias(name=os.getenv('REGISTERED_MODEL_NAME'), 
                                      alias=os.getenv('ALIAS_DESACTIVE'), 
                                      version=latest_versions[1].version
                                      )
    client.set_model_version_tag(
        name=os.getenv('REGISTERED_MODEL_NAME'),
        version=latest_versions[1].version,
        key=os.getenv('TAG_KEY_REGISTERED_MODEL') ,
        value=os.getenv('TAG_VALUE_REGISTERED_MODEL_DESACTIVE'),
    )

    print("change alias and tag old run id")
    return 1


def get_metrics(run_id: str)-> dict:

    mlflow.set_tracking_uri(os.getenv('EXPERIMENT_TRACKING_URI'))    
    experiment_id = mlflow.get_experiment_by_name(os.getenv('EXPERIMENT_NAME')).experiment_id
    filter = f"run_id = '{run_id}'"
    runs = mlflow.search_runs(experiment_ids=[experiment_id], filter_string=filter)

    return dict(rmse=runs["metrics.rmse"].values[0], r2=runs["metrics.r2"].values[0])


def compare_model(new_run_id, old_run_id) -> bool:

    metrics_new = get_metrics(new_run_id)
    metrics_old = get_metrics(old_run_id)

    if new_run_id == old_run_id:
        return False

    if  metrics_new.get("rmse") < metrics_old.get("rmse"):
        return True

    if metrics_new.get("rmse") > metrics_old.get("rmse"):
        return False
    
    if metrics_new.get("rmse") == metrics_old.get("rmse"):
        if round(metrics_new.get("r2"), 4)  > round(metrics_old.get("r2"), 4):
            print(metrics_new.get("rmse"), metrics_old.get("rmse"))
            print(round(metrics_new.get("r2"), 4) , round(metrics_old.get("r2"), 4))
            return True
        else:
            return False


def model_registration_flow(new_run_id) -> int:
    
    old_run_id = search_registered_model()

    if old_run_id:
        if compare_model(new_run_id, old_run_id):
            result = registered_model(new_run_id)
            result += change_alias_and_tag_to_deactive()
            return result
        else:
            return 0
    else:
        return registered_model(new_run_id)
