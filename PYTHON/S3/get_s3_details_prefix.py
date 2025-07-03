"""
This script is used for getting S3 details of the account by using the AWS role defined in current user aws config.
USAGE:
python get_s3_details_all_roles.py
"""
import csv
import datetime
import configparser
import argparse
import boto3

config = configparser.RawConfigParser()
config.read('/home/soumyaranjan.patra/.aws/credentials')
roles = config.sections()
parser = argparse.ArgumentParser(description="Provide vault details")
parser.add_argument("-p", "--role-prefix", type=str, help="AWS Role Prefix", default="prod")

MAIN_REGION = "ap-south-1"
csv_columns = ['Account Name', 'Bucket Name', 'Bucket Region', 'Creation Date', 'Total Size (GB)',
               'Number of Objects',
               'Owner',
               'Environment',
               'RequestedBy', 'Service', 'Vertical', 'Subvertical', 'LifeCycle Mgmt', 'All Tags']
date = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
end_time = date
start_time = date - datetime.timedelta(days=1)


def get_region_name(region, session):
    client = session.client("ssm")
    response = client.get_parameter(
        Name=f'/aws/service/global-infrastructure/regions/{region}/longName'
    )
    return response['Parameter']['Value']


def get_bucket_tag(name, tag_name, client_session):
    d = {"tag_value": "NA", "all_tags": "NA"}
    tags = []
    try:
        s3_client = client_session.client('s3')
        response = s3_client.get_bucket_tagging(Bucket=name)
        for tag in response['TagSet']:
            tag_key = tag["Key"]
            tag_val = tag["Value"]
            tag_string = f"{tag_key}::{tag_val}"
            tags.append(tag_string)
            if tag_key.lower() == tag_name.lower():
                d["tag_value"] = tag["Value"]
        d["all_tags"] = " | ".join(tags)
    # print(response["TagSet"])
    except Exception as e:
        if "The TagSet does not exist" in str(e):
            d["tag_value"] = "Bucket has No Tags"
        else:
            print(e)
    return d


def get_bucket_size_n_obj(name, session):
    cw_client = session.client('cloudwatch')
    d = {"size": "NA", "obj_count": "NA"}
    response_size = cw_client.get_metric_statistics(
        Namespace='AWS/S3',
        MetricName='BucketSizeBytes',
        Dimensions=[
            {'Name': 'BucketName', 'Value': name},
            {'Name': 'StorageType', 'Value': 'StandardStorage'}
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=86400,
        Statistics=['Average']
    )

    total_size = response_size['Datapoints'][0]['Average'] if response_size['Datapoints'] else 0
    total_size_gb = total_size / (1024 * 1024 * 1024)
    total_size_gb_float = f"{total_size_gb:.10f}"

    # Get the number of objects
    response_count = cw_client.get_metric_statistics(
        Namespace='AWS/S3',
        MetricName='NumberOfObjects',
        Dimensions=[
            {'Name': 'BucketName', 'Value': name},
            {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=86400,
        Statistics=['Average']
    )
    num_objects = response_count['Datapoints'][0]['Average'] if response_count['Datapoints'] else 0
    d["size"] = total_size_gb_float
    d["obj_count"] = num_objects
    return d


def get_lifecycle_details(name, client_session):
    lifecycle_rules = 'NA'
    s3_client = client_session.client("s3")
    try:
        lifecycle_response = s3_client.get_bucket_lifecycle_configuration(Bucket=name)
        lifecycle_rules = ', '.join([str(rule) for rule in lifecycle_response['Rules']])
    except s3.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
            lifecycle_rules = 'No Lifecycle Rules'
        else:
            raise
    return lifecycle_rules


CSV_FILE = '/tmp/prod_s3_buckets_details.csv'
with open(CSV_FILE, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for role in roles:
        if "prod" in role:
            global_session = boto3.Session(profile_name=role, region_name=MAIN_REGION)
            s3 = global_session.client('s3')
            acct_name = role.rsplit("-", 1)[0]
            print(f"Checking S3 in account {acct_name}")
            buckets = s3.list_buckets()
            for bucket in buckets['Buckets']:
                bucket_name = bucket['Name']
                creation_date = bucket['CreationDate']
                location = s3.get_bucket_location(Bucket=bucket_name)
                bucket_region = location['LocationConstraint'] or 'us-east-1'
                if bucket_region != MAIN_REGION:
                    new_session = boto3.Session(profile_name=role, region_name=bucket_region)
                    s3_session = new_session
                else:
                    s3_session = global_session
                size_details = get_bucket_size_n_obj(bucket_name, s3_session)
                OWNER_TAG = get_bucket_tag(bucket_name, "owner", s3_session)["tag_value"]
                ENV_TAG = get_bucket_tag(bucket_name, "env", s3_session)["tag_value"]
                REQUEST_BY_TAG = get_bucket_tag(bucket_name, "Requestedby",
                                                s3_session)["tag_value"]
                SVC_TAG = get_bucket_tag(bucket_name, "service", s3_session)["tag_value"]
                VERTICAL_TAG = get_bucket_tag(bucket_name, "vertical", s3_session)["tag_value"]
                SUBVERTICAL_TAG = get_bucket_tag(bucket_name, "subvertical",
                                                 s3_session)["tag_value"]
                ALL_TAG = get_bucket_tag(bucket_name, "owner", s3_session)["all_tags"]
                LIFECYCLE_MGMT = get_lifecycle_details(bucket_name, s3_session)
                writer.writerow({
                    'Account Name': acct_name,
                    'Bucket Name': bucket_name,
                    'Bucket Region': get_region_name(bucket_region, global_session),
                    'Creation Date': creation_date,
                    'Total Size (GB)': size_details["size"],
                    'Number of Objects': size_details["obj_count"],
                    'Owner': OWNER_TAG,
                    'Environment': ENV_TAG,
                    'RequestedBy': REQUEST_BY_TAG,
                    'Service': SVC_TAG,
                    'Vertical': VERTICAL_TAG,
                    'Subvertical': SUBVERTICAL_TAG,
                    'LifeCycle Mgmt': LIFECYCLE_MGMT,
                    'All Tags': ALL_TAG
                })
    print(f"Details of S3 buckets have been written to {CSV_FILE}")
