# Code to check Cloudwatch autorevory alarm status with reboot option

import boto3
import csv
from datetime import date

recover_arn_list = ['arn:aws:REDACTED', 'arn:aws:REDACTED']
reboot_arn_list = ['arn:aws:REDACTED',
                   'arn:aws:REDACTED']

region = 'ap-southeast-1'
cw = boto3.client('cloudwatch', region_name=region)
alarms = []
response = cw.describe_alarms(MaxRecords=100)
alarms.extend(response['MetricAlarms'])
while 'NextToken' in response:
    response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
    alarms.extend(response['MetricAlarms'])

alarm_count = 0
recover_count = 0
reboot_count = 0
autorecover_alarm_count = 0

now = date.today()
file_name = f'/tmp/{now}_autorecover.csv'
with open(file_name, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    # write column headers
    writer.writerow(['NAME', 'ALARMS', 'RECOVER', 'REBOOT'])
    # loop through all the records for a given zone
    for alarm in alarms:
        alarm_count += 1
        if alarm['MetricName'] == "StatusCheckFailed_System":
            recover = False
            reboot = False
            autorecover_alarm_count += 1
            actions = alarm['AlarmActions']
            if len(actions) > 1:
                for action in actions:
                    if action in recover_arn_list:
                        recover_count += 1
                        recover = True
                    elif action in reboot_arn_list:
                        reboot_count += 1
                        reboot = True
            csv_row = [''] * 4
            csv_row[0] = alarm['AlarmName']
            csv_row[1] = actions
            csv_row[2] = recover
            csv_row[3] = reboot
            writer.writerow(csv_row)
# write to csv file with zone name

print(file_name)
print(
    f'Total alarms: {alarm_count}\nAutorecover Alarm: {autorecover_alarm_count}\nRecover count: {recover_count}\nReboot Count:{reboot_count}')

