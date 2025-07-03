import json
import boto3
import logging
from datetime import datetime, timedelta
from athena_ops import append_athena_table
import os

TABLE_NAME = os.environ['TABLE_NAME']
DB = os.environ['DB']
S3_BUCKET = os.environ['S3_BUCKET']


def lambda_handler(event, context):
    try:
        print(json.dumps(event))
        s3 = boto3.client('s3')
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            filename = key.split('/')[-1]
            date_string = filename.split("_")[-2]
            utc_date = datetime.strptime(date_string, "%Y%m%dT%H%MZ")
            ist_date = utc_date + timedelta(hours=5, minutes=30)
            day = ist_date.strftime("%d")
            month = ist_date.strftime("%m")
            year = ist_date.strftime("%Y")
            hour = ist_date.strftime("%H")
            dest = 'structured_vpc_logs/{}/{}/{}/{}/{}'.format(year, month, day, hour, filename)
            print("- src: s3://%s/%s" % (bucket, key))
            print("- dst: s3://%s/%s" % (bucket, dest))
            s3.copy_object(Bucket=bucket, Key=dest, CopySource=bucket + '/' + key)
            print(TABLE_NAME, DB, S3_BUCKET, year, month, day, hour)
            append_athena_table(TABLE_NAME, DB, S3_BUCKET, year, month, day, hour)
    except Exception as e:
        logging.error(e)
        print(e)
