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

    return parser.parse_args()


def create_s3_bucket(bucket_name):
    try:
        s3.create_bucket(Bucket=bucket_name)

        access_block_configuration = {
            "BlockPublicAcls": False,
            "IgnorePublicAcls": False,
            "BlockPublicPolicy": False,
            "RestrictPublicBuckets": False,
        }

        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration=access_block_configuration,
        )

        public_read_policy = {
            "Id": "Policy20240722",
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Action": ["s3:GetObject"],
                    "Effect": "Allow",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    "Principal": "*",
                }
            ],
        }

        s3.put_bucket_policy(
            Bucket=bucket_name, Policy=json.dumps(public_read_policy)
        )

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
    load_dotenv()

    region_name = os.environ.get("AWS_REGION")
    bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")

    s3 = boto3.client("s3", region_name=region_name)

    if task == TASK1:
        create_s3_bucket(bucket_name)

    if task == TASK2:
        delete_s3_bucket(bucket_name)
