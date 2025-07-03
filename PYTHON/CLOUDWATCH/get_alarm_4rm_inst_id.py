import json
import logging
import boto3
import os

def pub_sns(arn,msg,sub):
    sns = boto3.client('sns')
    response = sns.publish(
        TargetArn = arn,
        Subject= sub,
        Message = msg,
    )
    return response

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



def lambda_handler(event, context):
    logging.info(json.dumps(event))
    print(event['detail'])
    message=event['detail']
    instance_id=message['instance-id']
    alarm_names = getNameList(instance_id)
    print(alarm_names)
    if len(alarm_names) == 0:
        return
    else:
        for alarm in alarm_names:
            del_alarm(alarm)
        print(f'Following Alarms has been deleted:\n{alarm_names}')
    msg=f'Cloudwatch Alarm deleted for instance-id {instance_id}.\nFollowing Alarms has been deleted: {alarm_names}'
    print(msg)
    sub=f'CloudWatch Alarm Deleted: {instance_id}'
    print(pub_sns(SNS_ARN,msg,sub))

print(getNameList('i-065fe484a52ea4376'))
