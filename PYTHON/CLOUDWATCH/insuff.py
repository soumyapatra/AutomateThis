import boto3
import json
import logging

def del_alarm(name):
    cw = boto3.client('cloudwatch')
    cw.delete_alarms(AlarmNames=[name])

def getAlarmName():
    cw=boto3.client('cloudwatch')
    alarms=[]
    response=cw.describe_alarms(StateValue='INSUFFICIENT_DATA',MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response=cw.describe_alarms(StateValue='INSUFFICIENT_DATA',MaxRecords=100,NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    return alarms

def getInstId():
    ec2 = boto3.resource('ec2')
    instance_ids=[]
    instances=ec2.instances.filter()
    for instance in instances:
        instance_ids.append(instance.id)
    return instance_ids

cw_alarm=getAlarmName()
instance_ids=getInstId()

for alarm in cw_alarm:
    for dimension in alarm['Dimensions']:
        if dimension["Name"] == "InstanceId" and dimension["Value"] not in instance_ids:
            print(alarm['AlarmName'])
