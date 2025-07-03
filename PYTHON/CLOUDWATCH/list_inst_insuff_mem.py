import boto3
import json
import logging

REGION = "ap-south-1"
METRICNAME = "MemoryUtilization"
NAMESPACE = "Linux/Memory"

cw = boto3.client('cloudwatch', region_name=REGION)
ec2 = boto3.client('ec2', region_name=REGION)


def getInstIds(region):
    cw = boto3.client('cloudwatch', region_name=region)
    alarms = []
    response = cw.describe_alarms(StateValue='INSUFFICIENT_DATA', MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    inst_ids = []
    while 'NextToken' in response:
        response = cw.describe_alarms(StateValue='INSUFFICIENT_DATA', MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    for alarm in alarms:
        if alarm["MetricName"] == METRICNAME and alarm["Namespace"] == NAMESPACE:
            for item in alarm["Dimensions"]:
                if item["Name"] == "InstanceId":
                    inst_ids.append(item["Value"])
    return inst_ids


def getInstIp(id):
    response = ec2.describe_instances(InstanceIds=[id])['Reservations'][0]['Instances'][0]["PrivateIpAddress"]
    return response


instances = getInstIds(REGION)

for instance in instances:
    print(getInstIp(instance))
