import os
import json
import argparse

import boto3
from dotenv import load_dotenv

TASK1 = "create"
TASK2 = "delete"
s3 = None


def parse_arg():
    parser = argparse.ArgumentParser(description="Task for Bucket S3/AWS")
    parser.add_argument("task", choices=[TASK1, TASK2], help="Choose the task")
    parser.add_argument("bucket_name", help="Name of the S3 bucket")

    return parser.parse_args()


def get_iam_user_name():

    sts = boto3.client('sts')
    response = sts.get_caller_identity()
    arn = response['Arn']
    user_name = arn.split('/')[-1]

    return user_name


def create_policy(bucket_name):

    iam = boto3.client('iam')
    policy_name = 'TerraformStateAccessPolicy'
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowTerraformStateModifications",
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket", 
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject"
                ],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}/*" 
                ]
            }
        ]
    }

    try:
        response = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document),
            Description='Allows Terraform to manage state in the S3 bucket'
        )
        policy_arn = response['Policy']['Arn']
        print(f"Policy created successfully. ARN: {policy_arn}")
        return policy_arn

    except iam.exceptions.EntityAlreadyExistsException:

        print(f"Policy '{policy_name}' already exists. Getting ARN...")
        policies = iam.list_policies(Scope='Local') 

        for policy in policies['Policies']:
            if policy['PolicyName'] == policy_name:
                policy_arn = policy['Arn']
                break
        print(f"Existing policy ARN: {policy_arn}")
        return policy_arn

    except Exception as e:
        print(f"Error creating policy: {e}")


def add_policy(bucket_name):

    iam = boto3.client('iam')
    user_name = get_iam_user_name()
    policy = create_policy(bucket_name)
    try:
        
        iam.attach_user_policy(
            UserName = user_name,
            PolicyArn = policy
        )
        print(f"Política adjuntada exitosamente al usuario {user_name}")
    except Exception as e:
        print(f"Error al adjuntar la política: {e}")


def create_s3_bucket(bucket_name):

    try:
        add_policy(bucket_name)
        s3.create_bucket(Bucket=bucket_name)
        print(f"Bucket S3 {bucket_name} create successfully.")
    except Exception as e:
        print(f"Error create bucket {bucket_name}: {e}")


def delete_s3_bucket(bucket_name):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket(bucket_name)

    try:
        bucket.objects.all().delete()
        bucket.delete()
        print(f"Bucket S3 '{bucket_name}' deleted successfully.")

    except Exception as e:
        print(f"Error delete bucket '{bucket_name}': {e}")


if __name__ == "__main__":
    args = parse_arg()
    task = args.task
    bucket_name = args.bucket_name
    load_dotenv()

    region_name = os.environ.get("AWS_REGION")

    s3 = boto3.client("s3", region_name=region_name)

    if task == TASK1:
        create_s3_bucket(bucket_name)

    if task == TASK2:
        delete_s3_bucket(bucket_name)
