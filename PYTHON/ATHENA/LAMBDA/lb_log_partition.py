import logging
import re
import time
from datetime import date, timedelta
import boto3
import sys
from slack_ops import slack_send
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ALB_DATABASE = os.environ['ALB_DATABASE']
ELB_DATABASE = os.environ['ELB_DATABASE']
REGION = os.environ['REGION']
ACCT_ID = os.environ['ACCT_ID']
s3_output = os.environ['s3_output']
DAYS = os.environ['DAYS']


def chk_obj(bucket, s3_key, region):
    s3 = boto3.client('s3', region_name=region)
    response = s3.list_objects(Bucket=bucket, Prefix=s3_key)
    if "Contents" not in response:
        return False
    else:
        return True


def alter_athena_alb(table_name, db, alb_s3_location, year, month, day, region, s3_out):
    athena_client = boto3.client('athena', region_name=region)
    query_create_table = """CREATE EXTERNAL TABLE IF NOT EXISTS {} (
         type string,
         time string,
         elb string,
         client_ip string,
         client_port int,
         target_ip string,
         target_port int,
         request_processing_time double,
         target_processing_time double,
         response_processing_time double,
         elb_status_code string,
         target_status_code string,
         received_bytes bigint,
         sent_bytes bigint,
         request_verb string,
         request_url string,
         request_proto string,
         user_agent string,
         ssl_cipher string,
         ssl_protocol string,
         target_group_arn string,
         trace_id string,
         domain_name string,
         chosen_cert_arn string,
         matched_rule_priority string,
         request_creation_time string,
         actions_executed string,
         redirect_url string,
         lambda_error_reason string,
         new_field string 
) 
PARTITIONED BY(year string, month string, day string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.RegexSerDe'
WITH SERDEPROPERTIES (
         'serialization.format' = '1', 'input.regex' = '([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*):([0-9]*) ([^ ]*)[:-]([0-9]*) ([-.0-9]*) ([-.0-9]*) ([-.0-9]*) (|[-0-9]*) (-|[-0-9]*) ([-0-9]*) ([-0-9]*) \\"([^ ]*) ([^ ]*) (- |[^ ]*)\\" \\"([^\\"]*)\\" ([A-Z0-9-]+) ([A-Za-z0-9.-]*) ([^ ]*) \\"([^\\"]*)\\" \\"([^\\"]*)\\" \\"([^\\"]*)\\" ([-.0-9]*) ([^ ]*) \\"([^\\"]*)\\" \\"([^\\"]*)\\"($| \\"[^ ]*\\")(.*)') 
LOCATION 's3://{}/AWSLogs/{}/elasticloadbalancing/{}/'""".format(table_name, alb_s3_location, ACCT_ID, REGION)
    response_table_creation = athena_client.start_query_execution(QueryString=query_create_table,
                                                                  QueryExecutionContext={'Database': db},
                                                                  ResultConfiguration={'OutputLocation': s3_out})

    execution_id = response_table_creation['QueryExecutionId']
    #logger.info("Execution id:", execution_id)
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
                #logger.info("Filename:", filename)
                print(filename)
        time.sleep(2)

    query_append_data = """ALTER TABLE {} ADD PARTITION (year='{}',month='{}',day='{}') LOCATION 's3://{}/AWSLogs/{}/elasticloadbalancing/{}/{}/{}/{}/'""".format(
        table_name, year, month, day, alb_s3_location, ACCT_ID, REGION, year, month, day)

    response = athena_client.start_query_execution(QueryString=query_append_data,
                                                   QueryExecutionContext={'Database': db},
                                                   ResultConfiguration={'OutputLocation': s3_out})
    return response


def alter_athena_elb(table_name, db, alb_s3_location, year, month, day, region, s3_out):
    athena_client = boto3.client('athena', region_name=region)
    query_create_table = """CREATE EXTERNAL TABLE IF NOT EXISTS {} (
 timestamp string,
 elb_name string,
 request_ip string,
 request_port int,
 backend_ip string,
 backend_port int,
 request_processing_time double,
 backend_processing_time double,
 client_response_time double,
 elb_response_code string,
 backend_response_code string,
 received_bytes bigint,
 sent_bytes bigint,
 request_verb string,
 url string,
 protocol string,
 user_agent string,
 ssl_cipher string,
 ssl_protocol string
)
PARTITIONED BY(year string, month string, day string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.RegexSerDe'
WITH SERDEPROPERTIES (
 'serialization.format' = '1',
 'input.regex' = '([^ ]*) ([^ ]*) ([^ ]*):([0-9]*) ([^ ]*)[:-]([0-9]*) ([-.0-9]*) ([-.0-9]*) ([-.0-9]*) (|[-0-9]*) (-|[-0-9]*) ([-0-9]*) ([-0-9]*) \\\"([^ ]*) ([^ ]*) (- |[^ ]*)\\\" (\"[^\"]*\") ([A-Z0-9-]+) ([A-Za-z0-9.-]*)$' )
LOCATION 's3://{}/AWSLogs/{}/elasticloadbalancing/{}/'""".format(table_name, alb_s3_location, ACCT_ID, REGION)
    response_table_creation = athena_client.start_query_execution(QueryString=query_create_table,
                                                                  QueryExecutionContext={'Database': db},
                                                                  ResultConfiguration={'OutputLocation': s3_out})

    execution_id = response_table_creation['QueryExecutionId']
    #logger.info("Execution id:", execution_id)
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
                #logger.info("Filename:", filename)
                print(filename)
        time.sleep(2)

    query_append_data = """ALTER TABLE {} ADD PARTITION (year='{}',month='{}',day='{}') LOCATION 's3://{}/AWSLogs/{}/elasticloadbalancing/{}/{}/{}/{}/'""".format(
        table_name, year, month, day, alb_s3_location, ACCT_ID, REGION, year, month, day)

    response = athena_client.start_query_execution(QueryString=query_append_data,
                                                   QueryExecutionContext={'Database': db},
                                                   ResultConfiguration={'OutputLocation': s3_out})
    return response


