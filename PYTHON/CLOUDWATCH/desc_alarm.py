import json
import logging
import boto3

def getNameList(inst_id):
    cw = boto3.client('cloudwatch')
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while('NextToken' in response):
        response = cw.describe_alarms(MaxRecords=100,NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    cw_name=[]
    for metric in alarms:
        for dimension in metric['Dimensions']:
            name = dimension['Name']
            value = dimension['Value']
            if name == 'InstanceId' and value == inst_id:
                cw_name.append(metric['AlarmName'])
    return cw_name

def del_alarm(name):
    cw = boto3.client('cloudwatch')
    cw.delete_alarms(AlarmNames=[name])



alarm_names = getNameList('i-0646ac3dfde7f3b34')
print(alarm_names)
for alarm in alarm_names:    
    del_alarm(alarm)
print(f'Following Alarms has been deleted:\n{alarm_names}')
