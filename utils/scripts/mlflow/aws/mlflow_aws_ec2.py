import os
import time
import argparse

import boto3
import botocore.exceptions
from dotenv import load_dotenv

TASK1 = "create"
TASK2 = "start"
TASK3 = "stop"
TASK4 = "delete"


def parse_arg():
    parser = argparse.ArgumentParser(description="Task for EC2/AWS")
    parser.add_argument(
        "task", choices=[TASK1, TASK2, TASK3, TASK4], help="Choose theTask"
    )

    return parser.parse_args()


def write_to_env(key, value):
    env_file = ".env"
    with open(env_file, "a") as f:
        f.write(f"{key}={value}\n")


def create_ec2_instance(
    key_name,
    security_group_name,
    security_group_description,
    image_id,
    vpc_id,
    instance_name,
):
    ec2.delete_key_pair(KeyName=key_name)
    key_pair = ec2.create_key_pair(KeyName=key_name)
    with open(key_name + ".pem", "w") as file:
        file.write(key_pair["KeyMaterial"])

    response = ec2.create_security_group(
        GroupName=security_group_name,
        Description=security_group_description,
        VpcId=vpc_id,
    )

    security_group_id = response["GroupId"]

    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            },
            {
                "IpProtocol": "tcp",
                "FromPort": 5000,
                "ToPort": 5000,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            },
        ],
    )
    instance_type = "t2.micro"

    response = ec2.run_instances(
        ImageId=image_id,
        InstanceType=instance_type,
        KeyName=key_name,
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=[security_group_id],
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {"Key": "Name", "Value": instance_name},
                ],
            },
        ],
    )

    instance_id = response["Instances"][0]["InstanceId"]
    print(f"Instance EC2 create ID: {instance_id}")

    waiter = ec2.get_waiter("instance_running")
    waiter.wait(InstanceIds=[instance_id])
    response = ec2.describe_instances(InstanceIds=[instance_id])
    public_dns = response["Reservations"][0]["Instances"][0]["PublicDnsName"]

    return public_dns


def stop_instance_by_name(instance_name):
    try:
        response = ec2.describe_instances(
            Filters=[{"Name": "tag:Name", "Values": [instance_name]}]
        )
        reservations = response["Reservations"]
        if not reservations:
            print(f"No instances found with the name '{instance_name}'.")
            return
        instance_id = reservations[0]["Instances"][0]["InstanceId"]
    except botocore.exceptions.ClientError as error:
        print(f"Error finding instance: {error}")
        return

    try:
        response = ec2.stop_instances(InstanceIds=[instance_id])
        print(
            f"Instance '{instance_name}' ({instance_id}) stopped successfully."
        )
        return response
    except botocore.exceptions.ClientError as error:
        print(f"Error stopping instance: {error}")


def start_instance_by_name(instance_name):
    try:
        response = ec2.describe_instances(
            Filters=[{"Name": "tag:Name", "Values": [instance_name]}]
        )
        reservations = response["Reservations"]
        if not reservations:
            print(f"No instances found with the name '{instance_name}'.")
            return
        instance_id = reservations[0]["Instances"][0]["InstanceId"]
    except botocore.exceptions.ClientError as error:
        print(f"Error finding instance: {error}")
        return

    try:
        response = ec2.start_instances(InstanceIds=[instance_id])
        print(
            f"Instance '{instance_name}' ({instance_id}) started successfully."
        )
        return response
    except botocore.exceptions.ClientError as error:
        print(f"Error starting instance: {error}")


def terminate_instance_by_name(instance_name):
    try:
        response = ec2.describe_instances(
            Filters=[{"Name": "tag:Name", "Values": [instance_name]}]
        )
        reservations = response["Reservations"]
        if not reservations:
            print(f"No instances found with the name '{instance_name}'.")
            return
        instance_id = reservations[0]["Instances"][0]["InstanceId"]
    except botocore.exceptions.ClientError as error:
        print(f"Error finding instance: {error}")
        return

    try:
        response = ec2.terminate_instances(InstanceIds=[instance_id])
        print(
            f"Instance '{instance_name}' ({instance_id}) terminated successfully."
        )
        return response
    except botocore.exceptions.ClientError as error:
        print(f"Error terminating instance: {error}")


def delete_security_group_by_name(group_name):
    try:
        response = ec2.describe_security_groups(
            Filters=[{"Name": "group-name", "Values": [group_name]}]
        )
        group_id = response["SecurityGroups"][0]["GroupId"]
    except (botocore.exceptions.ClientError, IndexError) as error:
        print(f"Error finding security group: {error}")
        return

    try:
        response = ec2.delete_security_group(GroupId=group_id)
        print(
            f"Security group '{group_name}' ({group_id}) deleted successfully."
        )
        return response
    except botocore.exceptions.ClientError as error:
        if error.response["Error"]["Code"] == "DependencyViolation":
            print(
                f"Error: Security group '{group_name}' is still in use. Detach it from any resources before deleting."
            )
        else:
            print(f"Error deleting security group: {error}")


if __name__ == "__main__":
    ec2 = None
    args = parse_arg()
    task = args.task
    load_dotenv()
    SEGUNDOS = 10

    region_name = os.environ.get("AWS_REGION")
    key_name = os.environ.get("AWS_EC2_KEY_PAR_NAME")
    security_group_name = os.environ.get("AWS_EC2_SECURITY_GROUP_NAME")
    security_group_description = os.environ.get(
        "AWS_EC2_SECURITY_GROUP_DESCRIPTION"
    )
    image_id = os.environ.get("AWS_EC2_AMI")
    vpc_id = os.environ.get("AWS_EC2_VPC_ID")
    instance_name = os.environ.get("AWS_EC2_INSTANCE_NAME")
    ec2 = boto3.client("ec2", region_name=region_name)

    if task == TASK1:
        terminate_instance_by_name(instance_name)
        time.sleep(SEGUNDOS)
        delete_security_group_by_name(security_group_name)
        time.sleep(SEGUNDOS)
        public_dns = create_ec2_instance(
            key_name,
            security_group_name,
            security_group_description,
            image_id,
            vpc_id,
            instance_name,
        )
        write_to_env("AWS_EC2_DNS_PUBLIC", public_dns)

    if task == TASK2:
        start_instance_by_name(instance_name)

    if task == TASK3:
        stop_instance_by_name(instance_name)

    if task == TASK4:
        terminate_instance_by_name(instance_name)
        time.sleep(SEGUNDOS)
        delete_security_group_by_name(security_group_name)
