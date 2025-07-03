import boto3
import logging
import re
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)
query_output = "s3://xxxxxxxx.ami.snap.del/athena_output"
cf_dict = [{'id': 'E1FRK1NHP0CKPZ', 'table': 'cloudfront_logs_temp', 's3_log': 's3://xxxxxxxx-my11circle-logs/structured/E1FRK1NHP0CKPZ'}]
years = [2019]
months = [11]
days = [8]


def update_cf_athena(table_name, database, cf_s3_location, year, month, day, hour):
    athena_client = boto3.client('athena')

    query_append_data = """ALTER TABLE {} ADD PARTITION (year='{}',month='{}',day='{}',hour='{}') LOCATION '{}/{}/{}/{}/{}'""".format(
        table_name, year, month, day, hour, cf_s3_location, year, month, day, hour)

    response = athena_client.start_query_execution(QueryString=query_append_data,
                                                   QueryExecutionContext={'Database': database},
                                                   ResultConfiguration={'OutputLocation': query_output})

    execution_id = response['QueryExecutionId']
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
                print("Query Failed")
                return
            elif state == 'SUCCEEDED':
                logger.info("Query Ran Successfully")
                s3_path = response['QueryExecution']['ResultConfiguration']['OutputLocation']
                filename = re.findall('.*\/(.*)', s3_path)[0]
                logger.info("Filename:", filename)
                print(filename)
                return response
        time.sleep(2)

def lambda_handler(event, context):
    for item in cf_dict:
        for year in years:
            for month in months:
                for day in days:
                    for i in range(0, 24):
                        cf_id = item['id']
                        table_name = item['table']
                        s3_loc = item['s3_log']
                        print('table:', table_name, 's3_location:', s3_loc, year, f'{month:02d}', 'day:', f'{day:02d}','hour:',f'{i:02d}')
                        update_cf_athena(table_name, 'cloudfront_logs', s3_loc, year, f'{month:02d}', f'{day:02d}', f'{i:02d}')
