import boto3

cw = boto3.client('cloudwatch')


def get_alarm_names():
    alarms = []
    response = cw.describe_alarms(StateValue='INSUFFICIENT_DATA', MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(StateValue='INSUFFICIENT_DATA', MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    alarm_name = []
    for alarm in alarms:
        for dimension in alarm['Dimensions']:
            if dimension['Name'] == "InstanceId":
                name = alarm['AlarmName']
                alarm_name.append(name)
    return alarm_name


alarm_name = get_alarm_names()

for alarm in alarm_name:
    print(alarm)
