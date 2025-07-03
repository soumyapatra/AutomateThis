import boto3
import json
ec2=boto3.client('ec2')
response=ec2.describe_instances(InstanceIds=['i-0d391ad09539a2bb5'])
print(response["Reservations"][0]["Instances"][0]["Tags"])

