import boto3

db = "flowlogs"
s3_out = "s3://xxxxxxxxxxxx/athena_output5/"
region = "ap-southeast-1"

athena_client = boto3.client('athena', region_name=region)
query_select = """SELECT * FROM "flowlogs"."inframgmt" limit 10;"""
response_table_creation = athena_client.start_query_execution(QueryString=query_select,
                                                                  QueryExecutionContext={'Database': db},
                                                                  ResultConfiguration={'OutputLocation': s3_out})
print(response_table_creation)
