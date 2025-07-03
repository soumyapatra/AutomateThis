import boto3

athena_client=boto3.client('athena')

s3_ouput = 's3://xxxxxxxxxxxxxxxx/athena_outputs/'
query1 = """select * from cloudfront_logs where hour='06';"""


#response = athena_client.start_query_execution(QueryString=query1,QueryExecutionContext={'Database':'cloudfront'},ResultConfiguration={'OutputLocation': s3_ouput})

#print(response)


result_response=athena_client.get_query_execution(QueryExecutionId='d13cbb75-8ab0-40b6-8aa5-20030fb4d76a')

print(result_response)
