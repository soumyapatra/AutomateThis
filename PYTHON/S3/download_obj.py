import boto3
from datetime import datetime, timezone, timedelta
import os
import time

s3 = boto3.client('s3')
BUCKET = 'xxxxxxxx.prod-app-logs'
TIME_NOW = int(time.time())
KEYS = ['applications/fusion_proxy/10.200.4.205/Feb-20/21/', 'applications/fusion_proxy/10.200.4.205/Feb-20/21',
        'applications/fusion_proxy/10.200.3.135/Feb-20/21', 'applications/fusion_proxy/10.200.3.49/Feb-20/21',
        'applications/fusion_proxy/10.200.4.214/Feb-20/21', 'applications/fusion_proxy/10.200.2.190/Feb-20/21']

date_dict = {"11": "Nov", "12": "Dec", "01": "Jan", "02": "Feb"}
KEYS = ["applications/asg/raven/"]


def create_dir(name):
    if not os.path.exists(name):
        os.makedirs(name)


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


start_date = datetime(2020, 2, 21, 17, 30)
end_date = datetime(2020, 2, 21, 18, 40)

for element in KEYS:
    list = get_obj1_v2(BUCKET, element)
    start_date = datetime(2020, 2, 21, 17, 30)
    start_date_mod = date_utc(start_date)
    end_date = datetime(2020, 2, 21, 18, 40)
    end_date_mod = date_utc(end_date)

    for item in list:
        mod_date = item['LastModified']
        if start_date_mod <= mod_date <= end_date_mod:
            key = item['Key']
            ip = key.split("/")[-3]
            path, file = os.path.split(key)
            filepath = f'{ip}/{file}'
            create_dir(ip)
            print(path, file, mod_date, filepath)

            # get_obj(BUCKET, key, filepath)
