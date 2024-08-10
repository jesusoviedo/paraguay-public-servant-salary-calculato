import pytest
import pickle
import json
import random
import os
import tempfile
import pandas as pd
import numpy as np
from datetime import datetime
from marshmallow import ValidationError
from deepdiff import DeepDiff
from predict import _load_artifact, _validate_input, _format_response, _create_folder, _prepare_features, _predict, _download_artifact, _search_path_prefix_and_version, _requiere_api_key
from unittest.mock import MagicMock
from flask import Flask, jsonify


@pytest.fixture
def data_need_test_load_model(mocker):
    
    mocker.patch('predict.FILE_MODEL_NAME', 'model.pkl')
    mocker.patch('predict.FILE_ENCODE_NAME', 'catboost_encoder.pkl')

    mock_model_data = {'k1': 'version 1',
                       'k2': 2,
                       'k3': 3.5,
                       'k4': False,
                       'k5': 't'}

    mock_open = mocker.patch('builtins.open',
                             mocker.mock_open(read_data=pickle.dumps(mock_model_data))
                             )

    return mock_model_data, mock_open


@pytest.fixture
def data_need_test_validate_input():
    
    input_valid = {
        "estado": "PERMANENTE",
        "categoria": "A46",
        "profesion": "ABOGADO",
        "antiguedad_laboral": 10,
        "nivel":"22",
        "entidad": "8",
        "cargo": "GOBERNADOR"
    }

    input_invalid = input_valid.copy()
    input_invalid['nivel'] = int(input_invalid['nivel'])

    return input_valid, input_invalid 


@pytest.fixture
def data_need_test_format_response(data_need_test_validate_input, mocker):

    pred = random.randint(2800000, 9750000)
    ver = random.randint(1, 10)
    attri, _ = data_need_test_validate_input

    return pred, ver, attri


@pytest.fixture
def data_need_test_prepare_features(data_need_test_validate_input, mocker):
    
    attri, _ = data_need_test_validate_input
    transform = dict(estado = [len(attri['estado'])],
                     categoria = [len(attri['categoria'])],
                     profesion = [len(attri['profesion'])],
                     antiguedad_laboral = [10 * int(attri['antiguedad_laboral'])],
                     nivel = [100 * int(attri['nivel'])],
                     entidad = [1000 * int(attri['entidad'])],
                     cargo = [len(attri['cargo'])]
                    )
    
    mock_encoder = mocker.MagicMock()
    mock_encoder.transform.return_value = pd.DataFrame(transform)

    return attri, mock_encoder


@pytest.fixture
def data_need_test_predict(data_need_test_prepare_features, mocker):
    
    attri, _ = data_need_test_prepare_features
    
    transform = dict(estado = [len(attri['estado'])],
                     categoria = [len(attri['categoria'])],
                     profesion = [len(attri['profesion'])],
                     antiguedad_laboral = [10 * int(attri['antiguedad_laboral'])],
                     nivel = [100 * int(attri['nivel'])],
                     entidad = [1000 * int(attri['entidad'])],
                     cargo = [len(attri['cargo'])]
                    )

    predi = sum([transform['antiguedad_laboral'][0], int(transform['nivel'][0]), int(transform['entidad'][0])])

    mock_encoder = mocker.MagicMock()
    mock_encoder.predict.return_value = [predi]

    return pd.DataFrame(transform), mock_encoder


@pytest.fixture
def data_need_test_download_artifact_with_data(mocker):
    
    mocker.patch('predict.AWS_ENPOINT_LOCAL', 'http://localhost:4566')
    mocker.patch('predict.FILE_MODEL_NAME', 'model.pkl')
    s3_client_mock = mocker.patch('boto3.client')

    s3_paginator_mock = mocker.MagicMock()
    s3_client_mock.return_value.get_paginator.return_value = s3_paginator_mock
    s3_paginator_mock.paginate.return_value = [
        {'Contents': [
            {'Key': 'test_path/model.pkl'},
            {'Key': 'test_path/catboost_encoder.pkl'},
        ]}
    ]

    def mock_download_file(Bucket, Key, Filename):
        with open(Filename, 'w') as f:
            pass  
    s3_client_mock.return_value.download_file = mock_download_file

    return s3_client_mock


@pytest.fixture
def data_need_test_download_artifact_without_data(mocker):
    
    mocker.patch('predict.AWS_ENPOINT_LOCAL', 'http://localhost:4566')
    s3_client_mock = mocker.patch('boto3.client')

    s3_paginator_mock = mocker.MagicMock()
    s3_client_mock.return_value.get_paginator.return_value = s3_paginator_mock
    s3_paginator_mock.paginate.return_value = []
  
    return s3_client_mock


@pytest.fixture
def data_need_test_search_path_prefix_and_version_found(mocker):

    mlflow_client_mock = mocker.patch("predict.MlflowClient")

    mock_response = MagicMock()
    mock_response.aliases = {"test_alias": "10"}
    mock_response.latest_versions = [MagicMock(
            source='s3://test_bucket/100/0a2f/test_artifa/model',
            version='10',
            tags={'current_stage': 'Production'},
            name='test_model',
            current_stage= 'Production'
        )]
    mock_response.name = 'test_model'

    
    mlflow_client_mock.return_value.search_registered_models.return_value = [mock_response]
    
    return mlflow_client_mock


