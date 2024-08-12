import os
import json
import pickle
import shutil
from datetime import datetime
from collections import OrderedDict

import boto3
import pandas as pd
from flask import Flask, Response, jsonify, request
from marshmallow import Schema, ValidationError, fields
from mlflow.tracking.client import MlflowClient

AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
TRACKING_URI = os.getenv("EXPERIMENT_TRACKING_URI")
MODEL_NAME = os.getenv("REGISTERED_MODEL_NAME")
ALIAS = os.getenv("ALIAS_ACTIVE")
TAG_KEY = os.getenv("TAG_KEY_REGISTERED_MODEL")
TAG_VALUE = os.getenv("TAG_VALUE_REGISTERED_MODEL_ACTIVE")
FOLDER_ARTIFACT = "artifacts"
FILE_MODEL_NAME = os.getenv("ARTIFACT_MODEL_NAME")
FILE_ENCODE_NAME = os.getenv("ARTIFACT_ENCODE_NAME")
AWS_ENPOINT_LOCAL = os.getenv("AWS_ENPOINT_LOCAL")
API_KEYS = {os.getenv("API_KEY_CODE_1"): os.getenv("API_KEY_USER_1")}
type_artifact_opcion = ("model", "encoder")

app = Flask("salary-prediction-fp-py")
app.config["JSON_SORT_KEYS"] = False


class InputSchema(Schema):
    estado = fields.String(required=True)
    categoria = fields.String(required=True)
    profesion = fields.String(required=True)
    antiguedad_laboral = fields.Integer(required=True)
    nivel = fields.String(required=True)
    entidad = fields.String(required=True)
    cargo = fields.String(required=True)


def _validate_input(json_in):
    attributes = InputSchema().load(json_in)

    return attributes


def _search_path_prefix_and_version():

    client = MlflowClient(tracking_uri=TRACKING_URI)
    version_n = filtered_models = artifact_path_prefix = None

    data_registered_models = [
        model.aliases.get(ALIAS)
        for model in client.search_registered_models(f"name='{MODEL_NAME}'")
    ]
    version_n = data_registered_models[0] if data_registered_models else None

    if version_n:
        os.environ["VERSION_PREDICT"] = version_n
        filtered_models = [
            model
            for model in client.search_registered_models(f"name='{MODEL_NAME}'")
            if any(
                version.tags.get(TAG_KEY) == TAG_VALUE
                for version in model.latest_versions
                if version.version == version_n
            )
        ]

    if filtered_models:
        model = filtered_models[0]
        latest_version = model.latest_versions[0]
        artifact_path_prefix = latest_version.source

        if artifact_path_prefix.startswith("s3://"):
            artifact_path_prefix = artifact_path_prefix.split(f"{BUCKET_NAME}/")[1]

    return artifact_path_prefix


def _create_folder(overwrite=False):

    cod_result = 0
    if overwrite and os.path.exists(FOLDER_ARTIFACT):
        shutil.rmtree(FOLDER_ARTIFACT)
        cod_result += 1
        print("Folder artifact delete all successful...")

    if not os.path.exists(FOLDER_ARTIFACT):
        os.mkdir(FOLDER_ARTIFACT)
        cod_result += 2
        print("Folder artifact created successful...")

    return cod_result


def _download_artifact(path_prefix):

    s3 = None

    if AWS_ENPOINT_LOCAL:
        s3 = boto3.client("s3", region_name=AWS_REGION, endpoint_url=AWS_ENPOINT_LOCAL)
    else:
        s3 = boto3.client("s3", region_name=AWS_REGION)

    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=BUCKET_NAME, Prefix=path_prefix)

    for page in pages:
        for obj in page["Contents"]:
            key = obj["Key"]
            filename = key.split("/")[-1]
            local_path = os.path.join(f"./{FOLDER_ARTIFACT}", filename)
            s3.download_file(BUCKET_NAME, key, local_path)
        print("Download successful artifacts...")


def _load_artifact(type_artifact):

    artifact = file = None
    path = f"./{FOLDER_ARTIFACT}"
    if type_artifact == type_artifact_opcion[0]:
        file = os.path.join(path, FILE_MODEL_NAME)
    elif type_artifact == type_artifact_opcion[1]:
        file = os.path.join(path, FILE_ENCODE_NAME)

    if file:
        with open(file, "rb") as f:
            artifact = pickle.load(f)

    return artifact


def _prepare_features(attributes):

    encoder = _load_artifact(type_artifact_opcion[1])
    attributes = {k: [v] for k, v in attributes.items()}
    df_attributes = pd.DataFrame.from_dict(attributes)

    features = encoder.transform(df_attributes)
    print("Applying feature engineering...")
    return features


def _predict(features):

    model = _load_artifact(type_artifact_opcion[0])
    prediccion = model.predict(features)
    print("Predicting the salary...")
    # salary is an integer in paraguay
    return int(prediccion[0])


def _format_response(pred, ver, attri):
    now = datetime.now()

    result = OrderedDict(
        [
            ("salary", pred),
            ("input", attri),
            ("version", ver),
            ("date", now.strftime("%y/%m/%d %H:%M:%S")),
        ]
    )

    return json.dumps(result, sort_keys=False)


def _requiere_api_key(f):
    def decorated(*args, **kwargs):
        api_key = request.headers.get("Authorization")
        if not api_key or api_key not in API_KEYS:
            return jsonify({"error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)

    return decorated


@app.route("/predict", methods=["POST"])
def predict_endpoint():

    try:

        attributes = _validate_input(request.get_json())
        features = _prepare_features(attributes)
        prediccion = _predict(features)
        version = os.environ.get("VERSION_PREDICT")

        result = _format_response(prediccion, version, attributes)
        return Response(result, mimetype="application/json")

    except ValidationError as err:
        return (
            jsonify({"error": "Incorrect data format", "details": err.messages}),
            400,
        )

    except FileNotFoundError as err:
        return jsonify({"error": "Unexpected error", "details": str(err)}), 404
    # pylint: disable=broad-exception-caught
    except Exception as err:
        return jsonify({"error": "Unexpected error", "details": str(err)}), 500


@app.route("/setup", methods=["POST"])
@_requiere_api_key
def setup_model():

    try:

        _create_folder(overwrite=True)
        prefix = _search_path_prefix_and_version()
        _download_artifact(prefix)

        result = {"version_setup": os.environ.get("VERSION_PREDICT")}
        return jsonify(result)
    # pylint: disable=broad-exception-caught
    except Exception as err:
        return jsonify({"error": "Unexpected error", "details": str(err)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9696)
