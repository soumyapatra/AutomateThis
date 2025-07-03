"""
This script is used for getting S3 details of the account by using the AWS role defined
in current user aws config.
It will use all the role defined in AWS config file
USAGE:
python get_s3_details_all_roles.py
"""
import csv
import datetime
import configparser
import os
import boto3

config = configparser.RawConfigParser()
home_dir = os.path.expanduser('~')
config.read(f'{home_dir}/.aws/credentials')
roles = config.sections()
role_prod_list = [b for b in roles if "prod" in b]

MAIN_REGION = "ap-south-1"
csv_columns = ['Account Name', 'Bucket Name', 'Bucket Region', 'Creation Date', 'Total Size (GB)',
               'Number of Objects', 'Storage Cost(Standard)','Owner', 'VersioningEnabled',
               'Latest Modified Obj', "Latest Modified Obj Time",
               'Current LifeCycle Rule', 'All Tags',
               'Logging Bucket', 'Logging Bucket Prefix']

date = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
end_time = date
start_time = date - datetime.timedelta(days=1)


def get_region_name(region, session):
    """
    get AWS region name
    :param region:
    :param session:
    :return:
    """
    client = session.client("ssm")
    response = client.get_parameter(
        Name=f'/aws/service/global-infrastructure/regions/{region}/longName'
    )
    return response['Parameter']['Value']


def get_bucket_delete_markers(name, client_session):
    client = client_session.client("s3")
    response = client.list_object_versions(Bucket=name)
    delete_markers = response.get('DeleteMarkers', [])
    if delete_markers:
        return len(delete_markers)
    return "NA"


def get_s3_logging_details(name, session):
    client = session.client("s3")
    d = {"logging_bucket_name": "NA", "logging_bucket_prefix": "NA"}
    response = client.get_bucket_logging(Bucket=name)
    if 'LoggingEnabled' in response:
        logging_info = response['LoggingEnabled']
        target_bucket = logging_info['TargetBucket']
        target_prefix = logging_info.get('TargetPrefix', '')
        d["logging_bucket_name"] = target_bucket
        d["logging_bucket_prefix"] = target_prefix
        return d
    return d


def get_mulitpart_upload(name, client_session):
    s3 = client_session.client("s3")
    response = s3.list_multipart_uploads(Bucket=name)
    uploads = response.get('Uploads', [])
    if uploads:
        return len(uploads)
    return "NA"


def get_bucket_tag(name, tag_name, client_session):
    """
    Get AWS bucket Tags
    :param name:
    :param tag_name:
    :param client_session:
    :return:
    """
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


def get_latest_object(name, client_session):
    s3_client = client_session.client('s3')
    response = s3_client.list_objects_v2(Bucket=name)
    d = {"latest_modified_obj": "NA", "latest_modified_time": "NA"}

    if 'Contents' in response:
        # Get the latest object by sorting the list by LastModified field
        latest_obj = max(response['Contents'], key=lambda x: x['LastModified'])
        d["latest_modified_obj"] = latest_obj['Key']
        d["latest_modified_time"] = latest_obj['LastModified']
        return d
    return d


def get_bucket_size_n_obj(name, session):
    """
    Get AWS bucket size and object count using CLOUDWATCH
    :param name:
    :param session:
    :return:
    """
    cw_client = session.client('cloudwatch')
    d = {"size": "NA", "obj_count": "NA", "str_cost": "NA"}
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
    cost_per_gb_mumbai = 0.022
    total_size = response_size['Datapoints'][0]['Average'] if response_size['Datapoints'] else 0
    total_size_gb = total_size / (1024 * 1024 * 1024)
    total_size_gb_float = f"{total_size_gb:.10f}"
    storage_cost = total_size_gb * cost_per_gb_mumbai

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
    d["str_cost"] = storage_cost
    return d


def get_lifecycle_details(name, client_session):
    """
    Get Bucket Lifecycle details
    :param name:
    :param client_session:
    :return:
    """
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


def bucket_version_enabled(name, client_session):
    s3_client = client_session.client("s3")
    response = s3_client.get_bucket_versioning(Bucket=name)
    if "Status" in response:
        return response["Status"]
    return "Disabled"


CSV_FILE = '/tmp/all_s3_buckets_details.csv'
with open(CSV_FILE, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for role in roles:
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
            logging_details = get_s3_logging_details(bucket_name, s3_session)
            delete_markers = get_bucket_delete_markers(bucket_name, s3_session)
            mulitpart_uploads = get_mulitpart_upload(bucket_name, s3_session)
            LOGGING_BUCKET = logging_details["logging_bucket_name"]
            LOGGING_BUCKET_PREFIX = logging_details["logging_bucket_prefix"]
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
            VERSIONING_ENABLED = bucket_version_enabled(bucket_name, s3_session)
            STORAGE_COST = size_details["str_cost"]
            LATEST_OBJ = get_latest_object(bucket_name, s3_session)
            writer.writerow({'Account Name': acct_name,
                             'Bucket Name': bucket_name,
                             'Bucket Region': get_region_name(bucket_region, global_session),
                             'Creation Date': creation_date,
                             'Total Size (GB)': size_details["size"],
                             'Number of Objects': size_details["obj_count"],
                             'Storage Cost(Standard)': STORAGE_COST,
                             'Owner': OWNER_TAG,
                             'VersioningEnabled': VERSIONING_ENABLED,
                             'Latest Modified Obj': LATEST_OBJ["latest_modified_obj"],
                             "Latest Modified Obj Time": LATEST_OBJ["latest_modified_time"],
                             'Current LifeCycle Rule': LIFECYCLE_MGMT,
                             'All Tags': ALL_TAG,
                             'Logging Bucket': LOGGING_BUCKET,
                             'Logging Bucket Prefix': LOGGING_BUCKET_PREFIX})
    print(f"Details of S3 buckets have been written to {CSV_FILE}")