def get_alb(region):
    alb = boto3.client('elbv2', region_name=region)
    response = alb.describe_load_balancers()
    lbs = []
    alb_names = []
    lbs.extend(response["LoadBalancers"])
    if 'NextMarker' in response:
        response = alb.describe_load_balancers(Marker=response["NextMarker"])
        lbs.extend(response["LoadBalancers"])
    for lb in lbs:
        alb_names.append(lb["LoadBalancerArn"])
    return alb_names


def get_elb(region):
    alb = boto3.client('elb', region_name=region)
    response = alb.describe_load_balancers()
    lbs = []
    alb_names = []
    lbs.extend(response["LoadBalancerDescriptions"])
    if 'NextMarker' in response:
        response = alb.describe_load_balancers(Marker=response["NextMarker"])
        lbs.extend(response["LoadBalancers"])
    for lb in lbs:
        alb_names.append(lb["LoadBalancerName"])
    return alb_names


def get_alb_log(arn, region):
    alb = boto3.client('elbv2', region_name=region)
    response = alb.describe_load_balancer_attributes(LoadBalancerArn=arn)
    s3_bucket = ""
    s3_prefix = ""
    s3_location = []
    for keys in response['Attributes']:
        if keys['Key'] == 'access_logs.s3.enabled' and keys['Value'] == 'false':
            return "NA"
        elif keys['Key'] == 'access_logs.s3.bucket':
            s3_bucket = keys['Value']
        elif keys['Key'] == 'access_logs.s3.prefix':
            s3_prefix = keys['Value']
    s3_location.append(s3_bucket)
    s3_location.append(s3_prefix)
    return s3_location


def get_elb_log(name, region):
    alb = boto3.client('elb', region_name=region)
    response = alb.describe_load_balancer_attributes(LoadBalancerName=name)
    s3_loc_list = []
    if response['LoadBalancerAttributes']['AccessLog']['Enabled']:
        s3_bucket = response['LoadBalancerAttributes']['AccessLog']['S3BucketName']
        s3_prefix = response['LoadBalancerAttributes']['AccessLog']['S3BucketPrefix']
        s3_loc_list.append(s3_bucket)
        s3_loc_list.append(s3_prefix)
        return s3_loc_list
    return "NA"


def alb_log_part(region, db, year, month, day, s3_out):
    albs = get_alb(region)
    alb_with_log = 0
    for alb in albs:
        s3_log = get_alb_log(alb, region)
        if s3_log != "NA":
            alb_with_log += 1
            s3_bucket = s3_log[0]
            s3_prefix = s3_log[1]
            s3_access_loc = f'{s3_bucket}/{s3_prefix}'
            log_location_prefix = f'{s3_prefix}/AWSLogs/{ACCT_ID}/elasticloadbalancing/{REGION}/{year}/{month}/{day}/'
            alb_name = alb.split('/')[-2].replace('-', '_')
            table_name = f'{alb_name}_logs'
            # print(table_name, s3_access_loc, year, month, day)
            # if chk_obj(s3_bucket, log_location_prefix, region):
            #    alb_name = alb.split('/')[-2].replace('-', '_')
            #    table_name = f'{alb_name}_logs'
            #    print(table_name, s3_access_loc, year, month, day)
            print(table_name, s3_access_loc, year, month, day)
            print(alter_athena_alb(table_name, db, s3_access_loc, year, month, day, region, s3_out))
    print(f'Total ALB with Log Enabled: {alb_with_log}')


def elb_log_part(region, db, year, month, day, s3_out):
    elb_names = get_elb(REGION)
    elb_with_log = 0
    for elb_name in elb_names:
        s3_log = get_elb_log(elb_name, REGION)
        if s3_log != "NA":
            elb_with_log += 1
            s3_bucket = s3_log[0]
            s3_prefix = s3_log[1]
            s3_location = f'{s3_bucket}/{s3_prefix}'
            log_location_prefix = f'{s3_prefix}/AWSLogs/{ACCT_ID}/elasticloadbalancing/{REGION}/{year}/{month}/{day}/'
            # if chk_obj(s3_bucket, log_location_prefix, region):
            #    elb_name = elb_name.lower().replace(" ", "_").replace("-", "_")
            #    table_name = f'{elb_name}_logs'
            #    print(table_name, s3_location, year, month, day)
            # print(update_athena_alb(table_name, s3_log, year, month, day, region))
            elb_name = elb_name.lower().replace(" ", "_").replace("-", "_")
            table_name = f'{elb_name}_logs'
            print(table_name, s3_location, year, month, day)
            print(alter_athena_elb(table_name, db, s3_location, year, month, day, region, s3_out))
    print(f'Total ALB with Log Enabled: {elb_with_log}')


def lambda_handler(event, context):
    try:
        count = 0
        while count < int(DAYS):
            result_date = date.today() + timedelta(count)
            alb_log_part(REGION, ALB_DATABASE, result_date.strftime("%Y"), result_date.strftime("%m"),
                         result_date.strftime("%d"), s3_output)
            elb_log_part(REGION, ELB_DATABASE, result_date.strftime("%Y"), result_date.strftime("%m"),
                         result_date.strftime("%d"), s3_output)
            count += 1
    except:
        e = sys.exc_info()
        lambda_name = context.function_name
        sub = f'AWS Lambda '
        msg = f'Error details: {e}'
        title = f'Error in {lambda_name} in region {REGION}'
        slack_send('slack_integration_testing', msg, sub, title)
        print("Exception: ", e)
