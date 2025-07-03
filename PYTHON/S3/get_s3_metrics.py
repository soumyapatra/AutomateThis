import boto3
from datetime import datetime, timedelta
import datetime

role_name = "xxxxxxxxfin-sbox-role"
region = "ap-south-1"
acct_name = role_name.rsplit("-", 1)[0]
session = boto3.Session(profile_name=role_name)
bucket_name = "ams-nbfc-qa"


s3 = session.client('s3')
cloudwatch = session.client('cloudwatch', region_name=region)
date = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

response_size = cloudwatch.get_metric_statistics(
    Namespace='AWS/S3',
    MetricName='BucketSizeBytes',
    Dimensions=[
        {'Name': 'BucketName', 'Value': bucket_name},
        {'Name': 'StorageType', 'Value': 'StandardStorage'}
    ],
    StartTime=date - datetime.timedelta(days=1),
    EndTime=date,
    Period=86400,
    Statistics=['Average']
)

print(response_size)