import boto3
from botocore.client import ClientError

SNS_ARN = "arn:aws:REDACTED"
ENV = "PROD"
ALERT_SNS_ARN = "arn:aws:REDACTED"
REGION = "ap-south-1"
recover_arn = f'arn:aws:REDACTED'

cw = boto3.client('cloudwatch', region_name=REGION)
ec2_client = boto3.resource('ec2', region_name=REGION)


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


def pub_sns(arn, msg, sub):
    sns = boto3.client('sns')
    reponse = sns.publish(
        TargetArn=arn,
        Subject=sub,
        Message=msg,
    )
    return reponse


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


def get_inst_ids(region):
    ec2 = boto3.resource('ec2', region_name=region)
    instance_ids = []
    instances = ec2.instances.filter()
    for instance in instances:
        instance_ids.append(instance.id)
    return instance_ids


instance_ids = get_inst_ids(REGION)


def getAlarmName():
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    return alarms


ALARMS = getAlarmName()


def del_instance_alarm(instance_id):
    alarm_names = []
    for alarm in ALARMS:
        for dimension in alarm['Dimensions']:
            if dimension["Name"] == "InstanceId" and dimension["Value"] == instance_id:
                # print(cw.delete_alarms(AlarmNames=[alarm]))
                alarm_names.append(alarm["AlarmName"])
    return alarm_names


for instance in instance_ids:
    if check_bi_tag(instance):
        alarm_list = del_instance_alarm(instance)
        if len(alarm_list) > 4:
            for item in alarm_list:
                print("Deleting alarm", item)
                # print(cw.delete_alarms(AlarmNames=[item]))
