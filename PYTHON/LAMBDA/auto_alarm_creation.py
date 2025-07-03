import boto3
import json
import time
import os

REGION = os.environ['REGION']
cw = boto3.client('cloudwatch', region_name=REGION)
SNS_ARN = os.environ['SNS_ARN']
lambda_client = boto3.client('lambda')
ENV = "STAGE"


def get_alarm_name(region, name):
    cw = boto3.client('cloudwatch', region_name=region)
    alarms = []
    alarm_name = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    for alarm in alarms:
        if alarm['Namespace'] == "AWS/Lambda":
            for dimension in alarm['Dimensions']:
                if dimension['Name'] == 'FunctionName' and dimension['Value'] == name:
                    alarm_name.append(alarm['AlarmName'])
    return alarm_name


def del_alarm(name):
    cw.delete_alarms(AlarmNames=[name])


def put_error_alarm(name, tag, region):
    alarm_name = f'{tag}:LAMBDA:{name}:{region}:Error'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        AlarmActions=[SNS_ARN],
        EvaluationPeriods=1,
        MetricName='Errors',
        Namespace='AWS/Lambda',
        Period=60,
        Statistic='Average',
        Threshold=1,
        AlarmDescription='Alarm when 4XX Error rate exceeds',
        Dimensions=[
            {
                'Name': 'FunctionName',
                'Value': name
            }
        ])
    return response


def lambda_handler(event, context):
    print(json.dumps(event))
    event_details = event['detail']
    event_name = event_details['eventName']
    if event_name == "CreateFunction20150331":
        print("Sleeping for 2 min")
        time.sleep(60)
        print("Creating Alarm")
        function_name = event_details['responseElements']['functionName']
        print(put_error_alarm(function_name, ENV, REGION))
    elif event_name == "DeleteFunction20150331":
        print("Sleeping for 2 min")
        time.sleep(60)
        print("Deleting Alarm")
        function_name = event_details['requestParameters']['functionName']
        alarm_name = get_alarm_name(REGION, function_name)
        for alarm in alarm_name:
            del_alarm(alarm)
