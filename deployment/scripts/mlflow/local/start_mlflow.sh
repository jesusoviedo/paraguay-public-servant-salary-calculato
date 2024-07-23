#!/bin/bash
mkdir artifacts
mkdir db

mlflow server --backend-store-uri sqlite:///db/mlflow.db --default-artifact-root ./artifacts --host 0.0.0.0 &