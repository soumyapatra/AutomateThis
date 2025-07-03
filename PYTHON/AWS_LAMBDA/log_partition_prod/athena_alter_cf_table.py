import boto3
import logging
import re
import time
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
query_output = "s3://xxxxxxxx.ami.snap.del/athena_output"


def get_table(db, region):
    glue_client = boto3.client('glue', region_name=region)
    table_list = []
    table_json = []
    response = glue_client.get_tables(DatabaseName=db)
    table_json.extend(response['TableList'])
    while 'NextToken' in response:
        response = glue_client.get_tables(DatabaseName=db, NextToken=response['NextToken'])
        table_json.extend(response['TableList'])
    for i in table_json:
        table_list.append(i['Name'])
    return table_list


def get_db(region):
    glue_client = boto3.client('glue', region_name=region)
    db_json = []
    response = glue_client.get_databases()
    db_json.extend(response['DatabaseList'])
    while 'NextToken' in response:
        response = glue_client.get_databases(NextToken=response['NextToken'])
        db_json.extend(response['DatabaseList'])
    db_list = []
    for i in db_json:
        db_list.append(i['Name'])
    return db_list


def get_cf_dict(region):
    db_list = get_db(region)
    cf_partition = [{'Name': 'year', 'Type': 'string'}, {'Name': 'month', 'Type': 'string'},
                    {'Name': 'day', 'Type': 'string'}, {'Name': 'hour', 'Type': 'string'}]
    glue = boto3.client('glue')
    cf_dict = []
    for db in db_list:
        table_list = get_table(db, region)
        for table in table_list:
            response = glue.get_table(DatabaseName=db, Name=table)
            if 'PartitionKeys' in response['Table']:
                partitions = response['Table']['PartitionKeys']
                if len(partitions) == 4:
                    if partitions == cf_partition:
                        location = response['Table']['StorageDescriptor']['Location']
                        id = location.split('/')[-1]
                        cf_dict.append({'id': id, 'table': table, 'db': db, 's3_log': location})
            else:
                continue
    return cf_dict


def update_cf_athena(table_name, database, cf_s3_location, year, month, day, hour):
    athena_client = boto3.client('athena')

    query_append_data = """ALTER TABLE {} ADD IF NOT EXISTS PARTITION (year='{}',month='{}',day='{}',hour='{}') LOCATION '{}/{}/{}/{}/{}'""".format(
        table_name, year, month, day, hour, cf_s3_location, year, month, day, hour)

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
    print(json.dumps(event))
    cf_dict = get_cf_dict('ap-south-1')
    id = event['id']
    for item in cf_dict:
        if item['id'] == id:
            table_name = item['table']
            database = item['db']
            s3_location = item['s3_log']
            print('table: ', table_name, 'database: ', database, 's3_loc: ', s3_location)
            update_cf_athena(table_name, database, s3_location, event['year'], event['month'], event['day'],
                             event['hour'])
