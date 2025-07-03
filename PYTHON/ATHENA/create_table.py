import boto3
import os
import time
import logging
import re
from datetime import date
from datetime import timedelta

lb_directory="s3://xxxxxxxxxxx/elb-logs/Platform-NonMTT-ext-alb-logs"
s3_output = 's3://xxxxxxxxxxxxxxxxxxxx/athena_outputs/'
DATABASE="stage_alb_log"
date_now=date.today()
no_of_days=5
count=1

logger=logging.getLogger()
logger.setLevel(logging.INFO)

def update_athena_alb(table_name,alb_s3_location,year,month,day):
    athena_client=boto3.client('athena')
    query_create_table="""CREATE EXTERNAL TABLE IF NOT EXISTS {} (
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
LOCATION '{}/AWSLogs/272110293415/elasticloadbalancing/ap-southeast-1/'""".format(table_name,alb_s3_location)
    response_table_creation = athena_client.start_query_execution(QueryString=query_create_table,
                                                                  QueryExecutionContext={'Database': DATABASE},
                                                                  ResultConfiguration={'OutputLocation': s3_output})
    #return response_table_creation
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
                #return filename
        time.sleep(2)
    query_append_data = """ALTER TABLE {} ADD PARTITION (year='{}',month='{}',day='{}') LOCATION '{}/AWSLogs/272110293415/elasticloadbalancing/ap-southeast-1/{}/{}/{}/'""".format(table_name,year,month,day,alb_s3_location,year,month,day)

    response = athena_client.start_query_execution(QueryString=query_append_data,QueryExecutionContext={'Database':DATABASE},ResultConfiguration={'OutputLocation': s3_output})
    return response

update_athena_alb('ALB_platformALB','s3://xxxxxxxx-alblogs/alb-logs','2019','07','05')
#while count < no_of_days:
#    result_date=date_now-timedelta(count)
#    count = count + 1
#    print(update_athena_alb("pt_platform_nonmtt",lb_directory,result_date.strftime('%Y'),result_date.strftime('%m'),result_date.strftime('%d')))
