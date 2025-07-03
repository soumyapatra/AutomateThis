import boto3
from botocore.exceptions import ClientError
import json
import os
import time

REGION = os.environ['REGION']
ENV = os.environ['ENV']
SNS_ARN = os.environ['SNS_ARN']
ALERT_SNS_ARN = os.environ['ALERT_SNS_ARN']
ec2_client = boto3.client('ec2', region_name=REGION)
cw = boto3.client('cloudwatch', region_name=REGION)
recover_arn = f'arn:aws:REDACTED'


def enable_detailed_monitor(inst_id):
    response = ec2_client.monitor_instances(InstanceIds=[inst_id])
    return response


def delCwAlarm(inst_id):
    cw = boto3.client('cloudwatch')
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    cw_name = []
    for metric in alarms:
        for dimension in metric['Dimensions']:
            name = dimension['Name']
            value = dimension['Value']
            if name == 'InstanceId' and value == inst_id:
                cw_name.append(metric['AlarmName'])
    for alarm in cw_name:
        print(f'Deleting Alarm {alarm}: ', del_alarm(alarm))


def del_alarm(name):
    cw = boto3.client('cloudwatch')
    cw.delete_alarms(AlarmNames=[name])


def check_bi_tag(instance_id):
    bi_names = ["BI", "bi"]
    name_tag = get_inst_tag(instance_id, "Name")
    billing_tag = get_inst_tag(instance_id, "billing_unit")
    name_matched = any(ele in name_tag for ele in bi_names)
    billing_matched = any(ele in billing_tag for ele in bi_names)
    if name_matched or billing_matched:
        return True
    else:
        return False


def get_inst_tag(inst_id, tag_name):
    try:
        ec2 = boto3.client('ec2')
        response = ec2.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [inst_id]}])
        tags = response['Tags']
        for tag in tags:
            if tag['Key'] == tag_name:
                return tag['Value']
        return "NA"
    except ClientError:
        print("Instance Does not exist")
        return


def get_subenv(inst_id):
    tag = get_inst_tag(inst_id, 'billing_unit')
    if tag == "rc_production":
        return "RC"
    elif tag == "reverie_production":
        return "Reverie"
    elif tag == "bi_production":
        return "BI"
    else:
        return


def put_cpu_alarm(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_CPU'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_CPU'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=2,
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        AlarmDescription='Alarm when server CPU exceeds 70%',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': inst_id
            },
        ])
    return response


def put_mem_alarm(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_MEM'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_MEM'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=1,
        MetricName='MemoryUtilization',
        Namespace='Linux/Memory',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        AlarmDescription='Alarm when server MEMORY exceeds 70%',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': inst_id
            },
        ])
    return response


def put_root_check(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_ROOT'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_ROOT'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=1,
        MetricName='DiskUtilization',
        Namespace='Linux/Disk',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        AlarmDescription='Alarm when server ROOT exceeds 70%',
        Dimensions=[
            {
                'Name': 'MountPath',
                'Value': '/'
            },
            {
                'Name': 'InstanceId',
                'Value': inst_id
            },
            {
                'Name': 'Filesystem',
                'Value': '/dev/xvda1'
            }
        ])
    return response


def put_home_check(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_HOME'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_HOME'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=1,
        MetricName='DiskUtilization',
        Namespace='Linux/Disk',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        AlarmDescription='Alarm when server HOME exceeds 70%',
        Dimensions=[
            {
                'Name': 'MountPath',
                'Value': '/home'
            },
            {
                'Name': 'InstanceId',
                'Value': inst_id
            },
            {
                'Name': 'Filesystem',
                'Value': '/dev/xvdl'
            }
        ])
    return response


def put_opt_check(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_OPT'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_OPT'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=1,
        MetricName='DiskUtilization',
        Namespace='Linux/Disk',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        AlarmDescription='Alarm when server OPT exceeds 70%',
        Dimensions=[
            {
                'Name': 'MountPath',
                'Value': '/opt'
            },
            {
                'Name': 'InstanceId',
                'Value': inst_id
            },
            {
                'Name': 'Filesystem',
                'Value': '/dev/xvdk'
            }
        ])
    return response


def put_autorecovery_check(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_AUTORECOVERY'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_AUTORECOVERY'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=2,
        MetricName='StatusCheckFailed_System',
        Namespace='AWS/EC2',
        Period=60,
        Statistic='Minimum',
        Threshold=1.0,
        AlarmDescription='This metric auto recovers EC2 instances',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': inst_id
            }
        ])
    return response


