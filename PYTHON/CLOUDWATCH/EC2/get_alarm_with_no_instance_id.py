import boto3


def get_alarm_names():
    cw = boto3.client('cloudwatch')
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    for alarm in alarms:
        for dimension in alarm['Dimensions']:
            if dimension["Name"] == "InstanceId":
                inst_id = dimension['Value']
                alarm_name = alarm['AlarmName']
                if "STATUS_CHECK" not in alarm_name:
                    alarm_name_id = alarm_name.split("_")[-2]
                    if "i-" not in alarm_name_id:
                        print(alarm_name, inst_id)
get_alarm_names()