import boto3

athena_client=boto3.client('athena')

s3_ouput = 's3://xxxxxxxxxxxxxx/athena_outputs/'
query1 = """select * from cloudfront_logs where hour='06';"""


query_append_data = """ALTER TABLE pt_platform_nonmtt ADD
        PARTITION (year='2019',month='08',day='12') LOCATION 's3://xxxxxxxx-logs-pt-stage/elb-logs/Platform-NonMTT-ext-alb-logs/AWSLogs/272110293415/elasticloadbalancing/ap-southeast-1/2019/08/12/'"""



#response = athena_client.start_query_execution(QueryString=query1,QueryExecutionContext={'Database':'cloudfront'},ResultConfiguration={'OutputLocation': s3_ouput})
#response = athena_client.start_query_execution(QueryString=query_append_data,QueryExecutionContext={'Database':'pt_elb_logs'},ResultConfiguration={'OutputLocation': s3_ouput})

#print(response)


result_response=athena_client.get_query_execution(QueryExecutionId='3aabc8f8-101d-473f-96ac-c5817a808c96')
print(result_response)
