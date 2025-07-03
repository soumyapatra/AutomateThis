import boto3
from datetime import datetime
from datetime import timedelta
from botocore.exceptions import ClientError

REGION = "ap-south-1"
SNS_ARN = "arn:aws:REDACTED"
ALERT_SNS_ARN = "arn:aws:REDACTED"
cw = boto3.client('cloudwatch', region_name=REGION)
ec2 = boto3.resource('ec2', region_name=REGION)
ec2_client = boto3.client('ec2', region_name=REGION)
ENV = "PROD"


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


def put_mem_cwagent_alarm(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_CWAGENT_MEM'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_CWAGENT_MEM'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=1,
        MetricName='mem_used_percent',
        Namespace='CWAgent',
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


def put_swap_cwagent_alarm(inst_id, env, sns_arn, name):
    if get_subenv(inst_id):
        subenv = get_subenv(inst_id)
        alarm_name = f'{subenv}_{env}_{name}_{inst_id}_CWAGENT_SWAP'
    else:
        alarm_name = f'{env}_{name}_{inst_id}_CWAGENT_SWAP'
    response = cw.put_metric_alarm(
        AlarmName=alarm_name,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[sns_arn],
        EvaluationPeriods=1,
        MetricName='swap_used_percent',
        Namespace='CWAgent',
        Period=60,
        Statistic='Average',
        Threshold=70.0,
        AlarmDescription='Alarm when server SWAP exceeds 70%',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': inst_id
            },
        ])
    return response


def get_inst_ids():
    inst_ids = []
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        inst_ids.append(instance.id)
    return inst_ids


def tag_inst(inst_id, tag_key, tag_val):
    response = ec2_client.create_tags(Resources=[inst_id], Tags=[{'Key': tag_key, 'Value': tag_val}])
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


def get_inst_state(inst_id):
    try:
        response = ec2_client.describe_instance_status(InstanceIds=[inst_id])
        instance_state = response["InstanceStatuses"][0]["InstanceState"]["Name"]
        return instance_state
    except ClientError as e:
        print("Instance not present ", e)


def del_alarm(name):
    cw = boto3.client('cloudwatch')
    cw.delete_alarms(AlarmNames=[name])


def delMemAlarm(inst_id):
    cw = boto3.client('cloudwatch')
    response = cw.describe_alarms_for_metric(MetricName='MemoryUtilization', Namespace='Linux/Memory',
                                             Dimensions=[{'Name': 'InstanceId', 'Value': inst_id}])
    if response["MetricAlarms"] == []:
        return "NA"
    else:
        alarm_name = response["MetricAlarms"][0]["AlarmName"]
        return alarm_name


def delMemCwAlarm(inst_id):
    cw = boto3.client('cloudwatch')
    response = cw.describe_alarms_for_metric(MetricName='mem_used_percent', Namespace='CWAgent',
                                             Dimensions=[{'Name': 'InstanceId', 'Value': inst_id}])
    if response["MetricAlarms"] == []:
        return "NA"
    else:
        alarm_name = response["MetricAlarms"][0]["AlarmName"]
        return alarm_name


def list_inst_4rm_metric():
    response = cw.list_metrics(Namespace="CWAgent", MetricName="mem_used_percent", RecentlyActive='PT3H')
    metrics = response["Metrics"]
    inst_list = []
    for metric in metrics:
        for item in metric["Dimensions"]:
            if item["Name"] == "InstanceId":
                inst_list.append(item["Value"])
    return inst_list


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


inst_ids = list_inst_4rm_metric()

for instance in inst_ids:
    name = get_inst_tag(instance, "Name")
    mem_alarm_name = delMemAlarm(instance)
    cw_mem_alarm_name = delMemCwAlarm(instance)
    tag_inst(instance, "cwagent", "enable")
    if cw_mem_alarm_name != "NA":
        continue
    print(f'{instance},{name}', delMemCwAlarm(instance))
    if check_bi_tag(instance):
        print(put_mem_cwagent_alarm(instance, ENV, SNS_ARN, name))
    else:
        print(put_mem_cwagent_alarm(instance, ENV, ALERT_SNS_ARN, name))
    if mem_alarm_name != "NA":
        print(f'Deleting alarm: {mem_alarm_name}', del_alarm(mem_alarm_name))
