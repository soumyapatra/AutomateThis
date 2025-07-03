import boto3
import logging
import time
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)
query_output = "s3://xxxxxxxx.ami.snap.del/athena_output"
table_names = ["cloudfront_logs_m11c_images", "cloudfront_logs_m11c_cdn", "cf_cs_my11 "]
table_dict = [{"table_name": "cloudfront_logs_m11c_images", "dist": "E2DQRMZPWI521U"},
              {"table_name": "cloudfront_logs_m11c_cdn", "dist": "E3EYB0F2MLDPSP"},
              {"table_name": "cf_cs_my11", "dist": "E3337BLW6SA1PX"}]
db = "cloudfront_logs"
bucket = "s3://xxxxxxxx-logs/structured/"


def update_cf_athena(table_name, database, cf_s3_location, year, month, day, hour):
    athena_client = boto3.client('athena')
    query_append_data = """ALTER TABLE {} ADD PARTITION (year='{}',month='{}',day='{}',hour='{}') LOCATION '{}/{}/{}/{}/{}'""".format(
        table_name, year, month, day, hour, cf_s3_location, year, month, day, hour)
    response = athena_client.start_query_execution(QueryString=query_append_data,
                                                   QueryExecutionContext={'Database': database},
                                                   ResultConfiguration={'OutputLocation': query_output})
    print(response)
    execution_id = response['QueryExecutionId']
    logger.info(f'Execution ID: {execution_id}')
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
                reason = response['QueryExecution']['Status']['StateChangeReason']
                print(f'Query failed. reason: {reason}')
                return
            elif state == 'SUCCEEDED':
                logger.info("Query Ran Successfully")
                s3_path = response['QueryExecution']['ResultConfiguration']['OutputLocation']
                filename = re.findall('.*\/(.*)', s3_path)[0]
                logger.info(f'Filename: {filename}')
                print(filename)
                return response
        time.sleep(2)


for table in table_dict:
    for i in range(0, 24):
        s3_key = bucket + table["dist"]
        update_cf_athena(table["table_name"], db, s3_key, 2020, 11, 20, f"{i:02d}")
