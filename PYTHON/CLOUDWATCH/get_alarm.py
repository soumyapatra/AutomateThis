import boto3

def get_alarm_names(alb_arn):
    cw=boto3.client('cloudwatch')
    alarms=[]
    names=[]
    response=cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while ('NextToken' in response):
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    for alarm in alarms:
        for dimension in alarm['Dimensions']:
            if dimension["Name"] == "LoadBalancer" and dimension["Value"] == alb_arn: 
                names.append(alarm["AlarmName"])
    return names

print(get_alarm_names('app/pf-jenkins-alb/9d8bc7ecf46b0cd6'))
