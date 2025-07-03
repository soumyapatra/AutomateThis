import boto3
import logging
import re
import time
logger = logging.getLogger()
logger.setLevel(logging.INFO)

query_output = "s3://xxxxxxxxxxxxxxxxxx/athena_output"


def append_athena_table(table_name, database, s3_bucket, year, month, day, hour):
    athena_client = boto3.client('athena')

    query_append_data = """ALTER TABLE {} ADD IF NOT EXISTS PARTITION (year='{}',month='{}',day='{}',hour='{}') LOCATION '{}/{}/{}/{}/{}'""".format(
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
