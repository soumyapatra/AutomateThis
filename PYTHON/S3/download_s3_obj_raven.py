import boto3
from datetime import datetime, timezone, timedelta
import os
import time

s3 = boto3.client('s3')
BUCKET = 'xxxxxxxx.prod-app-logs'
TIME_NOW = int(time.time())
date_dict = {"11": "Nov", "12": "Dec", "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
             "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct"}
KEYS = "applications/asg/raven"

# Set date time as datetime(year, month, day, hour, minute)
start_date = datetime(2020, 2, 21, 17, 30)
end_date = datetime(2020, 2, 21, 18, 40)
delta = timedelta(hours=1)


def create_dir(name):
    if not os.path.exists(name):
        os.makedirs(name)


def date_utc(date):
    response = date.replace(tzinfo=timezone.utc)
    return response


def get_obj1_v2(bucket, s3_key):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=s3_key, MaxKeys=123)
    keys_list = []
    if "Contents" in response:
        keys_list.extend(response['Contents'])
        while "NextContinuationToken" in response:
            response = s3.list_objects_v2(Bucket=bucket, Prefix=s3_key, MaxKeys=123,
                                          ContinuationToken=response['NextContinuationToken'])
            keys_list.extend(response['Contents'])
        return keys_list
    else:
        return False


def get_obj(bucket, key, file):
    s3_resource = boto3.resource('s3')
    s3_resource.meta.client.download_file(bucket, key, file)


while start_date <= end_date:
    year = start_date.strftime("%Y")
    month = start_date.strftime("%m")
    day = start_date.strftime("%d")
    month_str = date_dict.get(month)
    year_str = year[-2:]
    month = f"{month_str}-{year_str}"
    hour = start_date.strftime("%H")
    s3_key = f'{KEYS}/{year}/{month}/{day}/{hour}'
    start_date += delta
    if get_obj1_v2(BUCKET, s3_key):
        print("Getting logs from ", s3_key)
        list = get_obj1_v2(BUCKET, s3_key)
        for item in list:
            key = item["Key"]
            path, file = os.path.split(key)
            filepath = f'Download_files_{TIME_NOW}/{file}'
            create_dir(f"Download_files_{TIME_NOW}")
            get_obj(BUCKET, key, filepath)
    else:
        print("No object found for key", s3_key)
