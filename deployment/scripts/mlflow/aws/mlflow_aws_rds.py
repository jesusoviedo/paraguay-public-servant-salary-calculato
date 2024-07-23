import time
import argparse
import boto3
import botocore.exceptions
import os
from dotenv import load_dotenv

TASK1 = 'create'
TASK2 = 'start'
TASK3 = 'stop'
TASK4 = 'delete'
ec2 = None
rds = None


def parse_arg():
    parser = argparse.ArgumentParser(description='Task for RDS/AWS')
    parser.add_argument('task', choices=[TASK1, TASK2 , TASK3, TASK4], help='Choose theTask')

    return parser.parse_args()


def write_to_env(key, value):
    env_file = '.env'
    with open(env_file, 'a') as f:
        f.write(f"{key}={value}\n")


def create_rds(db_name, db_user, db_password, db_instance_identifier, vpc_security_group_name):
    try:
        response = ec2.describe_security_groups(Filters=[
            {'Name': 'group-name', 'Values': [vpc_security_group_name]}
        ])
        default_security_group_id = response['SecurityGroups'][0]['GroupId']
    except (botocore.exceptions.ClientError, IndexError) as error:
        print(f"Error finding security group: {error}")
        return
    
    try:
        response = rds.create_db_instance(
            DBName=db_name,
            DBInstanceIdentifier=db_instance_identifier,
            AllocatedStorage=20,
            DBInstanceClass='db.t3.micro',
            Engine='postgres',
            MasterUsername=db_user,
            MasterUserPassword=db_password,
            VpcSecurityGroupIds=[default_security_group_id],
            PubliclyAccessible=False,
            StorageType='gp2',
        )
        print(f"Database {db_name} creating...")

        db_instance_identifier = response['DBInstance']['DBInstanceIdentifier']
        waiter = rds.get_waiter('db_instance_available')
        waiter.wait(DBInstanceIdentifier=db_instance_identifier)
        print(f"Database {db_name} created and available.")
        
        endpoint = rds.describe_db_instances(DBInstanceIdentifier=db_instance_identifier)['DBInstances'][0]['Endpoint']['Address']
        port = rds.describe_db_instances(DBInstanceIdentifier=db_instance_identifier)['DBInstances'][0]['Endpoint']['Port']
        
        return endpoint, port

    except (botocore.exceptions.ClientError, IndexError) as error:
        print(f"Error created Database: {error}")
        return


def add_rule(vpc_security_group_name, ec2_security_group_name):
    try:
        response = ec2.describe_security_groups(Filters=[
            {'Name': 'group-name', 'Values': [vpc_security_group_name]}
        ])
        vpc_security_group_id = response['SecurityGroups'][0]['GroupId']
    
        response = ec2.describe_security_groups(Filters=[
            {'Name': 'group-name', 'Values': [ec2_security_group_name]}
        ])
        ec2_security_group_id = response['SecurityGroups'][0]['GroupId']
    except (botocore.exceptions.ClientError, IndexError) as error:
        print(f"Error finding security group: {error}")
        return

    try:
        ec2.authorize_security_group_ingress(
            GroupId=vpc_security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 5432,
                    'ToPort': 5432,
                    'UserIdGroupPairs': [{
                        'GroupId': ec2_security_group_id
                    }]
                }
            ]
        )
        print("Inbound rule added successfully.")
    except Exception as e:
        print(f"Error adding inbound rule: {e}")


def delete_rds_instance(db_instance_identifier):
    try:
        rds.delete_db_instance(
            DBInstanceIdentifier=db_instance_identifier,
            SkipFinalSnapshot=True
        )
        print(f"RDS instance {db_instance_identifier} successfully deleted.")
    except Exception as e:
        print(f"Error deleting RDS instance {db_instance_identifier}: {e}")


