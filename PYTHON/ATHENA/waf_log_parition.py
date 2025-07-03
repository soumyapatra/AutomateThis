import logging
import re
import time
from datetime import date, timedelta
import boto3
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DATABASE = "waf_logs"
REGION = 'ap-south-1'
ACCT_ID = '901680736066'
s3_loc = "aws-waf-logs-prod-dr/PG-WAF"
s3_output = "s3://xxxxxxxx.ami.snap.del/athena_output/"
DAYS = 1
start_date = datetime(2020, 9, 18)
end_date = datetime(2020, 9, 20)


def chk_obj(bucket, s3_key, region):
    s3 = boto3.client('s3', region_name=region)
    response = s3.list_objects(Bucket=bucket, Prefix=s3_key)
    if "Contents" not in response:
        return False
    else:
        return True


def update_athena_waf(table_name, waf_s3_location, year, month, day, hour, region):
    athena_client = boto3.client('athena', region_name=region)
    query_create_table = """CREATE EXTERNAL TABLE {}(
  `timestamp` bigint,
  `formatversion` int,
  `webaclid` string,
  `terminatingruleid` string,
  `terminatingruletype` string,
  `action` string,
  `terminatingrulematchdetails` array<
                                  struct<
                                    conditiontype:string,
                                    location:string,
                                    matcheddata:array<string>
                                        >
                                     >,
  `httpsourcename` string,
  `httpsourceid` string,
  `rulegrouplist` array<string>,
  `ratebasedrulelist` array<
                        struct<
                          ratebasedruleid:string,
                          limitkey:string,
                          maxrateallowed:int
                              >
                           >,
  `nonterminatingmatchingrules` array<
                                  struct<
                                    ruleid:string,
                                    action:string
                                        >
                                     >,
  `httprequest` struct<
                      clientip:string,
                      country:string,
                      headers:array<
                                struct<
                                  name:string,
                                  value:string
                                      >
                                   >,
                      uri:string,
                      args:string,
                      httpversion:string,
                      httpmethod:string,
                      requestid:string
                      > 
)
PARTITIONED BY(year string, month string, day string, hour string)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES (
 'paths'='action,formatVersion,httpRequest,httpSourceId,httpSourceName,nonTerminatingMatchingRules,rateBasedRuleList,ruleGroupList,terminatingRuleId,terminatingRuleMatchDetails,terminatingRuleType,timestamp,webaclId')
STORED AS INPUTFORMAT 'org.apache.hadoop.mapred.TextInputFormat'
OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION 's3://{}/'""".format(table_name, waf_s3_location)
    response_table_creation = athena_client.start_query_execution(QueryString=query_create_table,
                                                                  QueryExecutionContext={'Database': DATABASE},
                                                                  ResultConfiguration={'OutputLocation': s3_output})

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

    query_append_data = """ALTER TABLE {} ADD PARTITION (year='{}',month='{}',day='{}', hour='{}') LOCATION 's3://{
    }/{}/{}/{}/{}/'""".format(
        table_name, year, month, day, hour, waf_s3_location, year, month, day, hour)

    response = athena_client.start_query_execution(QueryString=query_append_data,
                                                   QueryExecutionContext={'Database': DATABASE},
                                                   ResultConfiguration={'OutputLocation': s3_output})
    return response


# count = 0

# while count < DAYS:
#    result_date = date.today() - timedelta(count)
#    update_table_alb(REGION, result_date.strftime("%Y"), result_date.strftime("%m"), result_date.strftime("%d"))
#   count += 1

delta = timedelta(hours=1)
while start_date <= end_date:
    print(start_date.strftime("%Y-%m-%d-%H"))
    print(update_athena_waf("pg_waf1",s3_loc,start_date.strftime("%Y"),start_date.strftime("%m"),start_date.strftime("%d"),start_date.strftime("%H"), REGION))
    start_date += delta
