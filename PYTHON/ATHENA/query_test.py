import boto3

database = "cloudfront_logs"
query_output = "s3://xxxxxxxx.ami.snap.del/athena_output"

athena_client = boto3.client('athena')

query_append_data = """ALTER TABLE cloudfront_logs_temp ADD PARTITION (year='2019',month='11',day='08',hour='10') LOCATION 's3://xxxxxxxx-my11circle-logs/structured/E1FRK1NHP0CKPZ/2019/11/08/10'"""

response = athena_client.start_query_execution(QueryString=query_append_data,
                                                   QueryExecutionContext={'Database': database},
                                                   ResultConfiguration={'OutputLocation': query_output})

execution_id = response['QueryExecutionId']
print("Exec-id:  ",execution_id)

q_resp = athena_client.get_query_execution(QueryExecutionId=execution_id)

print(q_resp)
