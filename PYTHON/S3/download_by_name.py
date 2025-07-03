import boto3
from datetime import datetime, timezone
import os

s3 = boto3.client('s3')
BUCKET = 'xxxxxxxx.prod-app-logs'
KEYS = ['applications/auditservice/10.200.3.227/logs/', 'applications/auditservice/10.200.3.7/logs/',
        'applications/auditservice/10.200.5.234/logs/']


def date_utc(date):
    response = date.replace(tzinfo=timezone.utc)
    return response


def get_obj1_v2(bucket, s3_key):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=s3_key, MaxKeys=123)
    keys_list = []
    keys_list.extend(response['Contents'])
    while "NextContinuationToken" in response:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=s3_key, MaxKeys=123,
                                      ContinuationToken=response['NextContinuationToken'])
        keys_list.extend(response['Contents'])
    return keys_list


def get_obj(bucket, key, file):
    s3_resource = boto3.resource('s3')
    s3_resource.meta.client.download_file(bucket, key, file)


for element in KEYS:
    list = get_obj1_v2(BUCKET, element)

    start_date = datetime(2020, 1, 14)
    start_date_mod = date_utc(start_date)
    end_date = datetime(2020, 2, 13)
    end_date_mod = date_utc(end_date)

    for item in list:
        mod_date = item['LastModified']
        key = item['Key']
        filedate = key.split(".")[-4]
        if len(filedate) < 10:
            continue
        date_in_file = datetime.strptime(filedate, "%Y-%m-%d")
        date_in_file_utc = date_utc(date_in_file)
        if start_date_mod <= date_in_file_utc <= end_date_mod:
            ip = key.split("/")[-3]
            path, file = os.path.split(key)
            filepath = f'{ip}/{file}'
            print(path, file, mod_date, filepath)
            #get_obj(BUCKET, key, filepath)