def put_autorecovery_check_recover_action(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_AUTORECOVERY'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_AUTORECOVERY'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        AlarmActions=[sns_arn, recover_arn],
        EvaluationPeriods=2,
        MetricName='StatusCheckFailed_System',
        Namespace='AWS/EC2',
        Period=60,
        Statistic='Minimum',
        Threshold=1.0,
        AlarmDescription='This metric auto recovers EC2 instances',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': inst_id
            }
        ])
    return response


def put_instance_status_check(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_STATUS_CHECK'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_STATUS_CHECK'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=2,
        MetricName='StatusCheckFailed',
        Namespace='AWS/EC2',
        Period=60,
        Statistic='Maximum',
        Threshold=1,
        AlarmDescription='This metric auto recovers EC2 instances',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': inst_id
            }
        ])
    return response


def lambda_handler(event, context):
    print(json.dumps(event))
    detail = event['detail']
    eventname = detail['eventName']
    print(f'Event Name:', eventname)
    response = detail['responseElements']
    instance_sets = response['instancesSet']['items']
    if eventname == "StartInstances":
        for item in instance_sets:
            if item['previousState']['name'] == "stopped" and item['currentState']['name'] == "pending":
                instance_id = item['instanceId']
                print(instance_id)
                name = get_inst_tag(instance_id, "Name")
                if check_bi_tag(instance_id):
                    print(put_cpu_alarm(instance_id, ENV, SNS_ARN, name))
                    print(put_mem_alarm(instance_id, ENV, SNS_ARN, name))
                    print(put_instance_status_check(instance_id, ENV, SNS_ARN, name))
                    print(put_autorecovery_check(instance_id, ENV, SNS_ARN, name))
                    try:
                        print(put_autorecovery_check_recover_action(instance_id, ENV, SNS_ARN, name))
                    except ClientError:
                        print("instance not supported. creating normal autorecover alarm")
                        print(put_autorecovery_check(instance_id, ENV, SNS_ARN, name))
                else:
                    print(put_cpu_alarm(instance_id, ENV, ALERT_SNS_ARN, name))
                    print(put_mem_alarm(instance_id, ENV, ALERT_SNS_ARN, name))
                    print(put_instance_status_check(instance_id, ENV, ALERT_SNS_ARN, name))
                    print(put_autorecovery_check(instance_id, ENV, ALERT_SNS_ARN, name))
                    try:
                        print(put_autorecovery_check_recover_action(instance_id, ENV, ALERT_SNS_ARN, name))
                    except ClientError:
                        print("instance not supported. creating normal autorecover alarm")
                        print(put_autorecovery_check(instance_id, ENV, ALERT_SNS_ARN, name))
    elif eventname == "StopInstances":
        print(eventname)
        for item in instance_sets:
            if item['previousState']['name'] == "running" and item['currentState']['name'] == "stopping":
                instance_id = item['instanceId']
                delCwAlarm(instance_id)
    elif eventname == "TerminateInstances":
        for item in instance_sets:
            instance_id = item['instanceId']
            delCwAlarm(instance_id)
    elif eventname == "RunInstances":
        time.sleep(30)

        for item in instance_sets:
            monitor_state = item['monitoring']['state']
            instance_id = item['instanceId']
            if monitor_state == "disabled":
                print(f'Enabling Deailed Monitor for instance {instance_id}')
                enable_detailed_monitor(instance_id)
            name = get_inst_tag(instance_id, "Name")
            if check_bi_tag(instance_id):
                print(put_cpu_alarm(instance_id, ENV, SNS_ARN, name))
                print(put_mem_alarm(instance_id, ENV, SNS_ARN, name))
                print(put_instance_status_check(instance_id, ENV, SNS_ARN, name))
                print(put_autorecovery_check(instance_id, ENV, SNS_ARN, name))
                try:
                    print(put_autorecovery_check_recover_action(instance_id, ENV, SNS_ARN, name))
                except ClientError:
                    print("instance not supported. creating normal autorecover alarm")
                    print(put_autorecovery_check(instance_id, ENV, SNS_ARN, name))
            else:
                print(put_cpu_alarm(instance_id, ENV, ALERT_SNS_ARN, name))
                print(put_mem_alarm(instance_id, ENV, ALERT_SNS_ARN, name))
                print(put_instance_status_check(instance_id, ENV, ALERT_SNS_ARN, name))
                print(put_autorecovery_check(instance_id, ENV, ALERT_SNS_ARN, name))
                try:
                    print(put_autorecovery_check_recover_action(instance_id, ENV, ALERT_SNS_ARN, name))
                except ClientError:
                    print("instance not supported. creating normal autorecover alarm")
                    print(put_autorecovery_check(instance_id, ENV, ALERT_SNS_ARN, name))
