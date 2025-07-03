import json
import logging
import re
import time
from datetime import datetime, timedelta
import os
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)
TABLE_NAME = os.environ['TABLE_NAME']
DB = os.environ['DB']
S3_BUCKET = os.environ['S3_BUCKET']
REGION = os.environ['REGION']
query_output = os.environ['QUERY_OUTPUT']


def append_athena_table(table_name, database, s3_bucket, year, month, day, hour, region):
    athena_client = boto3.client('athena', region_name=region)

    query_append_data = """ALTER TABLE {} ADD IF NOT EXISTS PARTITION (year='{}',month='{}',day='{}',hour='{}') LOCATION 's3://{}/structured_vpc_logs/{}/{}/{}/{}'""".format(
        table_name, year, month, day, hour, s3_bucket, year, month, day, hour)

    response = athena_client.start_query_execution(QueryString=query_append_data,
                                                   QueryExecutionContext={'Database': database},
                                                   ResultConfiguration={'OutputLocation': query_output})

    execution_id = response['QueryExecutionId']
    # logger.info("Execution id:", execution_id)
    print("Execution ID:", execution_id)
    state = 'RUNNING'
    max_execution = 5
    while max_execution > 0 and state == "RUNNING":
        response = athena_client.get_query_execution(QueryExecutionId=execution_id)
        if 'QueryExecution' in response and 'Status' in response['QueryExecution'] and 'State' in \
                response['QueryExecution']['Status']:
            state = response['QueryExecution']['Status']['State']
            if state == 'FAILED':
                logger.error("Query Exec Failed")
                print("Query Failed")
                reason = response['QueryExecution']['Status']['StateChangeReason']
                print(f'Query failed. reason: {reason}')
                return
            elif state == 'SUCCEEDED':
                logger.info("Query Ran Successfully")
                s3_path = response['QueryExecution']['ResultConfiguration']['OutputLocation']
                filename = re.findall('.*\/(.*)', s3_path)[0]
                # logger.info("Filename:", filename)
                print(filename)
                return response
        time.sleep(2)


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
            append_athena_table(TABLE_NAME, DB, S3_BUCKET, year, month, day, hour, REGION)
    except Exception as e:
        logging.error(e)
        print(e)
