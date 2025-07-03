import boto3
import json

alarms=[]

def get_alarm_inst():
    cw=boto3.client('cloudwatch')
    inst_alarm=[]
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



def get_inst_metric(inst_id):
    metric=[]
    for alarm in alarms:
        for dimension in alarm['Dimensions']:
            print(dimension)
            if dimension["Name"] == 'InstanceId' and dimension['Value'] == inst_id:
                metric.append(alarm['MetricName'])
    return metric

get_alarm_inst()
print(get_inst_metric('i-014554dc2ea8d0fb0'))



