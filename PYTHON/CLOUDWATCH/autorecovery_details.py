# Code to check Cloudwatch autorevory alarm status with reboot option

import boto3

recover_arn_list = ['arn:aws:REDACTED', 'arn:aws:REDACTED']
reboot_arn_list = ['arn:aws:REDACTED', 'arn:aws:REDACTED']


region = 'ap-southeast-1'
cw = boto3.client('cloudwatch',region_name = region)
alarms = []
response = cw.describe_alarms(MaxRecords=100)
alarms.extend(response['MetricAlarms'])
while 'NextToken' in response:
    response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
    alarms.extend(response['MetricAlarms'])

for alarm in alarms:
    recover = False
    reboot = False
    if alarm['MetricName'] == "StatusCheckFailed_System":
        print(alarm['AlarmName'])
        actions = alarm['AlarmActions']
        if len(actions) > 1:
            for action in actions:
                if action in recover_arn_list:
                    recover = True
                elif action in reboot_arn_list:
                    reboot = True
        print(f'ALARM ACTIONS: {actions}\nRecover: {recover}\nReboot: {reboot}\n\n')

