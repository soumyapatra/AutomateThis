import boto3
import logging
import json
import os
import time
from botocore.exceptions import ClientError

cw = boto3.client('cloudwatch')
SNS_ARN = os.environ['SNS_ARN']
ENV = os.environ['ENV']
ALERT_SNS_ARN = os.environ['ALERT_SNS_ARN']
region = "ap-south-1"
recover_arn = f'arn:aws:REDACTED'


def pub_sns(arn, msg, sub):
    sns = boto3.client('sns')
    reponse = sns.publish(
        TargetArn=arn,
        Subject=sub,
        Message=msg,
    )
    return reponse


def get_tag(inst_id, tag_name):
    try:
        ec2_client = boto3.resource('ec2')
        ec2_instance = ec2_client.Instance(inst_id)
        for tag in ec2_instance.tags:
            if tag["Key"] == tag_name:
                return tag["Value"]
    except ClientError:
        return "instance does not exist"


def get_subenv(inst_id):
    tag = get_tag(inst_id, 'billing_unit')
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


def lambda_handler(event, context):
    time.sleep(30)

    print(json.dumps(event))

    region = event["detail"]["awsRegion"]
    acct_id = event["detail"]["userIdentity"]["accountId"]
    userIdentity = event["detail"]["userIdentity"]
    tags = event["detail"]["requestParameters"]["tagSpecificationSet"]["items"][0]["tags"]
    name = ""
    print(region, acct_id)

    logging.info(json.dumps(event))
    message = event["detail"]["responseElements"]["instancesSet"]["items"]

    inst_ids = []

    for i in range(0, len(message)):
        inst_ids.append(message[i]['instanceId'])
    print(inst_ids)

    if "sessionContext" in userIdentity and "sessionIssuer" in userIdentity["sessionContext"]:
        username = userIdentity["sessionContext"]["sessionIssuer"]["userName"]
    else:
        username = userIdentity["userName"]
    print(username)

    name = ""
    tags = event["detail"]["requestParameters"]["tagSpecificationSet"]["items"][0]["tags"]
    for tag in tags:
        if tag["key"] == "Name":
            if tag["value"] == "Packer Builder":
                return
            else:
                name = tag["value"]
    print(name)
    for instance in inst_ids:
        print(put_cpu_alarm(instance, ENV, ALERT_SNS_ARN, name))
        print(put_mem_alarm(instance, ENV, ALERT_SNS_ARN, name))
        # print(put_root_check(instance, ENV, ALERT_SNS_ARN, name))
        # print(put_home_check(instance, ENV, ALERT_SNS_ARN, name))
        # print(put_opt_check(instance, ENV, ALERT_SNS_ARN, name))
        print(put_autorecovery_check(instance, ENV, ALERT_SNS_ARN, name))
        try:
            print(put_autorecovery_check_recover_action(instance, ENV, ALERT_SNS_ARN, name))
        except ClientError:
            print("instance not supported. creating normal autorecover alarm")
            print(put_autorecovery_check(instance, ENV, ALERT_SNS_ARN, name))
        msg = f'Cloudwatch Alarm Created for Instance: {instance}\nFollowing Alarm Created:\n=============\n-CPU\n-MEM\n-ROOT,HOME,OPT DISK\n-AutoRecover\n=============\nRegion: {region}\nAccountId: {acct_id}\nUserName: {username}'
        print(msg)
        sub = f'CloudWatch Alarm Created: {name}({instance})'
        print(pub_sns(SNS_ARN, msg, sub))
