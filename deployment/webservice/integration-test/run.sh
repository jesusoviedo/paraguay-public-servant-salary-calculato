#!/usr/bin/env bash

set -a  
source ./.env_integration_test 
set +a 


echo "Starting integration test..."
echo 


for image in salary-prediction-fp-py mlflow-aws-rj92
do
  if ! docker images -q $image | grep -q .; then
    docker build -t $image -f ../Dockerfile.$image .
    sleep 4
    echo 
  fi
done


docker compose up -d
echo 
sleep 4


for image in salary-prediction-fp-py mlflow-aws-rj92 localstack/localstack-pro
do
  if docker ps --filter "ancestor=$image" | grep -q .; then
    echo "Image $image runnig"
    sleep 2
  fi
done
echo



if aws --endpoint-url=$AWS_ENPOINT_LOCAL_TEST_INTEGRATION s3api head-bucket --bucket $S3_BUCKET_NAME >/dev/null 2>&1; then
    echo "Bucket '$S3_BUCKET_NAME' exist"
else
    echo "Bucket '$S3_BUCKET_NAME' does not exist, creating it..."
    if aws --endpoint-url=$AWS_ENPOINT_LOCAL_TEST_INTEGRATION s3 mb s3://$S3_BUCKET_NAME; then
        echo "Bucket '$S3_BUCKET_NAME' created successfully"
    else
        echo "Error creating bucket '$S3_BUCKET_NAME'." >&2
        exit 1
    fi
fi
echo 
sleep 4


task=init_test_integration
echo "run python -> $task..."
pipenv run python predit_test.py $task
ERROR_CODE=$?
if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi
echo 


task=setup_test_integration
echo "run python -> $task..."
pipenv run python predit_test.py $task
ERROR_CODE=$?
if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi
echo  


task=predict_test_integration
echo "run python -> $task..."
pipenv run python predit_test.py $task
ERROR_CODE=$?
if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi
echo


echo "Completing integration test"
docker-compose down