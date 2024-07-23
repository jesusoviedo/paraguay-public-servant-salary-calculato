#!/bin/bash
python mlflow_aws_s3.py create
python mlflow_aws_ec2.py create
python mlflow_aws_rds.py create

source .env

AWS_EC2_KEY_PAR="${AWS_EC2_KEY_PAR_NAME}.pem"
MLFLOW_BACKEND_STORE_URI="postgresql://{AWS_RDS_DB_USER}:{AWS_RDS_DB_PASSWORD}@{AWS_RDS_DB_ENDPOINT}:${AWS_RDS_DB_PORT}/${AWS_RDS_DB_NAME}"
MLFLOW_ARTIFACT_ROOT="s3://${AWS_S3_BUCKET_NAME}"

ssh -i "${AWS_EC2_KEY_PAR}" ec2-user@$AWS_EC2_DNS_PUBLIC <<EOF

echo "Conectado a la instancia EC2. Iniciando servidor MLflow..."
mlflow server \
  -h 0.0.0.0 \
  -p 5000 \
  --backend-store-uri "$MLFLOW_BACKEND_STORE_URI" \
  --default-artifact-root "$MLFLOW_ARTIFACT_ROOT"

EOF