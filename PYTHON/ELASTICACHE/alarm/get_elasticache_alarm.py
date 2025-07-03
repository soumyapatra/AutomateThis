import boto3
cw = boto3.client('cloudwatch')


def get_elasticache_alarm_names(cluster_id):
    alarms = []
    names = []
    response = cw.describe_alarms(MaxRecords=100)
    alarms.extend(response['MetricAlarms'])
    while 'NextToken' in response:
        response = cw.describe_alarms(MaxRecords=100, NextToken=response['NextToken'])
        alarms.extend(response['MetricAlarms'])
    for alarm in alarms:
        if alarm['Namespace'] == "AWS/ElastiCache":
            for dimension in alarm['Dimensions']:
                if dimension["Name"] == "CacheClusterId":
                    alarm_name = alarm['AlarmName']
                    alarm_name_extracted = alarm_name.split(":"[-3])
                    if cluster_id == alarm_name_extracted:
                        names.append(alarm["AlarmName"])
    return names