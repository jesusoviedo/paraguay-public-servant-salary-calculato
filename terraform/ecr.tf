resource "aws_ecr_repository" "rj92_aws_docker_repository" {
  name = var.ecr_repo_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }

  force_delete = true
}


data aws_ecr_image flask_image {
 depends_on = [
   null_resource.ecr_image
 ]
 repository_name = var.ecr_repo_name
 image_tag       = var.ecr_image_tag
}
