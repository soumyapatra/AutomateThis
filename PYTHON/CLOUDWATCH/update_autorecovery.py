from botocore.exceptions import ClientError
import boto3

cw = boto3.client('cloudwatch')
env = ""
region = ""
sns_arn = ""
recover_arn_list = ['arn:aws:REDACTED', 'arn:aws:REDACTED']

cw = boto3.client('cloudwatch', region_name=region)
alarms = []
response = cw.describe_alarms(MaxRecords=100)
alarms.extend(response['MetricAlarms'])
while 'NextToken' in response:
    response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
    alarms.extend(response['MetricAlarms'])


def get_tag(inst_id, tag_name):
    try:
        ec2_client = boto3.resource('ec2')
        ec2_instance = ec2_client.Instance(inst_id)
        for tag in ec2_instance.tags:
            if tag["Key"] == tag_name:
                return tag["Value"]
    except ClientError:
        return "instance does not exist"


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
    else:
        return


def update_autorecover_alarm(inst_id, env, sns_arn, name, region):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_AUTORECOVERY'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_AUTORECOVERY'
    recover_arn = f'arn:aws:REDACTED'
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


for alarm in alarms:
    inst = ""
    name = ""
    if alarm['MetricName'] == "StatusCheckFailed_System":
        print('Working on alarm:', alarm['AlarmName'])
        actions = alarm['AlarmActions']
        if len(actions) > 1:
            for action in actions:
                if action in recover_arn_list:
                    print('Recovery already added.', '\n\n')
                    continue
        else:
            for dimension in alarm['Dimensions']:
                if dimension['Name'] == "InstanceId":
                    inst = dimension['Value']
                    name = get_inst_tag(inst, "Name")
                    s_env = get_subenv(inst)
                    print(
                        f'Got instance id: {inst} and its name: {name}\nRegion: {region} SNS_ARN: {sns_arn} SUB_ENV: {s_env}\nAdding Alarm\n')
            try:
                update_autorecover_alarm(inst, env, sns_arn, name, region)
                print("done")
            except ClientError:
                print("Instance not supported", '\n\n')
