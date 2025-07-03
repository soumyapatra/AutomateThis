import boto3
from botocore.exceptions import ClientError
from .lambda_function import REGION

ec2_client = boto3.client('ec2', region_name=REGION)


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


def del_alarm(name):
    cw = boto3.client('cloudwatch')
    cw.delete_alarms(AlarmNames=[name])


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


def enable_detailed_monitor(inst_id):
    response = ec2_client.monitor_instances(InstanceIds=[inst_id])
    return response


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
