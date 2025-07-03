import sys
import boto3
import csv
import datetime
import configparser
import argparse
import os

parser = argparse.ArgumentParser(description="Provide vault details")
parser.add_argument("-r", "--role-name", type=str, help="AWS Role", required=True)
args = parser.parse_args()
config = configparser.RawConfigParser()
home_dir = os.path.expanduser('~')
config.read(f'{home_dir}/.aws/credentials')
roles = config.sections()

main_region = "ap-south-1"
csv_columns = ['Account Name', 'Bucket Name', 'Bucket Region', 'Creation Date', 'Total Size (GB)', 'Number of Objects',
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


def get_bucket_tag(bucket_name, tag_name, client_session):
    d = dict()
    d["tag_value"] = "NA"
    d["all_tags"] = "NA"
    tags = []
    try:
        s3_client = client_session.client('s3')
        response = s3_client.get_bucket_tagging(Bucket=bucket_name)
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
            return d
        else:
            print(e)
    return d


def get_bucket_size_n_obj(bucket_name, session):
    cw_client = session.client('cloudwatch')
    d = dict()
    response_size = cw_client.get_metric_statistics(
        Namespace='AWS/S3',
        MetricName='BucketSizeBytes',
        Dimensions=[
            {'Name': 'BucketName', 'Value': bucket_name},
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
            {'Name': 'BucketName', 'Value': bucket_name},
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


def get_lifecycle_details(bucket_name, client_session):
    lifecycle_rules = 'NA'
    s3_client = client_session.client("s3")
    try:
        lifecycle_response = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        lifecycle_rules = ', '.join([str(rule) for rule in lifecycle_response['Rules']])
    except s3.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
            lifecycle_rules = 'No Lifecycle Rules'
        else:
            raise
    return lifecycle_rules


role_arg = args.role_name
role_name = f"{role_arg}-role"
csv_file = f'/tmp/{role_arg}_s3_buckets_details.csv'

with open(csv_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    if role_name not in roles:
        print(f"Role: {role_name} not found")
        sys.exit(2)
    else:
        global_session = boto3.Session(profile_name=role_name, region_name=main_region)
        s3 = global_session.client('s3')
        acct_name = role_name.rsplit("-", 1)[0]
        print(f"Checking S3 in account {acct_name}")
        buckets = s3.list_buckets()
        for bucket in buckets['Buckets']:
            bucket_name = bucket['Name']
            creation_date = bucket['CreationDate']
            location = s3.get_bucket_location(Bucket=bucket_name)
            bucket_region = location['LocationConstraint'] or 'us-east-1'
            if bucket_region != main_region:
                new_session = boto3.Session(profile_name=role_name, region_name=bucket_region)
                s3_session = new_session
            else:
                s3_session = global_session
            size_details = get_bucket_size_n_obj(bucket_name, s3_session)
            owner_tag = get_bucket_tag(bucket_name, "owner", s3_session)["tag_value"]
            env_tag = get_bucket_tag(bucket_name, "env", s3_session)["tag_value"]
            requestedby_tag = get_bucket_tag(bucket_name, "Requestedby", s3_session)["tag_value"]
            svc_tag = get_bucket_tag(bucket_name, "service", s3_session)["tag_value"]
            vertical = get_bucket_tag(bucket_name, "vertical", s3_session)["tag_value"]
            subvertical = get_bucket_tag(bucket_name, "subvertical", s3_session)["tag_value"]
            all_tag = get_bucket_tag(bucket_name, "owner", s3_session)["all_tags"]
            lifecycle_mgmt = get_lifecycle_details(bucket_name, s3_session)
            writer.writerow({
                'Account Name': acct_name,
                'Bucket Name': bucket_name,
                'Bucket Region': get_region_name(bucket_region, global_session),
                'Creation Date': creation_date,
                'Total Size (GB)': size_details["size"],
                'Number of Objects': size_details["obj_count"],
                'Owner': owner_tag,
                'Environment': env_tag,
                'RequestedBy': requestedby_tag,
                'Service': svc_tag,
                'Vertical': vertical,
                'Subvertical': subvertical,
                'LifeCycle Mgmt': lifecycle_mgmt,
                'All Tags': all_tag
            })
        print(f"Details of S3 buckets have been written to {csv_file}")
