# Credenciales de AWS
aws_region                          = "us-east-1"
aws_access_key                      = env("AWS_ACCESS_KEY_ID")
aws_secret_key                      = env("AWS_SECRET_ACCESS_KEY")

# Configuración de la base de datos para MLflow
rds_username_mlflow                 = env("RDS_USERNAME_MLFLOW_DEV")
rds_password_mlflow                 = env("RDS_PASSWORD_MLFLOW_DEV")
rds_db_name_mlflow                  = env("RDS_DB_NAME_MLFLOW_DEV")

# Setting up the database for Mage
rds_username_mage                   = env("RDS_USERNAME_MAGE_DEV")
rds_password_mage                   = env("RDS_PASSWORD_MAGE_DEV")
rds_db_name_mage                    = env("RDS_DB_NAME_MAGE_DEV")

# Setting up S3 bucket for MLflow
s3_bucket_name_mlflow               = env("S3_BUCKET_NAME_MLFLOW_DEV")

# Setting up ECR
ecr_docker_image_flask_local_path   = "./file/flask/Dockerfile"
