import boto3

s3_client=boto3.client('s3')

data=open("cl_event.csv","rb")

response=s3_client.put_object(Bucket='stage.xxxxxxxxxx.sonartest',Key='cl_data/cl_event.csv',Body=data)

print(response)
