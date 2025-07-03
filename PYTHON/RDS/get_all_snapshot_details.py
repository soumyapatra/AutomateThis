import configparser
import os

import boto3
import csv

config = configparser.RawConfigParser()
home_dir = os.path.expanduser('~')
config.read(f'{home_dir}/.aws/credentials')
roles = config.sections()
REGION = ["ap-south-1", "ap-south-2"]


def check_rds_snapshots(role_name, region):
    session = boto3.Session(profile_name=role_name, region_name=region)
    rds_client = session.client('rds')
    acct_name = role_name.rsplit("-", 1)[0]

    snapshots = rds_client.describe_db_snapshots()['DBSnapshots']

    with open('rds_snapshots.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['AccountName', 'SnapshotID', 'Region', 'DBInstanceIdentifier', 'DBInstanceStatus', 'Tags'])

        for snapshot in snapshots:
            db_instance_identifier = snapshot['DBInstanceIdentifier']
            snapshot_id = snapshot['DBSnapshotIdentifier']

            try:
                db_instance = rds_client.describe_db_instances(DBInstanceIdentifier=db_instance_identifier)
                db_instance_status = db_instance['DBInstances'][0]['DBInstanceStatus']
            except rds_client.exceptions.DBInstanceNotFoundFault:
                db_instance_status = 'non-existent'

            tags_response = rds_client.list_tags_for_resource(ResourceName=snapshot['DBSnapshotArn'])
            tags = {tag['Key']: tag['Value'] for tag in tags_response['TagList']}

            writer.writerow([acct_name, snapshot_id, region, db_instance_identifier, db_instance_status, tags])


if __name__ == "__main__":
    with open('rds_snapshots.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['AccountName', 'SnapshotID', 'Region', 'Size', 'DBInstanceIdentifier', 'DBInstanceStatus', 'Tags'])
        for role in roles:
            region = "ap-south-1"
            acct_name = role.rsplit("-", 1)[0]
            print(f"Working on role {role}")
            session = boto3.Session(profile_name=role, region_name="ap-south-1")
            rds_client = session.client('rds')
            snapshots = rds_client.describe_db_snapshots()['DBSnapshots']
            for snapshot in snapshots:
                db_instance_identifier = snapshot['DBInstanceIdentifier']
                snapshot_id = snapshot['DBSnapshotIdentifier']
                allocated_storage = snapshot["AllocatedStorage"]

                try:
                    db_instance = rds_client.describe_db_instances(DBInstanceIdentifier=db_instance_identifier)
                    db_instance_status = db_instance['DBInstances'][0]['DBInstanceStatus']
                except rds_client.exceptions.DBInstanceNotFoundFault:
                    db_instance_status = 'non-existent'

                tags_response = rds_client.list_tags_for_resource(ResourceName=snapshot['DBSnapshotArn'])
                tags = {tag['Key']: tag['Value'] for tag in tags_response['TagList']}

                writer.writerow([acct_name, snapshot_id, region, allocated_storage, db_instance_identifier, db_instance_status, tags])
