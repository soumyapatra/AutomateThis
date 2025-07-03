import boto3
import json
import logging
REGION=["ap-south-1","ap-southeast-1"]
def del_alarm(name):
    cw = boto3.client('cloudwatch')
    cw.delete_alarms(AlarmNames=[name])

def getAlarmName(region):
    cw=boto3.client('cloudwatch',region_name=region)
    alarms=[]
    response=cw.describe_alarms(StateValue='INSUFFICIENT_DATA',MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response=cw.describe_alarms(StateValue='INSUFFICIENT_DATA',MaxRecords=100,NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    return alarms

def getInstId(region):
    ec2 = boto3.resource('ec2',region_name=region)
    instance_ids=[]
    instances=ec2.instances.filter()
    for instance in instances:
        instance_ids.append(instance.id)
    return instance_ids
alarm_name=[]
for region in REGION:
    print(region,"\n\n")
    cw_alarm=getAlarmName(region)
    instance_ids=getInstId(region)
    for alarm in cw_alarm:
        for dimension in alarm['Dimensions']:
            if dimension["Name"] == "InstanceId" and dimension["Value"] not in instance_ids:
                alarm_name.append(alarm["AlarmName"])
print(alarm_name)
cw = boto3.client('cloudwatch')

for alarm in alarm_name:
    print(f'Deleting Alarm {alarm}')
    #print(cw.delete_alarms(AlarmNames=[alarm]))