@pytest.fixture
def data_need_test_search_path_prefix_and_version_not_found(mocker):

    mlflow_client_mock = mocker.patch("predict.MlflowClient")    
    mlflow_client_mock.return_value.search_registered_models.return_value = []
    
    return mlflow_client_mock


@pytest.fixture
def data_need_test_requiere_api_key(mocker):

    mocker.patch('predict.API_KEYS', {'QH1Sa3Dd4p_': 'USER_N'})
    return Flask(__name__)


def test_load_artifact_encoder(data_need_test_load_model):

    mock_model_data, mock_open = data_need_test_load_model
    loaded_model = _load_artifact('encoder')

    assert loaded_model == mock_model_data
    mock_open.assert_called_once_with('./artifacts/catboost_encoder.pkl', 'rb') 


def test_load_artifact_model(data_need_test_load_model):

    mock_model_data, mock_open = data_need_test_load_model
    loaded_model = _load_artifact('model')

    assert loaded_model == mock_model_data
    mock_open.assert_called_once_with('./artifacts/model.pkl', 'rb') 


def test_load_artifact_none(data_need_test_load_model):

    _, mock_open = data_need_test_load_model
    loaded_model = _load_artifact('abc')

    assert loaded_model == None
    mock_open.assert_not_called()


def test_validate_input_valid(data_need_test_validate_input):

    input, _ = data_need_test_validate_input
    attributes = _validate_input(input)

    assert attributes == input


def test_validate_input_invalid(data_need_test_validate_input):
    
    _, input = data_need_test_validate_input
    expected_result = {'nivel': ['Not a valid string.']}
    with pytest.raises(ValidationError) as exc_info:
        attributes =_validate_input(input)

    response = exc_info.value.args[0]
    assert response == expected_result 


def test_format_response(data_need_test_format_response):
    predict, version, attributes = data_need_test_format_response
    expected_result = dict(salary=predict,
                                  input=attributes,
                                  version=version,
                                  date=datetime.now().strftime('%y/%m/%d %H:%M:%S')
                                  )
    expected_result = json.dumps(expected_result)
    
    result = _format_response(predict, version, attributes)
    assert not DeepDiff(result, expected_result, ignore_order=True)


def test_create_folder(mocker):
    
    FOLDER_ARTIFACT = 'tmp_artifacts'
    mocker.patch('predict.FOLDER_ARTIFACT', FOLDER_ARTIFACT)
    expected_result = 2
    original_cwd = os.getcwd()

    with tempfile.TemporaryDirectory(dir='./', prefix='test_create_folder_') as temp_dir:
        os.chdir(temp_dir)

        assert not os.path.exists(FOLDER_ARTIFACT)
        result = _create_folder()
        assert os.path.exists(FOLDER_ARTIFACT)

    os.chdir(original_cwd)
    assert result == expected_result


def test_create_folder_overwrite(mocker):

    FOLDER_ARTIFACT = 'tmp_artifacts_overwrite'
    mocker.patch('predict.FOLDER_ARTIFACT', FOLDER_ARTIFACT)
    expected_result = 3
    original_cwd = os.getcwd()

    with tempfile.TemporaryDirectory(dir='./', prefix='test_create_folder_overwrite_') as temp_overwrite:
        os.chdir(temp_overwrite)

        os.mkdir(FOLDER_ARTIFACT)
        with open(os.path.join(FOLDER_ARTIFACT, 'same_file.txt'), 'w') as f:
            f.write('same text')
        result = _create_folder(overwrite=True)
        assert os.path.exists(FOLDER_ARTIFACT)
        assert len(os.listdir(FOLDER_ARTIFACT)) == 0

    os.chdir(original_cwd)
    assert result == expected_result


def test_prepare_features(mocker, data_need_test_prepare_features):

    attributes, mock_encoder  = data_need_test_prepare_features
    list_expected_result = [len(attributes['estado']),
                            len(attributes['categoria']),
                            len(attributes['profesion']),
                            10 * int(attributes['antiguedad_laboral']),
                            100 * int(attributes['nivel']),
                            1000 * int(attributes['entidad']),
                            len(attributes['cargo'])
                        ]
    expected_result = np.array([list_expected_result])

    mocker.patch('predict._load_artifact', return_value=mock_encoder)
    result = _prepare_features(attributes)
    result = result.values

    mock_encoder.transform.assert_called_once()
    assert not DeepDiff(result, expected_result)


def test_predict(mocker, data_need_test_predict):

    features, mock_model  = data_need_test_predict
    expected_result = int(np.sum(features[['antiguedad_laboral', 'nivel', 'entidad']].values))

    mocker.patch('predict._load_artifact', return_value=mock_model)
    result = _predict(features)

    mock_model.predict.assert_called_once_with(features)
    assert not DeepDiff(result, expected_result)


