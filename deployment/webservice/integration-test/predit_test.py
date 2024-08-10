import pandas as pd
import mlflow
import sys
import os
import pickle
import argparse
import requests
import json
from pprint import pprint
from mlflow.tracking.client import MlflowClient
from sklearn.model_selection import train_test_split
from category_encoders import CatBoostEncoder
from deepdiff import DeepDiff
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error, mean_squared_error, r2_score


TASK1 = 'init_test_integration'
TASK2 = 'setup_test_integration'
TASK3 = 'predict_test_integration'
FOLDER = "data-util"
FILE_CSV = "funcionario_publico_demo.csv"
FILE_JSON = "data_request.json"
TARGET = "presupuestado"
CATEGORICAL_FEACTURE = ["estado", "categoria", "profesion", "nivel", "entidad", "cargo"]
TEST_PERCENTAGE = 0.25
RANDOM_STATE = 45
TRACKING_URI = os.getenv('EXPERIMENT_TRACKING_URI_TEST_INTEGRATION')
URL_HOST = os.getenv('URL_HOST_PREDICT_TEST_INTEGRATION')
ALIAS = os.getenv('ALIAS_ACTIVE')
TAG = os.getenv('TAG_KEY_REGISTERED_MODEL')
TAG_VALUE = os.getenv('TAG_VALUE_REGISTERED_MODEL_ACTIVE')
MODEL_NAME = os.getenv('REGISTERED_MODEL_NAME') 
ENCODE_NAME = os.getenv('ARTIFACT_ENCODE_NAME')
API_KEY = os.getenv('API_KEY_CODE_1')


def parse_arg():
    parser = argparse.ArgumentParser(description='Test integration script')
    
    parser.add_argument('task', choices=[TASK1, TASK2 , TASK3], help='Choose theTask')
    
    return parser.parse_args()


def read_and_split_data():

    df_data = pd.read_csv(f'{FOLDER}/{FILE_CSV}')

    X_data, y_data = df_data.drop(columns=TARGET), df_data[TARGET]
    X_data[CATEGORICAL_FEACTURE] = X_data[CATEGORICAL_FEACTURE].astype(str)
    
    return train_test_split(X_data, y_data, test_size=TEST_PERCENTAGE, random_state=RANDOM_STATE)


def train_save_encoder(X_train, X_test, y_train, y_test):
    
    cat_boost_encoder = CatBoostEncoder(cols=CATEGORICAL_FEACTURE)
    X_train = cat_boost_encoder.fit_transform(X_train, y_train)
    X_test = cat_boost_encoder.transform(X_test, y_test)

    with open(ENCODE_NAME, "wb") as f:
        pickle.dump(cat_boost_encoder, f)

    return X_train, X_test, ENCODE_NAME


def train_save_model(X_train, X_test, y_train, y_test, encoder_name):
    
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment("test_integration")
    run_id = None
    path = "test_inte"

    with mlflow.start_run() as run:
        params = dict(n_estimators=50, max_depth=10,random_state=RANDOM_STATE)
        random_forest_regressor_model = RandomForestRegressor(**params)
        random_forest_regressor_model.fit(X_train, y_train)

        y_pred = random_forest_regressor_model.predict(X_test)
        rmse = root_mean_squared_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        metrics = dict(rmse=rmse, mse=mse, r2=r2)
              
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        mlflow.log_artifact(encoder_name, artifact_path=path)
        mlflow.sklearn.log_model(random_forest_regressor_model, artifact_path=path)
        run_id = run.info.run_id

    return run_id, path


def registre_model(run_id, path):
    
    client = MlflowClient(tracking_uri=TRACKING_URI)

    model_version = mlflow.register_model("runs:/{}/{}".format(run_id, path), MODEL_NAME)
    client.set_registered_model_alias(name=MODEL_NAME, alias=ALIAS, version=model_version.version)
    client.set_model_version_tag(name=MODEL_NAME, version=model_version.version, key=TAG, value=TAG_VALUE)


def delete_save_encoder():

    if os.path.exists(ENCODE_NAME):
        os.remove(ENCODE_NAME)
        #print(f"File '{ENCODE_NAME}' deleted successfully.")
    else:
        print(f"File '{ENCODE_NAME}' not found.")


def print_ok_task(add_line_blank):
    if add_line_blank:
        print()
    print(f'{__file__.split("/")[-1]} ---->> {sys.argv[1]} <OK>')


def init_mlflow_s3_test_integration():
    
    X_train, X_test, y_train, y_test = read_and_split_data()
    X_train, X_test, encoder_name = train_save_encoder(X_train, X_test, y_train, y_test)
    id, path = train_save_model(X_train, X_test, y_train, y_test, encoder_name)
    registre_model(id, path)
    delete_save_encoder()
    print_ok_task(True)


def validate_diff(expected, actual):

    diff = DeepDiff(expected, actual)

    if diff:
        print('diff ---->>  <ERROR>')
        pprint(diff)
    else:
        print_ok_task(False)

    assert 'type_changes' not in diff
    assert 'values_changed' not in diff


def setup_predict_test_integration():
    url = f'{URL_HOST}/setup'
    actual_response = list()
    expected_response=[{'status_code': 200},
                       {'status_code': 401}, 
                       {'status_code': 401}]


    headers = {'Authorization': API_KEY}
    response = requests.post(url, headers=headers)
    actual_response.append({'status_code': response.status_code})
     

    headers['Authorization'] = 'aFsd4Zsd5_'
    response = requests.post(url, headers=headers)
    actual_response.append({'status_code': response.status_code})


    response = requests.post(url)
    actual_response.append({'status_code': response.status_code})

    validate_diff(expected_response, actual_response)


def run_predict_test_integration():

    url = f'{URL_HOST}/predict'
    actual_response = list()
    expected_response = [(200, 2003931),
                         (200, 5673736),
                         (200, 2855344),
                         (200, 2714520), 
                         (200, 2017661), 
                         (200, 2860512), 
                         (200, 2763412), 
                         (200, 2715607), 
                         (200, 2908317), 
                         (200, 2976702)]

    with open(f'{FOLDER}/{FILE_JSON}', 'r') as archivo_json:
        array_json = json.load(archivo_json)

    for attributes in array_json:
        response = requests.post(url, json=attributes)
        actual_response.append((response.status_code,response.json().get('salary')))

    validate_diff(expected_response, actual_response)


if __name__ == "__main__":
    
    args = parse_arg()
    task = args.task

    if task == TASK1:
        init_mlflow_s3_test_integration()

    if task == TASK2:
        setup_predict_test_integration()
        
    if task == TASK3:
        run_predict_test_integration()