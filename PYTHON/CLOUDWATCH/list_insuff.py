import boto3
from botocore.exceptions import ClientError

METRICNAME = "MemoryUtilization"
NAMESPACE = "Linux/Memory"


def get_inst_state(inst_id):
    try:
        ec2 = boto3.client('ec2')
        response = ec2.describe_instances(InstanceIds=[inst_id])
        return response['Reservations'][0]['Instances'][0]['State']['Name']
    except ClientError:
        return


def get_tag(inst_id, tag_name):
    try:
        ec2_client = boto3.resource('ec2')
        ec2_instance = ec2_client.Instance(inst_id)
        for tag in ec2_instance.tags:
            if tag["Key"] == tag_name:
                return tag["Value"]
    except ClientError:
        return "instance does not exist"


def get_met_inst(metric, namespace):
    inst_id = []
    cw = boto3.client('cloudwatch')
    response = cw.list_metrics(MetricName=metric, Namespace=namespace)
    # print(response['Metrics'][0]['Dimensions'])
    for dim in response['Metrics']:
        for inst in dim['Dimensions']:
            if inst['Name'] == 'InstanceId':
                inst_id.append(inst['Value'])
    return inst_id


def get_alarm_inst(metric, namespace):
    cw = boto3.client('cloudwatch')
    response = cw.describe_alarms()
    alarms = []
    inst_id = []
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    # print(alarms)
    for alarm in alarms:
        name = alarm['AlarmName']
        if alarm['MetricName'] == metric and alarm['Namespace'] == namespace:
            for dimension in alarm['Dimensions']:
                if dimension['Name'] == "InstanceId":
                    inst_id.append(dimension['Value'])
    return inst_id


alarm_inst = get_alarm_inst(METRICNAME, NAMESPACE)
# print(alarm_inst)
met_inst = get_met_inst(METRICNAME, NAMESPACE)
print(met_inst)

for instance in alarm_inst:
    if instance not in met_inst:
        print(instance, get_tag(instance, 'Name'), get_inst_state(instance))
