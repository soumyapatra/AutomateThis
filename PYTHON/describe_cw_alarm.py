
import boto3

ec2 = boto3.client('ec2')
cw = boto3.client('cloudwatch')

paginator = cw.get_paginator('describe_alarms')
for response in paginator.paginate(StateValue='INSUFFICIENT_DATA'):
    print(response['MetricAlarms'])
