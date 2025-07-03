import boto3

REGION = 'ap-southeast-1' 

alarm_filename = "./old_alb_alarms.txt"

def get_alarm_names(region):
    cw = boto3.client('cloudwatch', region_name=region)
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    alarm_name = []
    for alarm in alarms:
        if alarm['Namespace'] == 'AWS/ELB' or alarm['Namespace'] == 'AWS/ApplicationELB':
            print(alarm)
            name = alarm['AlarmName']
            alarm_name.append(name)
    return alarm_name

old_alarms = get_alarm_names(REGION)
print(old_alarms)
f = open(alarm_filename, 'a')
for alarm in old_alarms:
    f.write(f'{alarm}\n')
f.close()