def test_download_artifact_with_data(data_need_test_download_artifact_with_data, mocker):

    FOLDER_ARTIFACT = 'tmp_download_artifact'
    BUCKET_NAME = 'tmp_name'
    mocker.patch('predict.FOLDER_ARTIFACT', FOLDER_ARTIFACT)
    mocker.patch('predict.BUCKET_NAME', BUCKET_NAME)
    s3_mock = data_need_test_download_artifact_with_data
    original_cwd = os.getcwd()

    with tempfile.TemporaryDirectory(dir='./', prefix='test_download_artifact_') as temp_download:
        os.chdir(temp_download)
        os.mkdir(FOLDER_ARTIFACT)
        test_folder_download = f"./{FOLDER_ARTIFACT}"

        _download_artifact("test_path")

        s3_mock.return_value.get_paginator.assert_called_once_with('list_objects_v2')
        assert os.path.exists(f"{test_folder_download}/model.pkl")
        assert os.path.exists(f"{test_folder_download}/catboost_encoder.pkl")
    
    os.chdir(original_cwd)


def test_download_artifact_without_dat(data_need_test_download_artifact_without_data, mocker):

    FOLDER_ARTIFACT = 'tmp_download_artifact'
    BUCKET_NAME = 'tmp_name'
    mocker.patch('predict.FOLDER_ARTIFACT', FOLDER_ARTIFACT)
    mocker.patch('predict.BUCKET_NAME', BUCKET_NAME)
    s3_mock = data_need_test_download_artifact_without_data
    original_cwd = os.getcwd()

    with tempfile.TemporaryDirectory(dir='./', prefix='test_download_artifact_') as temp_download:
        os.chdir(temp_download)
        os.mkdir(FOLDER_ARTIFACT)
        test_folder_download = f"./{FOLDER_ARTIFACT}"

        _download_artifact("test_path")

        s3_mock.return_value.get_paginator.assert_called_once_with('list_objects_v2')
        assert not os.path.exists(f"{test_folder_download}/model.pkl")
        assert not os.path.exists(f"{test_folder_download}/catboost_encoder.pkl")
    
    os.chdir(original_cwd)


def test_search_path_prefix_and_version_found(data_need_test_search_path_prefix_and_version_found, mocker):

    mocker.patch('predict.TRACKING_URI', 'http://localhost:5000')
    mocker.patch('predict.MODEL_NAME', 'test_model')
    mocker.patch('predict.ALIAS', 'test_alias')
    mocker.patch('predict.BUCKET_NAME', 'test_bucket')
    mlflow_client_mock = data_need_test_search_path_prefix_and_version_found
    expected_resut = "100/0a2f/test_artifa/model"
    
    result = _search_path_prefix_and_version()

    mlflow_client_mock.return_value.search_registered_models.assert_called()
    assert mlflow_client_mock.return_value.search_registered_models.call_count == 2
    assert not DeepDiff(result, expected_resut)


def test_search_path_prefix_and_version_not_found(data_need_test_search_path_prefix_and_version_not_found, mocker):

    mocker.patch('predict.TRACKING_URI', 'http://localhost:5000')
    mocker.patch('predict.MODEL_NAME', 'test_model')
    mocker.patch('predict.ALIAS', 'test_alias')
    mocker.patch('predict.BUCKET_NAME', 'test_bucket')
    mlflow_client_mock = data_need_test_search_path_prefix_and_version_not_found
    expected_resut = None
    
    result = _search_path_prefix_and_version()

    mlflow_client_mock.return_value.search_registered_models.assert_called()
    assert mlflow_client_mock.return_value.search_registered_models.call_count == 1
    assert not DeepDiff(result, expected_resut)


def test_requiere_api_key_valid(data_need_test_requiere_api_key):

    app = data_need_test_requiere_api_key

    @ _requiere_api_key
    def func_dummy_return(user):
        return jsonify({'result': user})

    with app.test_request_context(headers={'Authorization': 'QH1Sa3Dd4p_'}): 
        response = func_dummy_return('rjo92')

    assert response.status_code == 200
    assert response.get_json() == {'result': 'rjo92'}
        

def test_requiere_api_key_not_valid(data_need_test_requiere_api_key):
    
    app = data_need_test_requiere_api_key

    @ _requiere_api_key
    def func_dummy_return(user):
        return jsonify({'result': user})

    with app.test_request_context(headers={'Authorization': 'QHS3d4p_'}): 
        response = func_dummy_return('rjo92')

    assert response[1] == 401
    assert response[0].json == {'error': 'Invalid or missing API key'}


def test_requiere_api_key_not_found(data_need_test_requiere_api_key): 
    
    app = data_need_test_requiere_api_key

    @ _requiere_api_key
    def func_dummy_return(user):
        return jsonify({'result': user})

    with app.test_request_context(): 
        response = func_dummy_return('rjo92')

    assert response[1] == 401
    assert response[0].json == {'error': 'Invalid or missing API key'}