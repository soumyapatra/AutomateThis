import boto3
import os

def get_inst_ids():
    ec2=boto3.resource('ec2')
    inst_ids=[]
    instances=ec2.instances.filter()
    for instance in instances:
        inst_ids.append(instance.id)
    return inst_ids

def get_alarm_inst():
    cw=boto3.client('cloudwatch')
    inst_alarm=[]
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    for alarm in alarms:
        for dimension in alarm['Dimensions']:
            if dimension["Name"] == "InstanceId":
                inst_alarm.append(dimension["Value"])
    return inst_alarm

alarm_inst_ids = get_alarm_inst()
inst_ids = get_inst_ids()

for inst in inst_ids:
    if inst not in alarm_inst_ids:
        print(inst)


