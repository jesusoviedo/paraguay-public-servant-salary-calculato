# Outputs
data "aws_caller_identity" "current" {}

output "aws_account_id" {
  value = data.aws_caller_identity.current.account_id
}

output "mlflow_db_endpoint" {
  value = aws_db_instance.mlflow_rds.address
}

output "mage_ai_db_endpoint" {
  value = aws_db_instance.mage_ai_rds.address
}

output "name_bucket_s3" {
  value = aws_s3_bucket.mlflow_artifacts.bucket
}

output "flask_image_uri" {
  value = "${aws_ecr_repository.rj92_aws_docker_repository.repository_url}:${data.aws_ecr_image.flask_image.image_tag}"
}
