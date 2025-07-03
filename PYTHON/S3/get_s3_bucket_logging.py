import configparser
import os

import boto3

MAIN_REGION = "ap-south-1"
main_session = boto3.Session(profile_name=role_name, region_name=MAIN_REGION)
s3 = main_session.client('s3')
config = configparser.RawConfigParser()
home_dir = os.path.expanduser('~')
config.read(f'{home_dir}/.aws/credentials')
roles = config.sections()
csv_columns = ['Account Name', 'Bucket Name', 'Bucket Region', 'Creation Date', 'Total Size (GB)',
               'Delete Markers', 'Multipart Uploads']


def get_s3_logging_details(name, session):
    client = session.client("s3")
    response = client.get_bucket_logging(Bucket=bucket_name)
    if 'LoggingEnabled' in response:
        logging_info = response['LoggingEnabled']
        target_bucket = logging_info['TargetBucket']
        target_prefix = logging_info.get('TargetPrefix', '')
        return f"{name}, {target_bucket}, {target_prefix}"
    return "NA"


buckets = s3.list_buckets()
print(f"Bucket Name, Logging Bucket, Prefix")
for bucket in buckets["Buckets"]:
    bucket_name = bucket['Name']
    location = s3.get_bucket_location(Bucket=bucket_name)
    bucket_region = location['LocationConstraint'] or 'us-east-1'
    if bucket_region != MAIN_REGION:
        new_session = boto3.Session(profile_name=role_name, region_name=bucket_region)
        s3_session = new_session
    else:
        s3_session = main_session
    logging_details = get_s3_logging_details(bucket_name, s3_session)
    if logging_details != "NA":
        print(logging_details)
