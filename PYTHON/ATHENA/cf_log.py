import boto3
import os
import time
import logging
import re
from datetime import date
from datetime import timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)

CF_BUCKET_NAME = 'xxxxxxxxxxxxxxxxxx'
s3_output = 's3://xxxxxxxxxxxxxxxxx/athena_outputs/'
DATABASE = "cloudfront"
IDENTIFIER = 'E3QDLM1VASI4YK'
table_name = f'cf_{IDENTIFIER}'


def update_athena_cf(table_name, cf_bucket_name, year, month, day, hour):
    athena_client = boto3.client('athena')
    query_create_table = """CREATE EXTERNAL TABLE IF NOT EXISTS {} (
  `date` DATE,
  time STRING,
  location STRING,
  bytes BIGINT,
  requestip STRING,
  method STRING,
  host STRING,
  uri STRING,
  status INT,
  referrer STRING,
  useragent STRING,
  querystring STRING,
  cookie STRING,
  resulttype STRING,
  requestid STRING,
  hostheader STRING,
  requestprotocol STRING,
  requestbytes BIGINT,
  timetaken FLOAT,
  xforwardedfor STRING,
  sslprotocol STRING,
  sslcipher STRING,
  responseresulttype STRING,
  httpversion STRING,
  filestatus STRING,
  encryptedfields INT
)
PARTITIONED BY(year string, month string, day string, hour string)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\\t'
LOCATION 's3://{}/structured/{}/';""".format(table_name, cf_bucket_name, IDENTIFIER)
    response_table_creation = athena_client.start_query_execution(QueryString=query_create_table,
                                                                  QueryExecutionContext={'Database': DATABASE},
                                                                  ResultConfiguration={'OutputLocation': s3_output})
    # return response_table_creation
    execution_id = response_table_creation['QueryExecutionId']
    logger.info("Execution id:", execution_id)
    print("Execution ID:", execution_id)
    state = 'RUNNING'
    max_execution = 5
    while (max_execution > 0 and state == "RUNNING"):
        response = athena_client.get_query_execution(QueryExecutionId=execution_id)
        if 'QueryExecution' in response and 'Status' in response['QueryExecution'] and 'State' in \
                response['QueryExecution']['Status']:
            state = response['QueryExecution']['Status']['State']
            if state == 'FAILED':
                logger.error("Query Exec Failed")
                print("Table Creation Failed")
                return
            elif state == 'SUCCEEDED':
                logger.info("Query Ran Successfully")
                s3_path = response['QueryExecution']['ResultConfiguration']['OutputLocation']
                print(s3_path)
                filename = re.findall('.*\/(.*)', s3_path)[0]
                logger.info("Filename:", filename)
                # return filename
        time.sleep(2)
    query_append_data = """ALTER TABLE {} ADD PARTITION (year={},month={},day={},hour={}) LOCATION 's3://{}/structured/{}/{}/{}/{}/{}'""".format(
        table_name, year, month, day, hour, cf_bucket_name, IDENTIFIER, year, month, day, hour)

    response = athena_client.start_query_execution(QueryString=query_append_data,
                                                   QueryExecutionContext={'Database': DATABASE},
                                                   ResultConfiguration={'OutputLocation': s3_output})
    return response


update_athena_cf(table_name, CF_BUCKET_NAME, '2019', '07', '14', '04')
update_athena_cf(table_name, CF_BUCKET_NAME, '2019', '07', '14', '05')
update_athena_cf(table_name, CF_BUCKET_NAME, '2019', '07', '14', '06')
