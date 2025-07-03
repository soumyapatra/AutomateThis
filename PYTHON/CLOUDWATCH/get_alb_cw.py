import boto3


def get_alarm_names(region):
    cw = boto3.client('cloudwatch', region_name = region)
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    print(f'ALARM_NAME,STATISTICS,PERIOD')
    for alarm in alarms:
        if alarm['MetricName'] == "HTTPCode_Target_5XX_Count":
            name = alarm['AlarmName']
            stats = alarm['Statistic']
            period = alarm['Period']
            print(f'{name},{stats},{period}')


get_alarm_names()