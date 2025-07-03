import boto3

REGION = "ap-south-1"
cw = boto3.client('cloudwatch', region_name=REGION)


def del_alarm(name):
    cw.delete_alarms(AlarmNames=[name])


def delCwAlarm():
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    cw_name = []
    for metric in alarms:
        if "AlarmDescription" in metric and metric['AlarmDescription'] == "EBS Volume Queue Length Anomaly Detection":
            cw_name.append(metric['AlarmName'])
    return cw_name


alarm_names = delCwAlarm()
print(alarm_names)

for alarm in alarm_names:
    del_alarm(alarm)
