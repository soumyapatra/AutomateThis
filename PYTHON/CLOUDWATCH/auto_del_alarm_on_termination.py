import json
import logging
import boto3
import os
import requests
from botocore.exceptions import ClientError

SNS_ARN = os.environ['SNS_ARN']
HOOK_URL = os.environ['HOOK_URL']


def slack_send(slack_channel, message, sub, title):
    channels = []
    if slack_channel != "":
        channels.append(slack_channel)
    for channel in channels:
        slack_msg = {
            "username": "ALARM",
            "mrkdwn": 'true',
            'icon_emoji': ':robot_face:',
            "channel": channel,
            "attachments": [
                {
                    "fallback": sub,
                    "author_name": "AWS",
                    "color": "#7B68EE",
                    "title": title,
                    "text": message,
                }
            ]
        }
        try:
            requests.post(HOOK_URL, data=json.dumps(slack_msg))
        except Exception as e:
            print("Failed:", e)


def pub_sns(arn, msg, sub):
    sns = boto3.client('sns')
    response = sns.publish(
        TargetArn=arn,
        Subject=sub,
        Message=msg,
    )
    return response


def getNameList(inst_id):
    cw = boto3.client('cloudwatch')
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while ('NextToken' in response):
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    cw_name = []
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
    try:
        logging.info(json.dumps(event))
        detail = json.loads(event["Records"][0]["body"])
        instance_id = detail["detail"]["instance-id"]
        alarm_names = getNameList(instance_id)
        if len(alarm_names) == 0:
            return
        else:
            for alarm in alarm_names:
                del_alarm(alarm)
            print(f'Following Alarms has been deleted:\n{alarm_names}')
        msg = f'Cloudwatch Alarm deleted for instance-id {instance_id}.\nFollowing Alarms has been deleted: {alarm_names}'
        sub = f'CloudWatch Alarm Deleted: {instance_id}'
        print(pub_sns(SNS_ARN, msg, sub))
    except ClientError as e:
        function_name = context.function_name
        excp = e.response['Error']['Code']
        print("Got Exception: ", excp)
        slack_send("lambda_alerts", f"Issue in Lambda function {function_name}\nIssue: {excp}", f"Issue in Lambda: {function_name}", "Lambda Issue")
    except Exception as e:
        function_name = context.function_name
        print("Got Exception: ", e)
        slack_send("lambda_alerts", f"Issue in Lambda function {function_name}\nIssue: {e}",
                   f"Issue in Lambda: {function_name}", "Lambda Issue")