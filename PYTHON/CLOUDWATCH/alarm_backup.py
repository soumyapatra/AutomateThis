import boto3
import json
import datetime
import logging
from datetime import date
import os
from .slack_ops import *

REGION = "ap-south-1"
BUCKET = "xxxxxxxx.ami.snap.del"
s3_client = boto3.client('s3')
SLACK_CHANNEL = os.environ['slack_channel']


def upload_s3(bucket, key, file):
    try:
        data = open(file, "rb")
        response = s3_client.put_object(Bucket=bucket, Key=key, Body=data)
    except Exception as e:
        logging.error(e)
    return response


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def get_alarms(region, namespace, metricname):
    cw = boto3.client('cloudwatch', region_name=region)
    inst_alarm = []
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    for alarm in alarms:
        if "Namespace" in alarm:
            if alarm['Namespace'] == namespace and alarm['MetricName'] == metricname:
                inst_alarm.append(alarm)
    inst_alarm_json = json.dumps(inst_alarm, default=myconverter)
    return inst_alarm_json


alarm_dict = [
    {'name': 'unhealthy_alb_alarm', 'namespace': 'AWS/ApplicationELB', 'metricname': 'UnHealthyHostCount'},
    {'name': 'unhealthy_elb_alarm', 'namespace': 'AWS/ELB', 'metricname': 'UnHealthyHostCount'},
    {'name': 'cpu_alarm', 'namespace': "AWS/EC2", 'metricname': 'CPUUtilization'},
    {'name': 'mem_alarm', 'namespace': "Linux/Memory", 'metricname': 'MemoryUtilization'},
    {'name': 'cpu_alarm', 'namespace': "AWS/EC2", 'metricname': 'CPUUtilization'},
    {'name': 'autorecovery_alarm', 'namespace': "AWS/EC2", 'metricname': 'StatusCheckFailed_System'},
    {'name': 'status_alarm', 'namespace': "AWS/EC2", 'metricname': 'StatusCheckFailed'},
    {'name': '4xx_alb_alarm', 'namespace': "AWS/ApplicationELB", 'metricname': 'HTTPCode_Target_4XX_Count'},
    {'name': '5xx_tg_alb_alarm', 'namespace': "AWS/ApplicationELB", 'metricname': 'HTTPCode_Target_5XX_Count'},
    {'name': '5xx_alb_alarm', 'namespace': "AWS/ApplicationELB", 'metricname': 'HTTPCode_ELB_5XX_Count'},
    {'name': 'target_response_alb_alarm', 'namespace': "AWS/ApplicationELB", 'metricname': 'TargetResponseTime'},
    {'name': 'unhealthy_alarm', 'namespace': 'AWS/ELB', 'metricname': 'UnHealthyHostCount'},
    {'name': '5xx_backend_elb_alarm', 'namespace': 'AWS/ELB', 'metricname': 'HTTPCode_Backend_5XX'},
    {'name': '5xx_elb_alarm', 'namespace': 'AWS/ELB', 'metricname': 'HTTPCode_ELB_5XX'},
    {'name': 'latency_elb_alarm', 'namespace': 'AWS/ELB', 'metricname': 'Latency'}
]


def lambda_handler(event, context):
    try:

        for item in alarm_dict:
            name = item['name']
            namespace = item['namespace']
            metric = item['metricname']
            json_data = get_alarms(REGION, namespace, metric)
            filename = f'/tmp/{name}.json'
            key = f'alarm_backup/{date.today()}/{name}.json'
            print(key)
            with open(filename, "w") as outfile:
                outfile.write(json_data)
                outfile.close()
            print(upload_s3(BUCKET, key, filename))
    except Exception as e:
        slack_send(SLACK_CHANNEL,f'Alarm backup lambda failed due to {e}.\nPlease check', "Alarm backup failed")

