import boto3
from botocore.client import ClientError

REGION = "ap-south-1"
ENV = "PROD"
SNS_ARN = "arn:aws:REDACTED"

cw = boto3.client('cloudwatch', region_name=REGION)
ec2_client = boto3.resource('ec2', region_name=REGION)


def get_tag(inst_id, tag_name):
    ec2 = boto3.client('ec2')
    response = ec2.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [inst_id]}])
    tags = response['Tags']
    for tag in tags:
        if tag['Key'] == tag_name:
            return tag['Value']
    return "NA"


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


def put_instance_status_check(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_STATUS_CHECK'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_STATUS_CHECK'
    print(alarm_name)
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


def getInstId(region):
    ec2 = boto3.resource('ec2', region_name=region)
    instance_ids = []
    instances = ec2.instances.filter()
    for instance in instances:
        instance_ids.append(instance.id)
    return instance_ids


instance_ids = getInstId(REGION)

for instance in instance_ids:
    name = get_tag(instance, "Name")
    put_instance_status_check(instance, ENV, SNS_ARN, name)