def revoke_rule(vpc_security_group_name, ec2_security_group_name):
    try:
        response = ec2.describe_security_groups(Filters=[
            {'Name': 'group-name', 'Values': [vpc_security_group_name]}
        ])
        vpc_security_group_id = response['SecurityGroups'][0]['GroupId']
    
        response = ec2.describe_security_groups(Filters=[
            {'Name': 'group-name', 'Values': [ec2_security_group_name]}
        ])
        ec2_security_group_id = response['SecurityGroups'][0]['GroupId']
    except (botocore.exceptions.ClientError, IndexError) as error:
        print(f"Error finding security group: {error}")
        return
    
    try:
        ec2.revoke_security_group_ingress(
            GroupId=vpc_security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 5432,
                    'ToPort': 5432,
                    'UserIdGroupPairs': [{
                        'GroupId': ec2_security_group_id
                    }]
                }
            ]
        )
        
        print(f"Inbound rule revoked from security group {vpc_security_group_id}.")
    except Exception as e:
        print(f"Error revoking inbound rule: {e}")


def start_rds_instance(db_instance_identifier):
    try:
        rds.start_db_instance(DBInstanceIdentifier=db_instance_identifier)
        print(f"Starting RDS instance {db_instance_identifier}...")
        
        waiter = rds.get_waiter('db_instance_available')
        waiter.wait(DBInstanceIdentifier=db_instance_identifier)
        print(f"RDS instance {db_instance_identifier} successfully started.")
    except Exception as e:
        print(f"Error starting RDS instance {db_instance_identifier}: {e}")


def stop_rds_instance(db_instance_identifier):
    try:
        rds.stop_db_instance(DBInstanceIdentifier=db_instance_identifier)
        waiter_stop_rds_instance(rds, db_instance_identifier)
        print(f"The RDS instance {db_instance_identifier} has been stopped.")
    except Exception as e:
        print(f"Error stopping RDS instance {db_instance_identifier}: {e}")


def waiter_stop_rds_instance(rds, db_instance_identifier):
    while True:
        response = rds.describe_db_instances(DBInstanceIdentifier=db_instance_identifier)
        state = response['DBInstances'][0]['DBInstanceStatus']
        if state == 'stopped':
            break
        print(f"Waiting for the instance to stop... Current state: {state}")
        time.sleep(10)


if __name__ == '__main__':
    args = parse_arg()
    task = args.task
    load_dotenv()
    SEGUNDOS = 10

    region_name = os.environ.get('AWS_REGION')
    db_name = os.environ.get('AWS_RDS_DB_NAME')
    db_user = os.environ.get('AWS_RDS_DB_USER') 
    db_password = os.environ.get('AWS_RDS_DB_PASSWORD')
    db_instance_identifier = os.environ.get('AWS_RDS_DB_INSTANCE_IDENTIFIER')
    vpc_security_group_name = os.environ.get('AWS_RDS_VPC_SECURITY_GROUP_NAME') 
    ec2_security_group_name = os.environ.get('AWS_EC2_SECURITY_GROUP_NAME')

    rds = boto3.client('rds', region_name=region_name)
    ec2 = boto3.client('ec2', region_name=region_name)

    if task == TASK1:
        endpoint, port= create_rds(db_name, db_user, db_password, db_instance_identifier, vpc_security_group_name)        
        time.sleep(SEGUNDOS)
        write_to_env("AWS_RDS_DB_ENDPOINT", endpoint)
        write_to_env("AWS_RDS_DB_PORT", port)
        time.sleep(SEGUNDOS)
        add_rule(vpc_security_group_name , ec2_security_group_name)

    if task == TASK2:
        start_rds_instance(db_instance_identifier)
        
    if task == TASK3:
        stop_rds_instance(db_instance_identifier)

    if task == TASK4:
        revoke_rule(vpc_security_group_name , ec2_security_group_name)
        time.sleep(SEGUNDOS)
        delete_rds_instance(db_instance_identifier)
        
        
