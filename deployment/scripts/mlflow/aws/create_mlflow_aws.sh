#!/bin/bash
python mlflow_aws_s3.py create
python mlflow_aws_ec2.py create
python mlflow_aws_rds.py create

source .env

AWS_EC2_KEY_PAR="${AWS_EC2_KEY_PAR_NAME}.pem"
MLFLOW_BACKEND_STORE_URI="postgresql://{AWS_RDS_DB_USER}:{AWS_RDS_DB_PASSWORD}@{AWS_RDS_DB_ENDPOINT}:${AWS_RDS_DB_PORT}/${AWS_RDS_DB_NAME}"
MLFLOW_ARTIFACT_ROOT="s3://${AWS_S3_BUCKET_NAME}"

# SSH
ssh -i "${AWS_EC2_KEY_PAR}" ec2-user@$AWS_EC2_DNS_PUBLIC <<EOF

# Commands to execute on the EC2 instance
echo "Connected to the EC2 instance. Starting MLflow server..."

sudo yum update
sudo yum install python-pip -y
pip3 install mlflow boto3 psycopg2-binary
export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
export AWS_REGION=$AWS_REGION
aws s3 ls

mlflow server \
  -h 0.0.0.0 \
  -p 5000 \
  --backend-store-uri "$MLFLOW_BACKEND_STORE_URI" \
  --default-artifact-root "$MLFLOW_ARTIFACT_ROOT"

EOF