import boto3
import os
from botocore.exceptions import ClientError

cw = boto3.client('cloudwatch')


def del_alarm(alarm_name):
    response = cw.delete_alarms(AlarmNames=[alarm_name])
    return response


def get_inst_tag(inst_id, tag_name):
    ec2 = boto3.client('ec2')
    response = ec2.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [inst_id]}])
    tags = response['Tags']
    for tag in tags:
        if tag['Key'] == tag_name:
            return tag['Value']
    return "NA"


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


def get_inst_ids():
    ec2 = boto3.resource('ec2')
    inst_ids = []
    instances = ec2.instances.filter()
    for instance in instances:
        inst_ids.append(instance.id)
    return inst_ids


def get_alarm_inst():
    instance_info = []
    cw = boto3.client('cloudwatch')
    inst_alarm = []
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    for alarm in alarms:
        if alarm['MetricName'] == "StatusCheckFailed" and alarm['Statistic'] == 'Minimum':
            alarm_name = alarm['AlarmName']
            for dimension in alarm['Dimensions']:
                if dimension["Name"] == "InstanceId":
                    inst_id = dimension["Value"]
                    instance_info.append({'instance-id': inst_id, 'alarm_name': alarm_name})
    return instance_info


inst_dict = get_alarm_inst()
for alarm in inst_dict:
    inst_id = alarm['instance-id']
    alarm_name = alarm['alarm_name']
    instance_name = get_inst_tag(inst_id, 'Name')
    env = "PROD"
    sns = "arn:aws:REDACTED"
    print("Deleting alarm: ", alarm_name, "\n", "For instance: ", inst_id, "\n\n")
    # print(del_alarm(alarm_name))
    print("Creating new alarm \n")
    # print(put_instance_status_check(inst_id, env, sns, instance_name))
