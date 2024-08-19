#!/usr/bin/env bash

export PROJECT_NAME=mlops
export MAGE_CODE_PATH=/home/src
export SMTP_EMAIL=abc
export SMTP_PASSWORD=abc

if ! docker images -q mlflow-aws-rj92 | grep -q .; then
  docker build -t mlflow-aws-rj92 -f Dockerfile.mlflow .
  sleep 4
fi

if ! docker images -q magic-rj92 | grep -q .; then
  docker build -t magic-rj92 -f Dockerfile.magic .
  sleep 4
fi
 
docker compose up -d
sleep 4


if docker ps --filter "ancestor=pgvector/pgvector:0.6.0-pg16" | grep -q .; then
    echo "Image pgvector/pgvector:0.6.0-pg16 running"
fi

if docker ps --filter "ancestor=magic-rj92" | grep -q .; then
    echo "Image magic-rj92 running"
fi

if docker ps --filter "ancestor=mlflow-aws-rj92" | grep -q .; then
    echo "Image mlflow-aws-rj92 running"
fi

if docker ps --filter "ancestor=minio/minio" | grep -q .; then
    echo "Image minio/minio running"
fi

if docker ps --filter "ancestor=localstack/localstack-pro" | grep -q .; then
    echo "Image localstack/localstack-pro running"
    sleep 4
    
    endpoint_url="http://localhost:4566"
    bucket_name="mlflow-bucket"

    if aws --endpoint-url=$endpoint_url s3api head-bucket --bucket $bucket_name >/dev/null 2>&1; then
        echo "Bucket '$bucket_name' exist"
    else
        echo "Bucket '$bucket_name' does not exist, creating it..."
        if aws --endpoint-url=$endpoint_url s3 mb s3://$bucket_name; then
            echo "Bucket '$bucket_name' created successfully"
        else
            echo "Error creating bucket '$bucket_name'." >&2
            exit 1
        fi
    fi

    bucket_name="data-clean-trams"

    if aws --endpoint-url=$endpoint_url s3api head-bucket --bucket $bucket_name >/dev/null 2>&1; then
        echo "Bucket '$bucket_name' exist"
    else
        echo "Bucket '$bucket_name' does not exist, creating it..."
        if aws --endpoint-url=$endpoint_url s3 mb s3://$bucket_name; then
            echo "Bucket '$bucket_name' created successfully"
        else
            echo "Error creating bucket '$bucket_name'." >&2
            exit 1
        fi
    fi

fi