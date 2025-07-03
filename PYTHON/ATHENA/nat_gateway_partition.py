import logging
from datetime import date, timedelta
import boto3
import time
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)
REGION = "ap-southeast-1"
DAYS = 20
end_date = date.today() - timedelta(days=DAYS)
BUCKET = "pt-vpc-flow-logs"
KEY = "stagevpc"
TABLE_NAME = "stagevpc"
DB = "flowlogs"
s3_output = "s3://xxxxxxxxxxxxxxxxx/athena_output3/"

table_list = [{'table_name': 'stagevpc', 'key': 'stagevpc'},
              {'table_name': 'rcstage', 'key': 'rc-stage'},
              {'table_name': 'inframgmt', 'key': 'infra-mgmt'}]


def create_table(table_name, db, s3_bucket, key, region, s3_out):
    athena_client = boto3.client('athena', region_name=region)
    query_create_table = """CREATE EXTERNAL TABLE IF NOT EXISTS {} ( version int, account string, interfaceid string, sourceaddress string, destinationaddress string, sourceport int, destinationport int, protocol int, numpackets int, numbytes bigint, starttime int, endtime int, action string, logstatus string
    )
    PARTITIONED BY(year string, month string, day string, hour string)
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ' '
    LOCATION 's3://{}/structured_vpc_logs/{}/'
    TBLPROPERTIES ("skip.header.line.count"="1")""".format(table_name, s3_bucket, key)
    response_table_creation = athena_client.start_query_execution(QueryString=query_create_table,
                                                                  QueryExecutionContext={'Database': db},
                                                                  ResultConfiguration={'OutputLocation': s3_out})

    execution_id = response_table_creation['QueryExecutionId']
    logger.info("Execution id:", execution_id)
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
                print("Table Creation Failed")
                return
            elif state == 'SUCCEEDED':
                logger.info("Query Ran Successfully")
                s3_path = response['QueryExecution']['ResultConfiguration']['OutputLocation']
                filename = re.findall('.*\/(.*)', s3_path)[0]
                logger.info("Filename:", filename)
                print(filename)
        time.sleep(2)
    return


def alter_fl(table_name, db, s3_bucket, key, year, month, day, hour, region, s3_out):
    athena_client = boto3.client('athena', region_name=region)
    query_append_data = """ALTER TABLE {} ADD IF NOT EXISTS PARTITION (year='{}',month='{}',day='{}',hour='{}') 
    LOCATION 's3://{}/structured_vpc_logs/{}/{}/{}/{}/{}'""".format(
        table_name, year, month, day, hour, s3_bucket, key, year, month, day, hour)

    response = athena_client.start_query_execution(QueryString=query_append_data,
                                                   QueryExecutionContext={'Database': db},
                                                   ResultConfiguration={'OutputLocation': s3_out})
    return response


for i in table_list:
    table_name = i["table_name"]
    key = i["key"]
    create_table(table_name, DB, BUCKET, key, REGION, s3_output)

    count = 0
    while count < DAYS:
        result_date = date.today() - timedelta(count)
        year = result_date.strftime("%Y")
        month = result_date.strftime("%m")
        day = result_date.strftime("%d")
        for hour in range(0, 24):
            hr = f'{hour:02d}'
            print(year, month, day, hr)
            alter_fl(table_name, DB, BUCKET, key, year, month, day, hour, REGION, s3_output)
        count += 1

# create_db(DB, REGION, s3_output)

