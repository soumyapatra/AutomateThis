import json
import boto3
import logging
from datetime import datetime, timedelta
import os

TABLE_NAME = os.environ['TABLE_NAME']
DB = os.environ['DB']
S3_BUCKET = os.environ['S3_BUCKET']
REGION = os.environ['REGION']
ec2_client = boto3.client('ec2', region_name=REGION)


def get_vpc_name(id):
    response = ec2_client.describe_vpcs(VpcIds=[id])
    vpc_tags = response['Vpcs']['Tags']
    for tag in vpc_tags:
        if tag['Key'] == "Name":
            vpc_name = tag['Value']
            vpc_name = vpc_name.lower().replace(" ", "_").replace("-", "_")
            return vpc_name
    return False


def get_vpc_log(s3_loc):
    response = ec2_client.describe_flow_logs()['FlowLogs']
    for fl in response:
        if fl['FlowLogStatus'] == "ACTIVE" and fl['DeliverLogsStatus'] == "SUCCESS" and fl[
            'LogDestinationType'] == "s3":
            log_dest = fl['LogDestination']
            if s3_loc in log_dest:
                return fl['ResourceId']
    print("No VPC found with this S3 Location")
    return False


def lambda_handler(event, context):
    try:
        print(json.dumps(event))
        s3 = boto3.client('s3')
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            s3_location = f'{bucket}/{key}'

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
    except Exception as e:
        logging.error(e)
        print(e)
