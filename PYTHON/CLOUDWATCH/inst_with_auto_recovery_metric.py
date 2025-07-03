import boto3
import json

cw=boto3.client('cloudwatch')

response=cw.describe_alarms(AlarmNames=['STAGE__i-094ba45946b5e2068_AUTORECOVERY'])

print(json.dumps(response['MetricAlarms'][0]['MetricName']))

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
        if alarm['MetricName'] == "StatusCheckFailed_System":
            for dimension in alarm['Dimensions']:
                if dimension["Name"] == "InstanceId":
                    inst_alarm.append(dimension["Value"])
    return inst_alarm

print(get_alarm_inst())
