import boto3

cw = boto3.client('cloudwatch')

""" :type : pyboto3.cloudwatch """

response = cw.describe_alarms()["MetricAlarms"]

for alarm in response:
    print(alarm)
