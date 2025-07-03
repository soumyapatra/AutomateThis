import boto3

REGION = ["ap-south-1"]


def del_alarm(name):
    cw = boto3.client('cloudwatch')
    cw.delete_alarms(AlarmNames=[name])


def getAlarmName(region, inst_id):
    cw = boto3.client('cloudwatch', region_name=region)
    alarms = []
    response = cw.describe_alarms(StateValue='INSUFFICIENT_DATA', MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(StateValue='INSUFFICIENT_DATA', MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    return alarms


def get_inst_ids(region):
    ec2 = boto3.resource('ec2', region_name=region)
    instance_ids = []
    instances = ec2.instances.filter()
    for instance in instances:
        instance_ids.append(instance.id)
    return instance_ids


cw_name = []
alarms_2_b_deleted = []
for region in REGION:
    inst_ids = get_inst_ids(region)
    cw = boto3.client('cloudwatch', region_name=region)
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])

    for metric in alarms:
        for dimension in metric['Dimensions']:
            name = dimension['Name']
            value = dimension['Value']
            if name == 'InstanceId' and value not in inst_ids:
                print(metric['AlarmName'])
                cw_name.append(metric['AlarmName'])
for name in cw_name:
    del_alarm(name)