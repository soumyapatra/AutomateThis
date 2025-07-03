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


def inst_alarm(inst_id):
    cw = boto3.client('cloudwatch')
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    cw_name = []
    for metric in alarms:
        for dimension in metric['Dimensions']:
            name = dimension['Name']
            value = dimension['Value']
            if name == 'InstanceId' and value == inst_id:
                cw_name.append(metric['AlarmName'])
    return cw_name


def getStoppedInstId(region):
    ec2 = boto3.resource('ec2', region_name=region)
    instance_ids = []
    instances = ec2.instances.filter()
    for instance in instances:
        if instance.state['Name'] == "stopped":
            instance_ids.append(instance.id)
    return instance_ids


alarms_2_b_deleted = []
for region in REGION:
    inst_ids = getStoppedInstId(region)
    if len(inst_ids) == 0:
        continue
    else:
        for inst in inst_ids:
            cw_name = inst_alarm(inst)
            print(inst, cw_name)
            for name in cw_name:
                alarms_2_b_deleted.append(name)

for item in alarms_2_b_deleted:
    # del_alarm(item)
    print(item)
