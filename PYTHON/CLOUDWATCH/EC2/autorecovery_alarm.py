import boto3
import os

env = "RC"
sns_arn = "arn:aws:REDACTED"
recover_action = "arn:aws:REDACTED"

cw = boto3.client('cloudwatch')


def put_autorecovery_check(inst_id, env, sns_arn, actions, name):
    alarm_name = f'{env}_{name}_{inst_id}_AUTORECOVERY'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        AlarmActions=[sns_arn, actions],
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


def get_inst_name(inst_id):
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(Filters=[], InstanceIds=[inst_id])
    tags = response['Reservations'][0]['Instances'][0]['Tags']
    for tag in tags:
        if tag['Key'] == "Name":
            return tag['Value']
    else:
        return 'NA'


def get_inst_ids():
    ec2 = boto3.resource('ec2')
    inst_ids = []
    instances = ec2.instances.filter()
    for instance in instances:
        inst_ids.append(instance.id)
    return inst_ids


alarms = []


def get_alarm_inst():
    cw = boto3.client('cloudwatch')
    inst_alarm = []
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


def get_inst_state(inst_id):
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(InstanceIds=[inst_id])
    return response['Reservations'][0]['Instances'][0]['State']['Name']


# inst='i-05bfd9c10097386a8'
# name=get_inst_name(inst)
# print(put_autorecovery_check(inst,env,sns_arn,recover_action,name))

alarm_inst_ids = get_alarm_inst()
inst_ids = get_inst_ids()

for inst in inst_ids:
    if inst not in alarm_inst_ids:
        if get_inst_state(inst) == "running":
            name = get_inst_name(inst)
            print(inst, get_inst_state(inst))
            print(put_autorecovery_check(inst, env, sns_arn, recover_action, name))
