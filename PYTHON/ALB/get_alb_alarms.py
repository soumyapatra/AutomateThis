"""
Script for getting current Alarm details in region
"""
import boto3


def get_alarm_names(region):
    """Get ALB Alarm Names/Details"""
    alarm_count = 0
    cw = boto3.client('cloudwatch', region_name=region)
    alarms = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    print('ALARM_NAME,METRIC_NAME,STATISTICS,PERIOD,'
          'COMPARISON_OPERATOR,THRESHOLD,EVALUATION_PERIOD')
    for alarm in alarms:
        if alarm['Namespace'] == 'AWS/ELB' or alarm['Namespace'] == 'AWS/ApplicationELB':
            name = alarm['AlarmName']
            metric_name = alarm['MetricName']
            stats = alarm['Statistic']
            period = alarm['Period']
            compare = alarm['ComparisonOperator']
            threshold = alarm['Threshold']
            evaluation_period = alarm['EvaluationPeriods']
            print(f'{name},{metric_name},{stats},{period},'
                  f'{compare},{threshold},{evaluation_period}')
    print('Alarm Count:', alarm_count)


get_alarm_names('ap-south-1')
